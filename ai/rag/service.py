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
    chinese_terms: list[str] = []
    for term in re.findall(r"[\u4e00-\u9fff]{2,}", text):
        chinese_terms.append(term)
        for size in range(2, min(7, len(term) + 1)):
            chinese_terms.extend(term[index : index + size] for index in range(0, len(term) - size + 1))

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


def needs_score_policy_context(query: str) -> bool:
    return any(
        term in query
        for term in (
            "加分",
            "多少分",
            "几分",
            "一等奖",
            "二等奖",
            "三等奖",
            "获奖",
            "推免",
        )
    )


def is_score_policy_chunk(document: KnowledgeDocument, content: str) -> bool:
    if "推免加分" not in document.title:
        return False
    return (
        "创新创业类竞赛" in content
        or "五级创新创业竞赛" in content
        or ("第一等次" in content and "50" in content and "40" in content and "三B级" in content)
        or ("团队获奖成员加分算法" in content and "教务处、学生工作处、团委" in content)
    )


class RAGService:
    async def retrieve_async(self, query: str, limit: int = 8) -> list[RetrievedChunk]:
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
            seen: set[tuple[int, int]] = set()
            should_add_score_policy = needs_score_policy_context(query)
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
                if should_add_score_policy and is_score_policy_chunk(document, chunk.content):
                    combined = max(combined, 0.92)

                if combined > 0:
                    seen.add((document.id, chunk.chunk_index))
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

                if should_add_score_policy and is_score_policy_chunk(document, chunk.content):
                    key = (document.id, chunk.chunk_index)
                    if key not in seen:
                        seen.add(key)
                        scored.append(
                            RetrievedChunk(
                                title=document.title,
                                content=chunk.content,
                                source=document.source_url,
                                score=0.92,
                                keyword_score=0.0,
                                vector_score=0.0,
                            )
                        )

            scored.sort(key=lambda item: item.score or 0, reverse=True)
            return scored[:limit]

    def retrieve(self, query: str, limit: int = 8) -> list[RetrievedChunk]:
        return asyncio.run(self.retrieve_async(query, limit=limit))

    def retrieve_context(self, query: str, limit: int = 8) -> str | None:
        chunks = self.retrieve(query, limit=limit)
        if not chunks:
            return None

        parts = []
        for index, chunk in enumerate(chunks, start=1):
            source = f" 来源：{chunk.source}" if chunk.source else ""
            score = chunk.score or 0.0
            parts.append(
                f"[{index}] {chunk.title}{source}\n"
                f"检索分数：{score:.3f}，关键词：{chunk.keyword_score:.3f}，向量：{chunk.vector_score:.3f}\n"
                f"{chunk.content}"
            )
        return "\n\n".join(parts)


_rag_service = RAGService()


def get_rag_service() -> RAGService:
    return _rag_service
