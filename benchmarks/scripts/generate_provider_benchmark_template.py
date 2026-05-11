from __future__ import annotations

import csv
import json
from pathlib import Path


FIELDS = [
    "provider",
    "category",
    "execution_mode",
    "evidence",
    "evidence_status",
    "measured_at",
    "fixture_mode",
    "source_note",
    "benchmark_status",
    "fixture_scope",
    "metrics_to_collect",
    "tradeoffs_to_test",
    "public_link_policy",
]


CANDIDATES = [
    {
        "provider": "local-fixture",
        "category": "baseline",
        "execution_mode": "local HTTP / fixture",
        "evidence": "measured",
        "evidence_status": "measured",
        "measured_at": "regenerate from current local run",
        "fixture_mode": "local HTTP / fixture",
        "source_note": "fixture-only baseline; does not represent live-site behavior",
        "benchmark_status": "available in this repo",
        "fixture_scope": "docs, ecommerce, browser debugger fixtures",
        "metrics_to_collect": "parse accuracy, bytes out, artifacts written",
        "tradeoffs_to_test": "does not represent live-site behavior",
        "public_link_policy": "no paid link",
    },
    {
        "provider": "local-playwright",
        "category": "baseline",
        "execution_mode": "local browser",
        "evidence": "measured",
        "evidence_status": "measured",
        "measured_at": "regenerate from current local run",
        "fixture_mode": "local browser",
        "source_note": "local browser fixture path; does not represent live provider behavior",
        "benchmark_status": "available in this repo",
        "fixture_scope": "browser debugger and selector drift fixtures",
        "metrics_to_collect": "success rate, p95 latency, screenshots, failure reason",
        "tradeoffs_to_test": "local browser maintenance and host resource limits",
        "public_link_policy": "no paid link",
    },
    {
        "provider": "Apify",
        "category": "hosted automation platform",
        "execution_mode": "hosted Crawlee / workflow platform",
        "evidence": "not tested",
        "evidence_status": "not tested",
        "measured_at": "",
        "fixture_mode": "candidate only",
        "source_note": "candidate provider; add measured raw data before recommendation",
        "benchmark_status": "candidate",
        "fixture_scope": "docs-to-RAG and Crawlee Python workflow",
        "metrics_to_collect": "success rate, p95 latency, storage output, run cost",
        "tradeoffs_to_test": "platform runtime boundaries and workflow portability",
        "public_link_policy": "add link only with nearby disclosure",
    },
    {
        "provider": "ScraperAPI",
        "category": "scraping API",
        "execution_mode": "API-first public page extraction",
        "evidence": "not tested",
        "evidence_status": "not tested",
        "measured_at": "",
        "fixture_mode": "candidate only",
        "source_note": "candidate provider; add measured raw data before recommendation",
        "benchmark_status": "candidate",
        "fixture_scope": "e-commerce price monitor and future SERP-style monitor",
        "metrics_to_collect": "success rate, p95 latency, status codes, cost per 1k successful pages",
        "tradeoffs_to_test": "less browser-level control and API-specific limits",
        "public_link_policy": "add affiliate link only with nearby disclosure",
    },
    {
        "provider": "Decodo",
        "category": "proxy / scraping API",
        "execution_mode": "proxy-backed browser or scraping API",
        "evidence": "not tested",
        "evidence_status": "not tested",
        "measured_at": "",
        "fixture_mode": "candidate only",
        "source_note": "candidate provider; add measured raw data before recommendation",
        "benchmark_status": "candidate",
        "fixture_scope": "e-commerce and region/session workflows",
        "metrics_to_collect": "block rate, retry cost, region behavior, cost per 1k successful pages",
        "tradeoffs_to_test": "proxy operations and site/API terms review",
        "public_link_policy": "add link only with nearby disclosure",
    },
    {
        "provider": "Bright Data",
        "category": "enterprise web data infrastructure",
        "execution_mode": "proxy, unlocker, dataset, or scraping infrastructure",
        "evidence": "not tested",
        "evidence_status": "not tested",
        "measured_at": "",
        "fixture_mode": "candidate only",
        "source_note": "candidate provider; add measured raw data before recommendation",
        "benchmark_status": "candidate",
        "fixture_scope": "high-volume public data workflows",
        "metrics_to_collect": "success rate, p95 latency, retries, cost per 1k successful pages",
        "tradeoffs_to_test": "enterprise complexity, cost, and compliance review",
        "public_link_policy": "add link only with nearby disclosure",
    },
    {
        "provider": "ScrapingBee",
        "category": "scraping API",
        "execution_mode": "API-first public page extraction",
        "evidence": "not tested",
        "evidence_status": "not tested",
        "measured_at": "",
        "fixture_mode": "candidate only",
        "source_note": "candidate provider; add measured raw data before recommendation",
        "benchmark_status": "candidate",
        "fixture_scope": "e-commerce and docs-style public pages",
        "metrics_to_collect": "success rate, p95 latency, JS rendering support, cost per 1k successful pages",
        "tradeoffs_to_test": "plan limits and less direct browser-worker control",
        "public_link_policy": "add link only with nearby disclosure",
    },
    {
        "provider": "Browserbase",
        "category": "managed browser API",
        "execution_mode": "hosted Playwright/browser runtime",
        "evidence": "not tested",
        "evidence_status": "not tested",
        "measured_at": "",
        "fixture_mode": "partner candidate only",
        "source_note": "partner candidate; add measured raw data before recommendation",
        "benchmark_status": "partner candidate",
        "fixture_scope": "Playwright production debugger",
        "metrics_to_collect": "success rate, p95 latency, screenshots, traces, cost per run",
        "tradeoffs_to_test": "provider cost and runtime-specific debugging surface",
        "public_link_policy": "no affiliate link unless partner terms exist",
    },
    {
        "provider": "Browserless",
        "category": "managed browser API",
        "execution_mode": "hosted Playwright/Puppeteer browser runtime",
        "evidence": "not tested",
        "evidence_status": "not tested",
        "measured_at": "",
        "fixture_mode": "partner candidate only",
        "source_note": "partner candidate; add measured raw data before recommendation",
        "benchmark_status": "partner candidate",
        "fixture_scope": "Playwright production debugger",
        "metrics_to_collect": "success rate, p95 latency, screenshots, sessions, cost per run",
        "tradeoffs_to_test": "provider cost and browser-service constraints",
        "public_link_policy": "no affiliate link unless partner terms exist",
    },
]


def write_template(output: Path) -> list[dict[str, str]]:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(CANDIDATES)
    return CANDIDATES


def main() -> None:
    output = Path("benchmarks/raw/provider_benchmark_template.csv")
    rows = write_template(output)
    print(json.dumps({"rows": len(rows), "raw_csv": str(output)}, indent=2))


if __name__ == "__main__":
    main()
