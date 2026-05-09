import csv

from benchmarks.scripts.generate_provider_evaluation_report import (
    summarize_raw_csv,
    write_report,
)


def test_provider_evaluation_report_summarizes_raw_csv(tmp_path) -> None:
    raw_csv = tmp_path / "provider_results.csv"
    with raw_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "evidence",
                "provider",
                "url",
                "ok",
                "latency_ms",
                "status_code",
                "bytes_out",
                "cost_usd",
                "error",
            ]
        )
        writer.writerow(["measured", "local-fixture", "https://example.test/a", "true", 10, 200, 100, 0, ""])
        writer.writerow(
            ["measured", "local-fixture", "https://example.test/b", "false", 30, 500, 0, 0, "timeout"]
        )

    rows = summarize_raw_csv(raw_csv)

    assert len(rows) == 1
    assert rows[0].provider == "local-fixture"
    assert rows[0].category == "local/open-source baseline"
    assert rows[0].evidence == "measured"
    assert rows[0].runs == 2
    assert rows[0].success_rate == 0.5
    assert rows[0].p95_latency_ms == 30
    assert rows[0].cost_per_1k_requests_usd == 0
    assert rows[0].cost_per_1k_successful_pages_usd == 0
    assert "timeout: 1" in rows[0].failure_classification


def test_provider_evaluation_report_contains_required_policy_sections(tmp_path) -> None:
    raw_csv = tmp_path / "provider_results.csv"
    raw_csv.write_text(
        "evidence,provider,url,ok,latency_ms,status_code,bytes_out,cost_usd,error\n"
        "not tested,ScraperAPI,https://example.test,true,100,200,1000,0.01,\n",
        encoding="utf-8",
    )
    output = tmp_path / "report.md"

    report = write_report(
        raw_csv=raw_csv,
        output=output,
        fixture_scope="e-commerce fixture pages",
        workflow="e-commerce price monitor",
    )

    assert output.exists()
    assert "## Disclosure Checklist" in report
    assert "## Fixture Scope" in report
    assert "## Credentials And Rate Limits" in report
    assert "## Summary Metrics" in report
    assert "## Category Tradeoffs" in report
    assert "Cost per 1k requests" in report
    assert "Cost per 1k successful pages" in report
    assert "Artifact support" in report
    assert "Failure classification" in report
    assert "affiliate relationship is disclosed" in report
    assert "https://www.scraperapi.com" not in report
    assert "best provider" not in report.lower()


def test_provider_evaluation_report_reads_external_run_metadata(tmp_path) -> None:
    raw_csv = tmp_path / "external_results.csv"
    raw_csv.write_text(
        "run_evidence,provider_candidate_evidence,provider,category,execution_mode,"
        "fixture_scope,url,ok,latency_ms,status_code,bytes_out,cost_usd,artifact_path,"
        "error,timeout_seconds,max_retries,region,session_used\n"
        "measured,not tested,example-external-provider,managed browser API,"
        "hosted browser runtime,reviewed public URL fixture,https://example.com/,"
        "true,100,200,1000,0.01,,,"
        "30,0,,False\n",
        encoding="utf-8",
    )

    rows = summarize_raw_csv(raw_csv)

    assert rows[0].provider == "example-external-provider"
    assert rows[0].category == "managed browser API"
    assert rows[0].evidence == "measured"
    assert rows[0].cost_per_1k_successful_pages_usd == 10
