import re
from pathlib import Path
from typing import Any

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SENSEVOICE_PATH = PROJECT_ROOT / "models" / "SensevoiceSmall"
WHISPER_PATH = PROJECT_ROOT / "models" / "whisper-base"

_MODEL: Any = None
_WHISPER_PIPE: Any = None
_LABELS = ["neutral", "happy", "sad", "angry", "anxious", "surprised"]
_EMOTION_TAG_MAP = {
    "HAPPY": "happy",
    "SAD": "sad",
    "ANGRY": "angry",
    "NEUTRAL": "neutral",
    "SURPRISED": "surprised",
    "AFRAID": "anxious",
    "DISGUSTED": "angry",
}


def _torch_device() -> str:
    import torch

    return "cuda" if torch.cuda.is_available() else "cpu"


def _transformer_device() -> int:
    import torch

    return 0 if torch.cuda.is_available() else -1


def _load_sensevoice():
    global _MODEL
    if _MODEL is None:
        from funasr import AutoModel

        _MODEL = AutoModel(
            model=str(SENSEVOICE_PATH),
            device=_torch_device(),
            disable_update=True,
        )
    return _MODEL


def _load_whisper():
    global _WHISPER_PIPE
    if _WHISPER_PIPE is None:
        from transformers import pipeline

        _WHISPER_PIPE = pipeline(
            task="automatic-speech-recognition",
            model=str(WHISPER_PATH),
            tokenizer=str(WHISPER_PATH),
            feature_extractor=str(WHISPER_PATH),
            device=_transformer_device(),
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
    try:
        from funasr.utils.postprocess_utils import rich_transcription_postprocess

        model = _load_sensevoice()
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
        text = rich_transcription_postprocess(raw_text).strip()
        print(f"[SenseVoice] Result: {text}")
        return text, _parse_emotion(raw_text)
    except Exception as exc:
        print(f"[ASR Error] SenseVoice failed, fallback to Whisper: {exc}")

    try:
        text = _transcribe_with_whisper(audio_path)
        print(f"[Whisper Fallback] Result: {text}")
        return text, None
    except Exception as exc:
        print(f"[ASR Fallback Error] {exc}")
        return "", None
