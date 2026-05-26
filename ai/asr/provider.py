import re
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import settings


SENSEVOICE_PATH = ROOT / "models" / "SensevoiceSmall"
WHISPER_PATH = ROOT / "models" / "whisper-base"

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
_TRADITIONAL_TO_SIMPLIFIED = str.maketrans(
    {
        "臺": "台",
        "灣": "湾",
        "學": "学",
        "習": "习",
        "體": "体",
        "會": "会",
        "個": "个",
        "們": "们",
        "這": "这",
        "覺": "觉",
        "得": "得",
        "麼": "么",
        "裡": "里",
        "裏": "里",
        "對": "对",
        "說": "说",
        "聽": "听",
        "語": "语",
        "氣": "气",
        "還": "还",
        "沒": "没",
        "發": "发",
        "現": "现",
        "讓": "让",
        "給": "给",
        "壓": "压",
        "醫": "医",
        "診": "诊",
        "處": "处",
        "員": "员",
        "長": "长",
        "總": "总",
        "經": "经",
        "歷": "历",
        "記": "记",
        "錄": "录",
        "關": "关",
        "開": "开",
        "過": "过",
        "時": "时",
        "間": "间",
        "點": "点",
        "題": "题",
        "難": "难",
        "應": "应",
        "該": "该",
        "幫": "帮",
        "師": "师",
        "級": "级",
        "獎": "奖",
        "賽": "赛",
        "認": "认",
        "為": "为",
        "與": "与",
        "專": "专",
        "業": "业",
    }
)


def _torch_device() -> str:
    if settings.ASR_DEVICE:
        return settings.ASR_DEVICE

    import torch

    return "cuda" if torch.cuda.is_available() else "cpu"


def _transformer_device() -> int:
    if settings.ASR_DEVICE and settings.ASR_DEVICE.lower() == "cpu":
        return -1
    if settings.ASR_DEVICE and settings.ASR_DEVICE.lower().startswith("cuda"):
        return 0

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


def _normalize_text(text: str) -> str:
    cleaned = re.sub(r"<\|.*?\|>", "", text).strip()
    if not settings.ASR_FORCE_SIMPLIFIED:
        return cleaned

    try:
        from opencc import OpenCC

        return OpenCC("t2s").convert(cleaned)
    except Exception:
        return cleaned.translate(_TRADITIONAL_TO_SIMPLIFIED)


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
        generate_kwargs={"task": "transcribe", "language": "zh"},
    )
    return _normalize_text(str(result.get("text", "")))


def transcribe(audio_path: str) -> tuple[str, np.ndarray | None]:
    try:
        from funasr.utils.postprocess_utils import rich_transcription_postprocess

        model = _load_sensevoice()
        result = model.generate(
            input=str(audio_path),
            language=settings.ASR_LANGUAGE,
            use_itn=True,
            batch_size_s=60,
            merge_vad=True,
            merge_length_s=15,
        )
        if not result:
            return "", None

        raw_text = str(result[0].get("text", ""))
        text = _normalize_text(rich_transcription_postprocess(raw_text))
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
