from typing import Optional

import numpy as np


LABELS = ["neutral", "happy", "sad", "angry", "anxious", "surprised"]


def _normalize(arr: np.ndarray) -> np.ndarray:
    total = float(arr.sum())
    if total > 0:
        return arr / total
    return arr


def calculate(audio_probs: Optional[np.ndarray], text_probs: Optional[np.ndarray], w_audio: float) -> dict:
    if audio_probs is None and text_probs is None:
        return {"label": "neutral", "confidence": 0.0, "audio_weight": 0.0, "text_weight": 1.0}

    wa = w_audio if audio_probs is not None else 0.0
    wt = (1 - w_audio) if text_probs is not None else 0.0
    total = wa + wt

    audio_arr = _normalize(audio_probs.astype(np.float32)) if audio_probs is not None else np.zeros(len(LABELS), dtype=np.float32)
    text_arr = _normalize(text_probs.astype(np.float32)) if text_probs is not None else np.zeros(len(LABELS), dtype=np.float32)
    fused = (wa * audio_arr + wt * text_arr) / total if total > 0 else np.zeros(len(LABELS), dtype=np.float32)

    idx = int(np.argmax(fused))
    return {
        "label": LABELS[idx],
        "confidence": float(fused[idx]),
        "audio_weight": wa / total if total > 0 else 0.0,
        "text_weight": wt / total if total > 0 else 1.0,
    }
