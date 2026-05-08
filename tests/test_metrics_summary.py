from prodkit_browser.adapters.provider import FetchResult
from prodkit_browser.metrics import summarize


def test_summarize_reports_success_rate_and_bytes() -> None:
    rows = [
        FetchResult("local", "https://a.test", True, 10, 200, 100, "ok"),
        FetchResult("local", "https://b.test", False, 20, 500, 0, "", error="failed"),
    ]

    summary = summarize(rows)

    assert summary["count"] == 2
    assert summary["success_rate"] == 0.5
    assert summary["p95_latency_ms"] == 20
    assert summary["bytes_out"] == 100
