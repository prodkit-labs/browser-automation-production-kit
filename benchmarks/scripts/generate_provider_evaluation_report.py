from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from prodkit_browser.metrics import percentile_95


@dataclass(frozen=True)
class ProviderReportRow:
    provider: str
    category: str
    evidence: str
    runs: int
    success_rate: float
    p95_latency_ms: float
    cost_per_1k_requests_usd: float
    cost_per_1k_successful_pages_usd: float
    artifact_support: str
    failure_classification: str


DEFAULT_CATEGORIES = {
    "local-fixture": "local/open-source baseline",
    "local-playwright": "local/open-source baseline",
    "mock-managed-browser": "managed browser API",
    "mock-provider-with-throttle": "managed browser API",
    "Apify": "hosted automation platform",
    "ScraperAPI": "scraping API",
    "Decodo": "proxy/data infrastructure",
    "Bright Data": "proxy/data infrastructure",
    "ScrapingBee": "scraping API",
    "Browserbase": "managed browser API",
    "Browserless": "managed browser API",
}


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def _as_float(value: str | None) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)


def _failure_label(error: str) -> str:
    cleaned = error.strip()
    return cleaned if cleaned else "none"


def summarize_raw_csv(raw_csv: Path) -> list[ProviderReportRow]:
    provider_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    with raw_csv.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            provider_rows[row["provider"]].append(row)

    summaries = []
    for provider, rows in sorted(provider_rows.items()):
        runs = len(rows)
        successes = sum(1 for row in rows if _as_bool(row["ok"]))
        evidence = rows[0].get("run_evidence") or rows[0].get("evidence", "not tested")
        category = rows[0].get("category") or DEFAULT_CATEGORIES.get(provider, "needs category")
        latencies = [_as_float(row.get("latency_ms")) for row in rows]
        costs = [_as_float(row.get("cost_usd")) for row in rows]
        total_cost = sum(costs)
        failures = Counter(_failure_label(row.get("error", "")) for row in rows)
        artifact_support = "html" if any(
            row.get("artifact_path") or _as_float(row.get("bytes_out")) > 0 for row in rows
        ) else "none"
        summaries.append(
            ProviderReportRow(
                provider=provider,
                category=category,
                evidence=evidence,
                runs=runs,
                success_rate=round(successes / runs, 4) if runs else 0.0,
                p95_latency_ms=percentile_95(latencies),
                cost_per_1k_requests_usd=round((total_cost / runs) * 1000, 4) if runs else 0.0,
                cost_per_1k_successful_pages_usd=round((total_cost / successes) * 1000, 4)
                if successes
                else 0.0,
                artifact_support=artifact_support,
                failure_classification=", ".join(
                    f"{label}: {count}" for label, count in sorted(failures.items())
                ),
            )
        )
    return summaries


def render_report(
    raw_csv: Path,
    rows: list[ProviderReportRow],
    fixture_scope: str,
    workflow: str,
) -> str:
    metric_rows = "\n".join(
        "| {provider} | {category} | {evidence} | {runs} | {success_rate:.4f} | "
        "{p95_latency_ms:.2f} ms | ${cost_per_1k_requests_usd:.4f} | "
        "${cost_per_1k_successful_pages_usd:.4f} | {artifact_support} | {failure_classification} |".format(
            **row.__dict__
        )
        for row in rows
    )
    if not metric_rows:
        metric_rows = (
            "| no rows | needs category | not tested | 0 | 0.0000 | 0.00 ms | "
            "$0.0000 | $0.0000 | none | none |"
        )

    return f"""# Provider Evaluation Report

This report summarizes raw benchmark CSV for a production provider decision.
It is not a provider ranking.

Local/open-source execution remains the default path unless benchmark evidence
shows a production reason to evaluate paid provider options.

## Disclosure Checklist

- [ ] This report includes a local or open-source path.
- [ ] Any future provider link appears near a disclosure note.
- [ ] Any affiliate relationship is disclosed before the link is clicked.
- [ ] Provider placement is based on workflow fit, evidence, and tradeoffs.
- [ ] No provider is described as universally best.
- [ ] No ranking is published without comparable benchmark data.
- [ ] Cost-control notes explain how to reduce spend.

## Fixture Scope

| Field | Value |
|---|---|
| Workflow | {workflow} |
| Fixture scope | {fixture_scope} |
| Raw CSV | `{raw_csv}` |

## Setup

| Field | Value |
|---|---|
| Benchmark command | Document the exact command used for this run. |
| Adapter | Document adapter name or import path. |
| Runtime | Document local fixture, local browser, hosted workflow, managed browser API, scraping API, or proxy-backed browser. |
| Artifact directory | Document output artifact path. |

## Credentials And Rate Limits

| Field | Value |
|---|---|
| Required environment variables | Names only, never values. |
| Optional environment variables | Names only, never values. |
| Rate limit assumptions | Documented limits or not tested. |
| Retry budget | Document configured retries. |
| Timeout | Document configured timeout. |

## Summary Metrics

| Provider | Category | Evidence | Runs | Success rate | p95 latency | Cost per 1k requests | Cost per 1k successful pages | Artifact support | Failure classification |
|---|---|---|---:|---:|---:|---:|---:|---|---|
{metric_rows}

## Category Tradeoffs

### Local/Open-Source Path

- Useful for parser development, fixture coverage, CI, and debugging without paid services.
- Watch for gaps between fixtures and live public pages.
- Upgrade only when production evidence shows reliability, scale, region, browser, or maintenance pressure.

### Hosted Automation Platform

- Document platform runtime boundaries, storage model, workflow portability, scheduling semantics, and run cost.

### Managed Browser API

- Document cost, browser version support, debugging surface, concurrency limits, artifact retention, and runtime behavior.

### Scraping API

- Document browser-level control, rendering behavior, request limits, retry behavior, response shape, and cost per successful page.

### Proxy/Data Infrastructure

- Document terms review, operations work, block-rate measurement, bandwidth pricing, session behavior, and compliance boundaries.

### Deployment Platform

- Document browser dependencies, worker resources, job scheduling, artifact storage, and maintenance effort.

## Decision Notes

- When local execution is enough:
- What failed or became expensive:
- Which metrics changed the decision:
- What needs another benchmark before a provider link is added:
"""


def write_report(
    raw_csv: Path,
    output: Path,
    fixture_scope: str,
    workflow: str,
) -> str:
    rows = summarize_raw_csv(raw_csv)
    report = render_report(raw_csv, rows, fixture_scope, workflow)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a provider evaluation Markdown report.")
    parser.add_argument("--raw-csv", default="benchmarks/raw/provider_stub_results.csv")
    parser.add_argument("--output", default="benchmarks/reports/provider-evaluation-report.md")
    parser.add_argument("--workflow", default="provider scaffold benchmark")
    parser.add_argument("--fixture-scope", default="local docs fixture pages")
    args = parser.parse_args()

    write_report(
        raw_csv=Path(args.raw_csv),
        output=Path(args.output),
        fixture_scope=args.fixture_scope,
        workflow=args.workflow,
    )
    print(args.output)


if __name__ == "__main__":
    main()
