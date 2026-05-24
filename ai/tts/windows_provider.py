import subprocess
import uuid
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import settings
from .text import sanitize_for_tts


_SYSTEM_VOICE_NAME = "Microsoft Huihui Desktop"
_WINDOWS_RATE_BY_EMOTION = {
    "happy": 2,
    "sad": -2,
    "angry": 1,
    "anxious": -1,
    "neutral": 0,
    "surprised": 3,
}


def _save_with_windows_tts(text: str, out_path: Path, emotion: str) -> None:
    escaped_text = text.replace("'", "''")
    escaped_voice = _SYSTEM_VOICE_NAME.replace("'", "''")
    escaped_out = str(out_path.resolve()).replace("'", "''")
    rate = _WINDOWS_RATE_BY_EMOTION.get(emotion, 0)

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
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(detail or f"PowerShell TTS failed with exit code {result.returncode}")


def synthesize(text: str, session_id: str, emotion: str) -> str:
    clean_text = sanitize_for_tts(text)
    if not clean_text:
        return ""

    out_dir = settings.TTS_DIR / session_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{emotion}_{uuid.uuid4().hex[:10]}.wav"

    try:
        _save_with_windows_tts(clean_text, out_path, emotion)
        if out_path.exists() and out_path.stat().st_size > 0:
            return str(Path("tts") / session_id / out_path.name)
        raise RuntimeError("Windows local TTS output file is empty")
    except Exception as exc:
        print(f"[TTS Local Error] {exc}")
        out_path.unlink(missing_ok=True)
        return ""
