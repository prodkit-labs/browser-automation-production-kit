from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Iterable
from urllib.parse import urlparse


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    source_url: str
    title: str
    heading_path: list[str]
    text: str
    token_count: int
    char_count: int
    content_hash: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


def slug_from_url(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    return path.rsplit("/", 1)[-1] or "index"


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_chunk_id(source_url: str, chunk_index: int, text: str) -> str:
    seed = f"{source_url}\n{chunk_index}\n{content_hash(text)}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]


def chunk_text(text: str, max_chars: int = 1200) -> list[str]:
    paragraphs = [part.strip() for part in text.splitlines() if part.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for paragraph in paragraphs:
        separator_len = 1 if current else 0
        proposed_len = current_len + separator_len + len(paragraph)
        if current and proposed_len > max_chars:
            chunks.append("\n".join(current))
            current = [paragraph]
            current_len = len(paragraph)
        else:
            current.append(paragraph)
            current_len = proposed_len

    if current:
        chunks.append("\n".join(current))

    return chunks


def chunks_from_record(record: dict[str, object], max_chars: int = 1200) -> list[DocumentChunk]:
    source_url = str(record["url"])
    title = str(record.get("title") or slug_from_url(source_url).replace("-", " ").title())
    heading_path = record.get("heading_path")
    if not isinstance(heading_path, list):
        heading_path = [title] if title else []
    chunks: list[DocumentChunk] = []

    for index, text in enumerate(chunk_text(str(record["text"]), max_chars=max_chars)):
        chunks.append(
            DocumentChunk(
                chunk_id=stable_chunk_id(source_url, index, text),
                source_url=source_url,
                title=title,
                heading_path=[str(heading) for heading in heading_path],
                text=text,
                token_count=len(text.split()),
                char_count=len(text),
                content_hash=content_hash(text),
            )
        )

    return chunks


def chunks_from_records(records: Iterable[dict[str, object]], max_chars: int = 1200) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for record in records:
        chunks.extend(chunks_from_record(record, max_chars=max_chars))
    return chunks


def to_jsonl(chunks: Iterable[DocumentChunk]) -> str:
    lines = [chunk.to_json() for chunk in chunks]
    return "\n".join(lines) + ("\n" if lines else "")
