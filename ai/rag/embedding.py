from pathlib import Path
from typing import Any

import numpy as np


_MODEL: Any = None


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _model_path() -> Path:
    fallback = _project_root() / "models" / "bge-small-zh-v1.5"
    try:
        from app.core.config import settings

        configured = settings.RAG_EMBEDDING_MODEL_DIR
    except Exception:
        return fallback

    if configured.exists():
        return configured

    # Docker deployments often use /app/models/..., but local Windows runs from the repo root.
    # Keep the Docker config valid while making local tests work without editing every .env value.
    normalized = configured.as_posix().lstrip("/")
    if normalized.startswith("app/"):
        local_from_docker_path = _project_root() / normalized.removeprefix("app/")
        if local_from_docker_path.exists():
            return local_from_docker_path

    if fallback.exists():
        return fallback

    return configured


def get_embedding_model():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer

        _MODEL = SentenceTransformer(str(_model_path()))
    return _MODEL


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = get_embedding_model()
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return vectors.astype(np.float32).tolist()


def embed_text(text: str) -> list[float]:
    vectors = embed_texts([text])
    return vectors[0] if vectors else []


def cosine_similarity(query: np.ndarray, candidate: np.ndarray) -> float:
    if query.size == 0 or candidate.size == 0:
        return 0.0
    return float(np.dot(query, candidate))
