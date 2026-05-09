import asyncio
import re
import subprocess
import uuid
from pathlib import Path

from app.core.config import settings


_EDGE_TTS_ENABLED = True
_SYSTEM_VOICE_NAME = "Microsoft Huihui Desktop"
_RATE_BY_EMOTION = {
    "happy": 2,
    "sad": -2,
    "angry": 1,
    "anxious": -1,
    "neutral": 0,
    "surprised": 3,
}


def _sanitize_for_tts(text: str) -> str:
    cleaned = text.strip()
    # Remove action/stage directions that read awkwardly in TTS.
    cleaned = re.sub(r"[\(\（\[\【<《].{0,20}?[\)\）\]\】>》]", "", cleaned)
    cleaned = re.sub(r"\*[^*]{0,20}\*", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip("，。；、,.!?！？ ")


async def _save_with_edge_tts(text: str, out_path: Path, emotion: str) -> None:
    import edge_tts

    rate_map = {
        "happy": "+10%",
        "sad": "-10%",
        "angry": "+6%",
        "anxious": "+4%",
        "neutral": "+0%",
        "surprised": "+12%",
    }
    communicator = edge_tts.Communicate(
        text=text,
        voice=settings.TTS_VOICE,
        rate=rate_map.get(emotion, "+0%"),
    )
    await communicator.save(str(out_path))


def _save_with_windows_tts(text: str, out_path: Path, emotion: str) -> None:
    escaped_text = text.replace("'", "''")
    escaped_voice = _SYSTEM_VOICE_NAME.replace("'", "''")
    escaped_out = str(out_path.resolve()).replace("'", "''")
    rate = _RATE_BY_EMOTION.get(emotion, 0)

    command = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$voices = $s.GetInstalledVoices() | ForEach-Object {{ $_.VoiceInfo.Name }}; "
        f"if ($voices -contains '{escaped_voice}') {{ $s.SelectVoice('{escaped_voice}') }} "
        "elseif ($voices.Count -gt 0) { $s.SelectVoice($voices[0]) }; "
        f"$s.Rate = {rate}; "
        f"$s.SetOutputToWaveFile('{escaped_out}'); "
        f"$s.Speak('{escaped_text}'); "
        "$s.Dispose()"
    )

    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(detail or f"PowerShell TTS failed with exit code {result.returncode}")


def synthesize(text: str, session_id: str, emotion: str) -> str:
    global _EDGE_TTS_ENABLED

    clean_text = _sanitize_for_tts(text)
    if not clean_text:
        return ""

    out_dir = settings.TTS_DIR / session_id
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{emotion}_{uuid.uuid4().hex[:10]}"

    if _EDGE_TTS_ENABLED:
        edge_path = out_dir / f"{stem}.mp3"
        try:
            asyncio.run(_save_with_edge_tts(clean_text, edge_path, emotion))
            if edge_path.exists() and edge_path.stat().st_size > 0:
                return str(Path("tts") / session_id / edge_path.name)
            raise RuntimeError("edge-tts output file is empty")
        except Exception as edge_exc:
            message = str(edge_exc)
            print(f"[TTS Edge Error] {message}")
            edge_path.unlink(missing_ok=True)
            if "403" in message or "Invalid response status" in message:
                _EDGE_TTS_ENABLED = False
                print("[TTS] edge-tts disabled for current process, fallback to Windows local TTS")

    local_path = out_dir / f"{stem}.wav"
    try:
        _save_with_windows_tts(clean_text, local_path, emotion)
        if local_path.exists() and local_path.stat().st_size > 0:
            return str(Path("tts") / session_id / local_path.name)
        raise RuntimeError("Windows local TTS output file is empty")
    except Exception as local_exc:
        print(f"[TTS Local Error] {local_exc}")
        local_path.unlink(missing_ok=True)
        return ""
