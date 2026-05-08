from pathlib import Path

from prodkit_browser.jobs import docs_to_rag, ecommerce_price_monitor


ROOT = Path(__file__).resolve().parents[1]


def test_docs_to_rag_writes_records(tmp_path) -> None:
    records = docs_to_rag.run(ROOT / "benchmarks/fixtures/docs_pages.json", tmp_path)

    assert len(records) == 3
    assert (tmp_path / "docs-to-rag/records.json").exists()


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
