import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
from transformers import pipeline

sys.path.append(str(Path(__file__).parent.parent / "backend"))


_PROJECT_ROOT = Path(__file__).parent.parent
_DEVICE = 0 if torch.cuda.is_available() else -1
_MODEL_PATH = _PROJECT_ROOT / "models"
_TEXT_PIPE: Any = None
_LABELS = ["neutral", "happy", "sad", "angry", "anxious", "surprised"]
_KEYWORDS = {
    "happy": ["开心", "高兴", "快乐", "兴奋", "喜欢", "太棒了", "牛", "爽", "满意"],
    "sad": ["难过", "伤心", "失落", "低落", "委屈", "想哭", "沮丧", "emo", "崩溃"],
    "angry": ["生气", "火大", "气死", "烦死", "无语", "离谱", "讨厌", "破防", "恼火"],
    "anxious": ["焦虑", "紧张", "担心", "害怕", "慌", "怎么办", "来不及", "deadline", "ddl"],
    "surprised": ["震惊", "惊了", "居然", "竟然", "哇", "天哪", "真的假的", "没想到"],
}


def _load_text() -> Any:
    global _TEXT_PIPE
    if _TEXT_PIPE is None:
        model_path = _MODEL_PATH / "chinese-sentiment"
        _TEXT_PIPE = pipeline("text-classification", model=str(model_path), device=_DEVICE)
    return _TEXT_PIPE


def _keyword_weight(text: str, label: str) -> float:
    normalized = text.lower()
    weight = 0.0
    for keyword in _KEYWORDS[label]:
        if keyword.lower() in normalized:
            weight += 1.0
    return weight


def _positive_distribution(text: str) -> dict[str, float]:
    surprise_weight = _keyword_weight(text, "surprised")
    if surprise_weight > 0 or any(char in text for char in "！？!?"):
        return {"happy": 0.6, "surprised": 0.4}
    return {"happy": 0.85, "surprised": 0.15}


def _negative_distribution(text: str) -> dict[str, float]:
    weights = {
        "sad": 1.2 + _keyword_weight(text, "sad"),
        "anxious": 1.0 + _keyword_weight(text, "anxious"),
        "angry": 0.8 + _keyword_weight(text, "angry"),
    }
    total = sum(weights.values())
    return {label: value / total for label, value in weights.items()}


def predict_text(text: str) -> np.ndarray:
    try:
        pipe = _load_text()
        raw_scores = pipe(text[:512], top_k=None)

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

        vec = np.zeros(len(_LABELS), dtype=np.float32)
        vec[_LABELS.index("neutral")] = neutral_score

        for label, ratio in _positive_distribution(text).items():
            vec[_LABELS.index(label)] += positive_score * ratio

        for label, ratio in _negative_distribution(text).items():
            vec[_LABELS.index(label)] += negative_score * ratio

        total = float(vec.sum())
        if total > 0:
            vec /= total
        else:
            vec[_LABELS.index("neutral")] = 1.0

        return vec
    except Exception as exc:
        print(f"[Emotion Error] {exc}")
        vec = np.zeros(len(_LABELS), dtype=np.float32)
        vec[_LABELS.index("neutral")] = 1.0
        return vec
