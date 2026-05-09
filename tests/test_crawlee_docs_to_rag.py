import asyncio
import json
from pathlib import Path

import pytest

from prodkit_browser.jobs import docs_to_rag
from prodkit_browser.rag_chunks import chunks_from_records


pytest.importorskip("crawlee")

from prodkit_browser.jobs.crawlee_docs_to_rag import run_crawlee_docs_to_rag


ROOT = Path(__file__).resolve().parents[1]


def test_crawlee_docs_to_rag_writes_shared_chunk_schema_and_metadata(tmp_path) -> None:
    fixture = ROOT / "benchmarks/fixtures/docs_pages.json"
    local_records = docs_to_rag.run(fixture, tmp_path / "local")
    asyncio.run(run_crawlee_docs_to_rag(fixture, tmp_path / "crawlee"))

    local_chunks = chunks_from_records(local_records)
    crawlee_chunks_path = tmp_path / "crawlee/crawlee-docs-to-rag/chunks.jsonl"
    crawlee_chunks = [
        json.loads(line) for line in crawlee_chunks_path.read_text(encoding="utf-8").splitlines()
    ]
    crawlee_chunks = sorted(crawlee_chunks, key=lambda chunk: chunk["source_url"])

    assert len(crawlee_chunks) == len(local_chunks)
    assert set(crawlee_chunks[0]) == {
        "chunk_id",
        "source_url",
        "title",
        "heading_path",
        "text",
        "token_count",
        "whitespace_token_count",
        "char_count",
        "content_hash",
    }
    getting_started = next(
        chunk
        for chunk in crawlee_chunks
        if chunk["source_url"] == "https://example.test/docs/getting-started"
    )
    assert getting_started["heading_path"] == ["Getting Started"]

    metadata_path = tmp_path / "crawlee/crawlee-docs-to-rag/chunk_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata = sorted(metadata, key=lambda item: item["discovered_source_url"])

    assert len(metadata) == 3
    assert metadata[0]["chunk_id"]
    assert metadata[0]["crawl_run_id"] == "local-fixture:docs_pages"
    assert metadata[0]["request_url"].startswith("http://127.0.0.1:")
    assert metadata[0]["response_status"] == 200
    assert metadata[0]["storage_path"] == str(tmp_path / "crawlee/crawlee-storage")
    assert metadata[0]["discovered_source_url"] == "https://example.test/docs/debugging"
