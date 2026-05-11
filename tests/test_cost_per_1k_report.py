import csv

from benchmarks.scripts.generate_cost_per_1k_report import (
    CostScenario,
    write_raw_cost_model,
    write_report,
)


def test_cost_model_writes_reproducible_raw_csv(tmp_path) -> None:
    raw_csv = tmp_path / "cost.csv"
    scenarios = [
        CostScenario(
            scenario="example",
            evidence="estimated",
            successful_pages=500,
            retries=10,
            browser_minutes=20,
            provider_calls=510,
            artifact_storage_mb=100,
            debugging_minutes=30,
            browser_minute_cost_usd=0.01,
            provider_call_cost_usd=0.002,
            artifact_storage_gb_month_cost_usd=0.02,
            debugging_hour_cost_usd=0,
        )
    ]

    write_raw_cost_model(raw_csv, scenarios)
    rows = list(csv.DictReader(raw_csv.open(encoding="utf-8")))

    assert rows[0]["scenario"] == "example"
    assert rows[0]["attempted_pages"] == "510"
    assert rows[0]["retries"] == "10"
    assert rows[0]["retry_rate"] == "0.02"
    assert rows[0]["total_cost_usd"] == "1.221953"
    assert rows[0]["cost_per_1k_pages_usd"] == "2.4439"


def test_cost_report_teaches_reduction_without_vendor_ranking(tmp_path) -> None:
    raw_csv = tmp_path / "cost.csv"
    output = tmp_path / "cost.md"

    report = write_report(raw_csv=raw_csv, output=output)

    assert output.exists()
    assert "## Cost Inputs" in report
    assert "## Spend Reduction Checklist" in report
    assert "## Formula" in report
    assert "Attempted pages" in report
    assert "Retry rate" in report
    assert "local-fixture" in report
    assert "local-playwright" in report
    assert "mock-managed-browser" in report
    assert "future-provider-backed-run" in report
    assert "Cost per 1k pages" in report
    assert "not a provider ranking" in report
    assert "best provider" not in report.lower()
    assert "https://www.scraperapi.com" not in report


def test_cost_assumption_worksheet_documents_required_fields() -> None:
    worksheet = open("reports/cost-assumption-worksheet.md", encoding="utf-8").read()

    required_terms = [
        "successful_pages + retries",
        "retries / successful_pages",
        "browser_minutes * browser_minute_cost_usd",
        "provider_calls * provider_call_cost_usd",
        "artifact_storage_gb * artifact_storage_gb_month_cost_usd",
        "total_cost / successful_pages * 1000",
        "Local browser worker",
        "Proxy-backed browser worker",
        "Scraping API",
        "Managed browser provider",
    ]

    for term in required_terms:
        assert term in worksheet

    assert "not a provider ranking" in worksheet
    assert "https://www.scraperapi.com" not in worksheet
