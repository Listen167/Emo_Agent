import torch
import numpy as np
from transformers import pipeline

_DEVICE = 0 if torch.cuda.is_available() else -1
_audio_pipe = None
_text_pipe = None

def _load_audio():
    global _audio_pipe
    if _audio_pipe is None:
        _audio_pipe = pipeline("audio-classification", model="emotion2vec/emotion2vec-base", device=_DEVICE)
    return _audio_pipe

def _load_text():
    global _text_pipe
    if _text_pipe is None:
        _text_pipe = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest", device=_DEVICE)
    return _text_pipe

def predict_audio(path: str) -> np.ndarray:
    labels = ["neutral", "happy", "sad", "angry", "anxious", "surprised"]
    res = _load_audio()(path, top_k=6)
    prob_map = {r["label"]: r["score"] for r in res}
    return np.array([prob_map.get(l, 0.0) for l in labels])

def predict_text(text: str) -> np.ndarray:
    res = _load_text()(text[:512])[0]
    label_map = {"LABEL_0": "sad", "LABEL_1": "neutral", "LABEL_2": "happy"}
    mapped = label_map.get(res["label"], "neutral")
    vec = np.zeros(6)
    idx = ["neutral", "happy", "sad", "angry", "anxious", "surprised"].index(mapped)
    vec[idx] = res["score"]
    return vec