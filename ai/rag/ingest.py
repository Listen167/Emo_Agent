import argparse
import asyncio
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from sqlalchemy import delete

from ai.rag.embedding import embed_texts
from app.core.config import settings
from app.core.database import async_session, init_db
from app.models.message import KnowledgeChunk, KnowledgeDocument


@dataclass
class ParsedMarkdown:
    metadata: dict[str, str]
    content: str


def parse_markdown(path: Path) -> ParsedMarkdown:
    text = path.read_text(encoding="utf-8")
    metadata: dict[str, str] = {}
    body = text

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            _, raw_metadata, body = parts
            for line in raw_metadata.splitlines():
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip().strip('"')

    return ParsedMarkdown(metadata=metadata, content=body.strip())


def split_chunks(content: str, max_chars: int = 700) -> list[str]:
    blocks = [block.strip() for block in re.split(r"\n(?=#{1,6}\s)|\n\s*\n", content) if block.strip()]
    chunks: list[str] = []
    current = ""

    for block in blocks:
        candidate = f"{current}\n\n{block}".strip() if current else block
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(block) <= max_chars:
            current = block
        else:
            chunks.extend(block[i : i + max_chars] for i in range(0, len(block), max_chars))
            current = ""

    if current:
        chunks.append(current)
    return chunks


def _embedding_payloads(chunks: list[str]) -> list[str | None]:
    if not settings.RAG_EMBEDDING_ENABLED:
        return [None for _ in chunks]
    vectors = embed_texts(chunks)
    return [json.dumps(vector, ensure_ascii=False, separators=(",", ":")) for vector in vectors]


async def ingest_markdown_file(path: Path) -> tuple[int, int]:
    parsed = parse_markdown(path)
    title = parsed.metadata.get("title") or path.stem
    chunks = split_chunks(parsed.content)
    embeddings = _embedding_payloads(chunks)

    async with async_session() as db:
        document = KnowledgeDocument(
            title=title,
            school=parsed.metadata.get("school"),
            college=parsed.metadata.get("college"),
            category=parsed.metadata.get("category"),
            source_url=parsed.metadata.get("source") or parsed.metadata.get("source_url"),
            content=parsed.content,
        )
        db.add(document)
        await db.flush()

        for index, chunk in enumerate(chunks):
            db.add(
                KnowledgeChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk,
                    embedding=embeddings[index],
                )
            )

        await db.commit()
        return document.id, len(chunks)


async def ingest_directory(directory: Path, reset: bool = False) -> None:
    await init_db()

    async with async_session() as db:
        if reset:
            await db.execute(delete(KnowledgeChunk))
            await db.execute(delete(KnowledgeDocument))
            await db.commit()

    files = sorted(directory.glob("*.md"))
    if not files:
        print(f"No markdown files found in {directory}")
        return

    for path in files:
        document_id, chunk_count = await ingest_markdown_file(path)
        print(f"Imported {path.name}: document_id={document_id}, chunks={chunk_count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import campus knowledge markdown files into SQLite.")
    parser.add_argument("--dir", type=Path, default=settings.KNOWLEDGE_RAW_DIR)
    parser.add_argument("--reset", action="store_true", help="Clear existing knowledge documents before importing.")
    args = parser.parse_args()
    asyncio.run(ingest_directory(args.dir, reset=args.reset))


if __name__ == "__main__":
    main()
