from prodkit_browser.adapters.provider import FetchResult
from prodkit_browser.metrics import cost_per_1k_requests, cost_per_1k_successful_pages, percentile_95, summarize
import prodkit_browser
from importlib.metadata import version


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


def test_percentile_95_uses_max_for_small_samples() -> None:
    assert percentile_95([]) == 0
    assert percentile_95([10, 30]) == 30


def test_cost_per_1k_successful_pages_uses_successful_denominator() -> None:
    rows = [
        FetchResult("provider", "https://a.test", True, 10, 200, 100, "ok", cost_usd=0.01),
        FetchResult("provider", "https://b.test", False, 20, 500, 0, "", cost_usd=0.01),
    ]

    assert cost_per_1k_requests(rows) == 10
    assert cost_per_1k_successful_pages(rows) == 20


def test_package_version_matches_metadata() -> None:
    assert prodkit_browser.__version__ == version("browser-automation-production-kit")
