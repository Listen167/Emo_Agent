import numpy as np
from typing import Optional

def calculate(audio_probs: Optional[np.ndarray], text_probs: Optional[np.ndarray], w_audio: float) -> dict:
    if audio_probs is None and text_probs is None:
        return {"label": "neutral", "confidence": 0.0, "audio_weight": 0.0, "text_weight": 1.0}
    
    wa = w_audio if audio_probs is not None else 0.0
    wt = (1 - w_audio) if text_probs is not None else 0.0
    total = wa + wt
    
    audio_arr = audio_probs if audio_probs is not None else np.zeros(6)
    text_arr = text_probs if text_probs is not None else np.zeros(6)
    
    fused = (wa * audio_arr + wt * text_arr) / total if total > 0 else np.zeros(6)
    labels = ["neutral", "happy", "sad", "angry", "anxious", "surprised"]
    idx = np.argmax(fused)
    return {"label": labels[idx], "confidence": float(fused[idx]), "audio_weight": wa/total if total > 0 else 0.0, "text_weight": wt/total if total > 0 else 1.0}