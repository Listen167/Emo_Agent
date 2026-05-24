from pathlib import Path
from typing import Any

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "chinese-sentiment"

_TEXT_PIPE: Any = None
LABELS = ["neutral", "happy", "sad", "angry", "anxious", "surprised"]
KEYWORDS = {
    "happy": ["开心", "高兴", "快乐", "舒服", "满意", "太好了", "喜欢", "顺利", "期待", "兴奋"],
    "sad": ["难过", "伤心", "失落", "崩溃", "委屈", "想哭", "emo", "疲惫", "孤独", "绝望"],
    "angry": ["生气", "愤怒", "烦死", "离谱", "讨厌", "不公平", "火大", "气死", "无语"],
    "anxious": ["焦虑", "紧张", "担心", "害怕", "压力", "deadline", "ddl", "来不及", "怎么办", "失眠"],
    "surprised": ["惊讶", "震惊", "没想到", "居然", "突然", "意外", "啊？", "真的吗"],
}


def _load_text_model() -> Any:
    global _TEXT_PIPE
    if _TEXT_PIPE is None:
        import torch
        from transformers import pipeline

        device = 0 if torch.cuda.is_available() else -1
        _TEXT_PIPE = pipeline("text-classification", model=str(MODEL_PATH), device=device)
    return _TEXT_PIPE


def _keyword_weight(text: str, label: str) -> float:
    normalized = text.lower()
    return sum(1.0 for keyword in KEYWORDS[label] if keyword.lower() in normalized)


def _positive_distribution(text: str) -> dict[str, float]:
    if _keyword_weight(text, "surprised") > 0 or any(char in text for char in "!?！？"):
        return {"happy": 0.65, "surprised": 0.35}
    return {"happy": 0.9, "surprised": 0.1}


def _negative_distribution(text: str) -> dict[str, float]:
    weights = {
        "sad": 1.2 + _keyword_weight(text, "sad"),
        "anxious": 1.0 + _keyword_weight(text, "anxious"),
        "angry": 0.8 + _keyword_weight(text, "angry"),
    }
    total = sum(weights.values())
    return {label: value / total for label, value in weights.items()}


def _keyword_fallback(text: str) -> np.ndarray:
    vec = np.zeros(len(LABELS), dtype=np.float32)
    weights = {label: _keyword_weight(text, label) for label in KEYWORDS}
    best_label = max(weights, key=weights.get)

    if weights[best_label] <= 0:
        vec[LABELS.index("neutral")] = 1.0
        return vec

    vec[LABELS.index(best_label)] = 0.75
    vec[LABELS.index("neutral")] = 0.25
    return vec


def predict_text(text: str) -> np.ndarray:
    clean_text = text.strip()
    if not clean_text:
        vec = np.zeros(len(LABELS), dtype=np.float32)
        vec[LABELS.index("neutral")] = 1.0
        return vec

    try:
        pipe = _load_text_model()
        raw_scores = pipe(clean_text[:512], top_k=None)
        if isinstance(raw_scores, list) and raw_scores and isinstance(raw_scores[0], list):
            score_items = raw_scores[0]
        elif isinstance(raw_scores, list):
            score_items = raw_scores
        else:
            score_items = []

        sentiment_scores = {
            str(item["label"]).lower(): float(item["score"])
            for item in score_items
            if "label" in item and "score" in item
        }

        positive_score = sentiment_scores.get("positive", 0.0)
        neutral_score = sentiment_scores.get("neutral", 0.0)
        negative_score = sentiment_scores.get("negative", 0.0)

        vec = np.zeros(len(LABELS), dtype=np.float32)
        vec[LABELS.index("neutral")] = neutral_score
        for label, ratio in _positive_distribution(clean_text).items():
            vec[LABELS.index(label)] += positive_score * ratio
        for label, ratio in _negative_distribution(clean_text).items():
            vec[LABELS.index(label)] += negative_score * ratio

        total = float(vec.sum())
        if total > 0:
            return vec / total
    except Exception as exc:
        print(f"[Emotion Error] text model unavailable, fallback to keywords: {exc}")

    return _keyword_fallback(clean_text)
