from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CostScenario:
    scenario: str
    evidence: str
    successful_pages: int
    retries: int
    browser_minutes: float
    provider_calls: int
    artifact_storage_mb: float
    debugging_minutes: float
    browser_minute_cost_usd: float
    provider_call_cost_usd: float
    artifact_storage_gb_month_cost_usd: float
    debugging_hour_cost_usd: float

    @property
    def attempted_pages(self) -> int:
        return self.successful_pages + self.retries

    @property
    def retry_rate(self) -> float:
        if self.successful_pages <= 0:
            return 0.0
        return round(self.retries / self.successful_pages, 4)

    @property
    def total_cost_usd(self) -> float:
        storage_gb = self.artifact_storage_mb / 1024
        return round(
            (self.browser_minutes * self.browser_minute_cost_usd)
            + (self.provider_calls * self.provider_call_cost_usd)
            + (storage_gb * self.artifact_storage_gb_month_cost_usd)
            + ((self.debugging_minutes / 60) * self.debugging_hour_cost_usd),
            6,
        )

    @property
    def cost_per_1k_pages_usd(self) -> float:
        if self.successful_pages <= 0:
            return 0.0
        return round((self.total_cost_usd / self.successful_pages) * 1000, 4)


DEFAULT_SCENARIOS = [
    CostScenario(
        scenario="local-fixture",
        evidence="measured",
        successful_pages=1000,
        retries=0,
        browser_minutes=0,
        provider_calls=0,
        artifact_storage_mb=5,
        debugging_minutes=5,
        browser_minute_cost_usd=0,
        provider_call_cost_usd=0,
        artifact_storage_gb_month_cost_usd=0.02,
        debugging_hour_cost_usd=0,
    ),
    CostScenario(
        scenario="local-playwright",
        evidence="estimated",
        successful_pages=1000,
        retries=40,
        browser_minutes=180,
        provider_calls=0,
        artifact_storage_mb=120,
        debugging_minutes=25,
        browser_minute_cost_usd=0,
        provider_call_cost_usd=0,
        artifact_storage_gb_month_cost_usd=0.02,
        debugging_hour_cost_usd=0,
    ),
    CostScenario(
        scenario="mock-managed-browser",
        evidence="estimated",
        successful_pages=1000,
        retries=70,
        browser_minutes=210,
        provider_calls=1070,
        artifact_storage_mb=180,
        debugging_minutes=20,
        browser_minute_cost_usd=0.002,
        provider_call_cost_usd=0.003,
        artifact_storage_gb_month_cost_usd=0.02,
        debugging_hour_cost_usd=0,
    ),
    CostScenario(
        scenario="future-provider-backed-run",
        evidence="not tested",
        successful_pages=0,
        retries=0,
        browser_minutes=0,
        provider_calls=0,
        artifact_storage_mb=0,
        debugging_minutes=0,
        browser_minute_cost_usd=0,
        provider_call_cost_usd=0,
        artifact_storage_gb_month_cost_usd=0,
        debugging_hour_cost_usd=0,
    ),
]


CSV_FIELDS = [
    "scenario",
    "evidence",
    "successful_pages",
    "attempted_pages",
    "retries",
    "retry_rate",
    "browser_minutes",
    "provider_calls",
    "artifact_storage_mb",
    "debugging_minutes",
    "browser_minute_cost_usd",
    "provider_call_cost_usd",
    "artifact_storage_gb_month_cost_usd",
    "debugging_hour_cost_usd",
    "total_cost_usd",
    "cost_per_1k_pages_usd",
]


def write_raw_cost_model(output: Path, scenarios: list[CostScenario] | None = None) -> list[CostScenario]:
    rows = scenarios or DEFAULT_SCENARIOS
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "scenario": row.scenario,
                    "evidence": row.evidence,
                    "successful_pages": row.successful_pages,
                    "attempted_pages": row.attempted_pages,
                    "retries": row.retries,
                    "retry_rate": row.retry_rate,
                    "browser_minutes": row.browser_minutes,
                    "provider_calls": row.provider_calls,
                    "artifact_storage_mb": row.artifact_storage_mb,
                    "debugging_minutes": row.debugging_minutes,
                    "browser_minute_cost_usd": row.browser_minute_cost_usd,
                    "provider_call_cost_usd": row.provider_call_cost_usd,
                    "artifact_storage_gb_month_cost_usd": row.artifact_storage_gb_month_cost_usd,
                    "debugging_hour_cost_usd": row.debugging_hour_cost_usd,
                    "total_cost_usd": row.total_cost_usd,
                    "cost_per_1k_pages_usd": row.cost_per_1k_pages_usd,
                }
            )
    return rows


def render_report(raw_csv: Path, scenarios: list[CostScenario]) -> str:
    table_rows = "\n".join(
        "| {scenario} | {evidence} | {successful_pages} | {attempted_pages} | "
        "{retries} | {retry_rate:.4f} | {browser_minutes:.2f} | {provider_calls} | "
        "{artifact_storage_mb:.2f} | {debugging_minutes:.2f} | ${total_cost_usd:.4f} | "
        "${cost_per_1k_pages_usd:.4f} |".format(
            scenario=row.scenario,
            evidence=row.evidence,
            successful_pages=row.successful_pages,
            attempted_pages=row.attempted_pages,
            retries=row.retries,
            retry_rate=row.retry_rate,
            browser_minutes=row.browser_minutes,
            provider_calls=row.provider_calls,
            artifact_storage_mb=row.artifact_storage_mb,
            debugging_minutes=row.debugging_minutes,
            total_cost_usd=row.total_cost_usd,
            cost_per_1k_pages_usd=row.cost_per_1k_pages_usd,
        )
        for row in scenarios
    )

    return f"""# Cost Per 1k Pages Report

This report models cost per 1k successful pages for local fixture, local browser,
mock managed browser, and future provider-backed runs.

It is a cost-control report, not a provider ranking.

## Raw Cost Model

Raw assumptions are written to:

```text
{raw_csv}
```

## Cost Inputs

| Input | Why it matters | Cost-control lever |
|---|---|---|
| Attempted pages | Providers may bill attempted pages, not only successful pages | Track retries separately from successful pages |
| Retries | Retried pages can multiply browser and provider usage | Classify failures before retrying |
| Browser minutes | Browser runtime can become the main operating cost | Reduce waits and keep fixture tests fast |
| Proxy/API calls | Provider-backed paths may charge per call or usage unit | Avoid re-fetching stable pages |
| Artifact storage | HTML, screenshots, traces, and logs accumulate | Keep full artifacts for failures and sampled successes |
| Debugging time | Human investigation can dominate low-volume jobs | Preserve failure reasons and artifacts |

## Cost Summary

| Scenario | Evidence | Successful pages | Attempted pages | Retries | Retry rate | Browser minutes | Provider calls | Artifact MB | Debugging minutes | Total cost | Cost per 1k pages |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{table_rows}

## Formula

```text
attempted_pages = successful_pages + retries
retry_rate = retries / successful_pages

total_cost =
  browser_minutes * browser_minute_cost_usd
  + provider_calls * provider_call_cost_usd
  + artifact_storage_gb * artifact_storage_gb_month_cost_usd
  + debugging_hours * debugging_hour_cost_usd

cost_per_1k_pages = total_cost / successful_pages * 1000
```

## Spend Reduction Checklist

- Improve fixture coverage before live runs.
- Separate deterministic failures from transient failures before retrying.
- Set smaller retry budgets for selector drift and parsing failures.
- Keep full artifacts for failures; sample successful artifacts.
- Cache stable public pages where terms and workflow requirements allow it.
- Track cost per successful page, not only cost per request.
- Re-run this model when pricing assumptions or workflow volume changes.

## Decision Notes

- Which cost input is growing fastest:
- Which failures are worth retrying:
- Which artifacts are worth keeping:
- Which local/open-source path remains enough:
- Which provider-backed path needs more benchmark evidence:
"""


def write_report(
    raw_csv: Path,
    output: Path,
    scenarios: list[CostScenario] | None = None,
) -> str:
    rows = write_raw_cost_model(raw_csv, scenarios)
    report = render_report(raw_csv, rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a cost per 1k pages report.")
    parser.add_argument("--raw-csv", default="benchmarks/raw/cost_per_1k_pages.csv")
    parser.add_argument("--output", default="benchmarks/reports/cost-per-1k-pages.md")
    args = parser.parse_args()

    write_report(raw_csv=Path(args.raw_csv), output=Path(args.output))
    print(args.output)


if __name__ == "__main__":
    main()
