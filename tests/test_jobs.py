from pathlib import Path
import json

from prodkit_browser.jobs import docs_to_rag, ecommerce_price_monitor


ROOT = Path(__file__).resolve().parents[1]


def test_docs_to_rag_writes_records(tmp_path) -> None:
    records = docs_to_rag.run(ROOT / "benchmarks/fixtures/docs_pages.json", tmp_path)

    assert len(records) == 3
    assert (tmp_path / "docs-to-rag/records.json").exists()


def test_docs_to_rag_writes_deterministic_chunks(tmp_path) -> None:
    docs_to_rag.run(ROOT / "benchmarks/fixtures/docs_pages.json", tmp_path)
    chunks_path = tmp_path / "docs-to-rag/chunks.jsonl"

    chunks = [json.loads(line) for line in chunks_path.read_text(encoding="utf-8").splitlines()]

    assert len(chunks) == 3
    assert chunks[0]["source_url"] == "https://example.test/docs/getting-started"
    assert chunks[0]["title"] == "Getting Started"
    assert chunks[0]["heading_path"] == ["Getting Started"]
    assert chunks[0]["token_count"] == len(chunks[0]["text"].split())
    assert chunks[0]["whitespace_token_count"] == len(chunks[0]["text"].split())
    assert chunks[0]["char_count"] == len(chunks[0]["text"])
    assert len(chunks[0]["content_hash"]) == 64
    assert len(chunks[0]["chunk_id"]) == 16

    second_dir = tmp_path / "second-run"
    docs_to_rag.run(ROOT / "benchmarks/fixtures/docs_pages.json", second_dir)
    assert chunks_path.read_text(encoding="utf-8") == (
        second_dir / "docs-to-rag/chunks.jsonl"
    ).read_text(encoding="utf-8")


def test_ecommerce_price_monitor_reports_change_and_drift(tmp_path) -> None:
    summary = ecommerce_price_monitor.run(
        ROOT / "benchmarks/fixtures/ecommerce_pages.json",
        tmp_path,
    )

    assert summary["checked"] == 3
    assert summary["price_changes"] == 1
    assert summary["selector_drift"] == 1
    assert (tmp_path / "ecommerce-price-monitor/price_events.json").exists()
    assert (tmp_path / "ecommerce-price-monitor/selector_drift.json").exists()
