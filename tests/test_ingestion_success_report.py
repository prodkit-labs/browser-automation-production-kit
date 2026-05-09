import csv
from pathlib import Path

from benchmarks.scripts.generate_ingestion_success_report import (
    future_provider_placeholder,
    run_local_ingestion,
    write_report,
)


ROOT = Path(__file__).resolve().parents[1]


def test_ingestion_success_report_writes_raw_csv_and_report(tmp_path) -> None:
    fixture = ROOT / "benchmarks/fixtures/docs_pages.json"
    artifact_dir = tmp_path / "artifacts"
    raw_csv = tmp_path / "raw/ingestion_success_cost.csv"
    report_path = tmp_path / "reports/ingestion-success-cost.md"

    local_row = run_local_ingestion(fixture, artifact_dir)
    report = write_report(raw_csv, report_path, [local_row, future_provider_placeholder()])
    rows = list(csv.DictReader(raw_csv.open(encoding="utf-8")))

    assert rows[0]["scenario"] == "local-docs-to-rag"
    assert rows[0]["evidence"] == "measured"
    assert rows[0]["pages_attempted"] == "3"
    assert rows[0]["pages_succeeded"] == "3"
    assert rows[0]["pages_failed"] == "0"
    assert rows[0]["success_rate"] == "1.0"
    assert rows[0]["chunks_produced"] == "3"
    assert int(rows[0]["bytes_fetched"]) > 0
    assert float(rows[0]["artifact_storage_mb"]) > 0
    assert rows[0]["artifact_storage_gb_month_rate_usd"] == "0.02"
    assert float(rows[0]["artifact_storage_cost_usd"]) < 0.0001
    assert rows[1]["evidence"] == "not tested"
    assert "Ingestion Success And Cost Report" in report
    assert "Success rate: 100.00%" in report
    assert "Failed pages: 0" in report
    assert "Chunks produced: 3" in report
    assert "future-provider-backed-ingestion" in report
    assert "Storage rate / GB-month" in report
    assert "Storage cost" in report
    assert "not a provider ranking" in report
    assert "best provider" not in report.lower()
    assert "https://www.scraperapi.com" not in report
    assert report_path.exists()
