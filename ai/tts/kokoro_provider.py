import uuid
from pathlib import Path
import sys
from typing import Any

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import settings
from .text import sanitize_for_tts


_PIPELINE: Any = None


def _get_device() -> str:
    if settings.KOKORO_DEVICE:
        return settings.KOKORO_DEVICE

    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def _get_pipeline():
    global _PIPELINE
    if _PIPELINE is None:
        from kokoro import KModel, KPipeline

        model_dir = settings.KOKORO_MODEL_DIR
        config_path = model_dir / "config.json"
        model_path = model_dir / "kokoro-v1_1-zh.pth"
        if not config_path.exists():
            raise FileNotFoundError(f"Kokoro config not found: {config_path}")
        if not model_path.exists():
            raise FileNotFoundError(f"Kokoro model not found: {model_path}")

        model = KModel(
            repo_id="hexgrad/Kokoro-82M-v1.1-zh",
            config=str(config_path),
            model=str(model_path),
        ).to(_get_device()).eval()
        _PIPELINE = KPipeline(
            lang_code=settings.KOKORO_LANG_CODE,
            repo_id="hexgrad/Kokoro-82M-v1.1-zh",
            model=model,
            device=_get_device(),
        )
    return _PIPELINE


def _voice_path() -> str:
    voice = settings.KOKORO_VOICE
    if voice.endswith(".pt"):
        path = Path(voice)
    else:
        path = settings.KOKORO_MODEL_DIR / "voices" / f"{voice}.pt"
    if not path.exists():
        raise FileNotFoundError(f"Kokoro voice not found: {path}")
    return str(path)


def _result_to_numpy(result) -> np.ndarray:
    audio_tensor = result.output.audio
    audio = audio_tensor.detach().cpu().numpy()
    if audio.ndim == 1:
        audio = audio.reshape(-1, 1)
    return audio


def synthesize(text: str, session_id: str, emotion: str) -> str:
    clean_text = sanitize_for_tts(text)
    if not clean_text:
        return ""

    out_dir = settings.TTS_DIR / session_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{emotion}_{uuid.uuid4().hex[:10]}.wav"

    try:
        pipeline = _get_pipeline()
        generator = pipeline(clean_text, voice=_voice_path(), speed=settings.KOKORO_SPEED)
        audio_parts = [_result_to_numpy(result) for result in generator if result.output is not None]
        if not audio_parts:
            raise RuntimeError("Kokoro produced no audio")

        audio = np.concatenate(audio_parts, axis=0)
        sf.write(out_path, audio, settings.KOKORO_SAMPLE_RATE)
        if out_path.exists() and out_path.stat().st_size > 0:
            return str(Path("tts") / session_id / out_path.name)
        raise RuntimeError("Kokoro output file is empty")
    except Exception as exc:
        print(f"[TTS Kokoro Error] {exc}")
        out_path.unlink(missing_ok=True)
        return ""
