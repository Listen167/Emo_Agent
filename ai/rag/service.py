import asyncio
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from ai.rag.embedding import embed_text
from app.core.config import settings
from app.core.database import async_session
from app.models.message import KnowledgeChunk, KnowledgeDocument


@dataclass
class RetrievedChunk:
    title: str
    content: str
    source: str | None = None
    score: float | None = None
    keyword_score: float = 0.0
    vector_score: float = 0.0


def tokenize(text: str) -> list[str]:
    chinese_terms = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    latin_terms = re.findall(r"[A-Za-z0-9_+-]{2,}", text.lower())
    return list(dict.fromkeys(chinese_terms + latin_terms))


def keyword_score(query_terms: list[str], haystack: str) -> float:
    if not query_terms:
        return 0.0
    normalized = haystack.lower()
    hits = sum(normalized.count(term.lower()) for term in query_terms)
    return min(1.0, hits / max(len(query_terms), 1))


def parse_embedding(payload: str | None) -> np.ndarray | None:
    if not payload:
        return None
    try:
        return np.asarray(json.loads(payload), dtype=np.float32)
    except Exception:
        return None


class RAGService:
    async def retrieve_async(self, query: str, limit: int = 4) -> list[RetrievedChunk]:
        terms = tokenize(query)
        query_vector = None
        if settings.RAG_EMBEDDING_ENABLED:
            try:
                query_vector = np.asarray(embed_text(query), dtype=np.float32)
            except Exception as exc:
                print(f"[RAG Embedding Error] {exc}")

        async with async_session() as db:
            result = await db.execute(
                select(KnowledgeChunk, KnowledgeDocument).join(
                    KnowledgeDocument,
                    KnowledgeDocument.id == KnowledgeChunk.document_id,
                )
            )

            scored: list[RetrievedChunk] = []
            for chunk, document in result.all():
                haystack = (
                    f"{document.title}\n{document.school or ''}\n{document.college or ''}\n"
                    f"{document.category or ''}\n{chunk.content}"
                )
                k_score = keyword_score(terms, haystack)
                v_score = 0.0

                embedding = parse_embedding(chunk.embedding)
                if query_vector is not None and embedding is not None:
                    v_score = float(np.dot(query_vector, embedding))

                combined = settings.RAG_KEYWORD_WEIGHT * k_score + settings.RAG_VECTOR_WEIGHT * v_score
                if combined > 0:
                    scored.append(
                        RetrievedChunk(
                            title=document.title,
                            content=chunk.content,
                            source=document.source_url,
                            score=combined,
                            keyword_score=k_score,
                            vector_score=v_score,
                        )
                    )

            scored.sort(key=lambda item: item.score or 0, reverse=True)
            return scored[:limit]

    def retrieve(self, query: str, limit: int = 4) -> list[RetrievedChunk]:
        return asyncio.run(self.retrieve_async(query, limit=limit))

    def retrieve_context(self, query: str, limit: int = 4) -> str | None:
        chunks = self.retrieve(query, limit=limit)
        if not chunks:
            return None

        parts = []
        for index, chunk in enumerate(chunks, start=1):
            source = f" 来源：{chunk.source}" if chunk.source else ""
            parts.append(
                f"[{index}] {chunk.title}{source}\n"
                f"检索分数：{chunk.score:.3f}，关键词：{chunk.keyword_score:.3f}，向量：{chunk.vector_score:.3f}\n"
                f"{chunk.content}"
            )
        return "\n\n".join(parts)


_rag_service = RAGService()


def get_rag_service() -> RAGService:
    return _rag_service
