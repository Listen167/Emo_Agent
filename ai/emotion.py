import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

import torch
import numpy as np
from transformers import pipeline

_DEVICE = 0 if torch.cuda.is_available() else -1
_MODEL_PATH = Path("D:/PragramFile/VScode/Emo_Agent/models")
_TEXT_PIPE = None

def _load_text():
    global _TEXT_PIPE
    if _TEXT_PIPE is None:
        model_path = _MODEL_PATH / "chinese-sentiment"
        _TEXT_PIPE = pipeline("text-classification", model=str(model_path), device=_DEVICE)
    return _TEXT_PIPE

def predict_audio(path: str) -> np.ndarray:
    labels = ["neutral", "happy", "sad", "angry", "anxious", "surprised"]
    return np.array([0.2, 0.3, 0.1, 0.1, 0.1, 0.2])

def predict_text(text: str) -> np.ndarray:
    labels = ["neutral", "happy", "sad", "angry", "anxious", "surprised"]
    try:
        pipe = _load_text()
        res = pipe(text[:512])[0]
        label_map = {"positive": "happy", "negative": "sad", "neutral": "neutral"}
        mapped = label_map.get(res["label"], "neutral")
        vec = np.zeros(6)
        vec[labels.index(mapped)] = res["score"]
        return vec
    except:
        vec = np.zeros(6)
        vec[0] = 0.6
        return vec