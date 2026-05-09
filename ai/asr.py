import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

sys.path.append(str(Path(__file__).parent.parent / "backend"))


_PROJECT_ROOT = Path(__file__).parent.parent
_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
_MODEL_PATH = _PROJECT_ROOT / "models" / "SensevoiceSmall"
_WHISPER_PATH = _PROJECT_ROOT / "models" / "whisper-base"
_MODEL = None
_WHISPER_PIPE: Any = None

_EMOTION_TAG_MAP = {
    "HAPPY": "happy",
    "SAD": "sad",
    "ANGRY": "angry",
    "NEUTRAL": "neutral",
    "SURPRISED": "surprised",
    "AFRAID": "anxious",
    "DISGUSTED": "angry",
}
_LABELS = ["neutral", "happy", "sad", "angry", "anxious", "surprised"]


def _load_model():
    global _MODEL
    if _MODEL is None:
        from funasr import AutoModel

        _MODEL = AutoModel(
            model=str(_MODEL_PATH),
            device=_DEVICE,
            disable_update=True,
        )
    return _MODEL


def _load_whisper():
    global _WHISPER_PIPE
    if _WHISPER_PIPE is None:
        from transformers import pipeline

        device = 0 if torch.cuda.is_available() else -1
        _WHISPER_PIPE = pipeline(
            task="automatic-speech-recognition",
            model=str(_WHISPER_PATH),
            tokenizer=str(_WHISPER_PATH),
            feature_extractor=str(_WHISPER_PATH),
            device=device,
        )
    return _WHISPER_PIPE


def _parse_emotion(raw_text: str) -> np.ndarray:
    vec = np.zeros(len(_LABELS), dtype=np.float32)
    for tag, label in _EMOTION_TAG_MAP.items():
        if re.search(rf"<\|{tag}\|>", raw_text):
            vec[_LABELS.index(label)] = 0.9
            if label != "neutral":
                vec[_LABELS.index("neutral")] = 0.1
            return vec

    vec[_LABELS.index("neutral")] = 1.0
    return vec


def _load_audio(audio_path: str) -> tuple[np.ndarray, int]:
    import soundfile as sf

    waveform, sample_rate = sf.read(audio_path, dtype="float32", always_2d=False)
    if waveform.ndim > 1:
        waveform = waveform.mean(axis=1)
    return waveform.astype(np.float32), int(sample_rate)


def _transcribe_with_whisper(audio_path: str) -> str:
    pipe = _load_whisper()
    waveform, sample_rate = _load_audio(audio_path)
    result = pipe(
        {"array": waveform, "sampling_rate": sample_rate},
        generate_kwargs={"task": "transcribe"},
    )
    return str(result.get("text", "")).strip()


def transcribe(audio_path: str) -> tuple[str, np.ndarray | None]:
    from funasr.utils.postprocess_utils import rich_transcription_postprocess

    try:
        model = _load_model()
        result = model.generate(
            input=str(audio_path),
            language="auto",
            use_itn=True,
            batch_size_s=60,
            merge_vad=True,
            merge_length_s=15,
        )

        if not result:
            return "", None

        raw_text = str(result[0].get("text", ""))
        emotion_vec = _parse_emotion(raw_text)
        text = rich_transcription_postprocess(raw_text).strip()
        print(f"[SenseVoice] Result: {text}")
        return text, emotion_vec
    except Exception as exc:
        print(f"[ASR Error] SenseVoice failed, fallback to Whisper: {exc}")

    try:
        text = _transcribe_with_whisper(audio_path)
        print(f"[Whisper Fallback] Result: {text}")
        return text, None
    except Exception as exc:
        print(f"[ASR Fallback Error] {exc}")
        return "", None
