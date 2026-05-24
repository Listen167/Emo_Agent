import argparse
import asyncio
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

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


async def ingest_markdown_file(path: Path) -> tuple[int, int]:
    parsed = parse_markdown(path)
    title = parsed.metadata.get("title") or path.stem
    chunks = split_chunks(parsed.content)

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
            db.add(KnowledgeChunk(document_id=document.id, chunk_index=index, content=chunk))

        await db.commit()
        return document.id, len(chunks)


async def ingest_directory(directory: Path) -> None:
    await init_db()
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
    args = parser.parse_args()
    asyncio.run(ingest_directory(args.dir))


if __name__ == "__main__":
    main()
