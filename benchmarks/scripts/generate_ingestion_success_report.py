from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from prodkit_browser.adapters.provider import LocalFixtureAdapter
from prodkit_browser.artifacts import ArtifactWriter
from prodkit_browser.jobs.docs_to_rag import load_fixture, normalize_record
from prodkit_browser.rag_chunks import chunks_from_records, to_jsonl


CSV_FIELDS = [
    "scenario",
    "evidence",
    "pages_attempted",
    "pages_succeeded",
    "pages_failed",
    "success_rate",
    "bytes_fetched",
    "chunks_produced",
    "retries",
    "runtime_ms",
    "artifact_storage_mb",
    "local_runtime_cost_usd",
    "artifact_storage_gb_month_rate_usd",
    "artifact_storage_cost_usd",
    "provider_calls",
    "provider_cost_usd",
    "notes",
]


@dataclass(frozen=True)
class IngestionReportRow:
    scenario: str
    evidence: str
    pages_attempted: int
    pages_succeeded: int
    pages_failed: int
    bytes_fetched: int
    chunks_produced: int
    retries: int
    runtime_ms: float
    artifact_storage_mb: float
    local_runtime_cost_usd: float
    artifact_storage_gb_month_rate_usd: float
    provider_calls: int
    provider_cost_usd: float
    notes: str

    @property
    def success_rate(self) -> float:
        if self.pages_attempted == 0:
            return 0.0
        return round(self.pages_succeeded / self.pages_attempted, 4)

    @property
    def artifact_storage_cost_usd(self) -> float:
        storage_gb = self.artifact_storage_mb / 1024
        return round(storage_gb * self.artifact_storage_gb_month_rate_usd, 8)


def _directory_size_mb(path: Path) -> float:
    if not path.exists():
        return 0.0
    total_bytes = sum(item.stat().st_size for item in path.rglob("*") if item.is_file())
    return round(total_bytes / (1024 * 1024), 6)


def run_local_ingestion(
    fixture_path: Path,
    artifact_dir: Path,
    *,
    retries: int = 0,
    local_runtime_cost_usd: float = 0.0,
    artifact_storage_gb_month_rate_usd: float = 0.02,
) -> IngestionReportRow:
    pages, urls = load_fixture(fixture_path)
    adapter = LocalFixtureAdapter(pages)
    writer = ArtifactWriter(artifact_dir)
    records: list[dict[str, object]] = []
    bytes_fetched = 0
    failures = 0

    start = perf_counter()
    for url in urls:
        result = adapter.fetch(url)
        bytes_fetched += result.bytes_out
        if result.ok:
            writer.write_text(f"html/{url.split('/')[-1] or 'index'}.html", result.text)
            records.append(normalize_record(url, result.text))
        else:
            failures += 1

    writer.write_text("docs-to-rag/records.json", json.dumps(records, indent=2))
    chunks = chunks_from_records(records)
    writer.write_text("docs-to-rag/chunks.jsonl", to_jsonl(chunks))
    runtime_ms = (perf_counter() - start) * 1000

    return IngestionReportRow(
        scenario="local-docs-to-rag",
        evidence="measured",
        pages_attempted=len(urls),
        pages_succeeded=len(records),
        pages_failed=failures,
        bytes_fetched=bytes_fetched,
        chunks_produced=len(chunks),
        retries=retries,
        runtime_ms=round(runtime_ms, 4),
        artifact_storage_mb=_directory_size_mb(artifact_dir),
        local_runtime_cost_usd=local_runtime_cost_usd,
        artifact_storage_gb_month_rate_usd=artifact_storage_gb_month_rate_usd,
        provider_calls=0,
        provider_cost_usd=0.0,
        notes="local fixture run; no external provider calls",
    )


def future_provider_placeholder() -> IngestionReportRow:
    return IngestionReportRow(
        scenario="future-provider-backed-ingestion",
        evidence="not tested",
        pages_attempted=0,
        pages_succeeded=0,
        pages_failed=0,
        bytes_fetched=0,
        chunks_produced=0,
        retries=0,
        runtime_ms=0.0,
        artifact_storage_mb=0.0,
        local_runtime_cost_usd=0.0,
        artifact_storage_gb_month_rate_usd=0.0,
        provider_calls=0,
        provider_cost_usd=0.0,
        notes="placeholder only; add measured raw data before comparing providers",
    )


def write_raw_results(output: Path, rows: list[IngestionReportRow]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "scenario": row.scenario,
                    "evidence": row.evidence,
                    "pages_attempted": row.pages_attempted,
                    "pages_succeeded": row.pages_succeeded,
                    "pages_failed": row.pages_failed,
                    "success_rate": row.success_rate,
                    "bytes_fetched": row.bytes_fetched,
                    "chunks_produced": row.chunks_produced,
                    "retries": row.retries,
                    "runtime_ms": row.runtime_ms,
                    "artifact_storage_mb": row.artifact_storage_mb,
                    "local_runtime_cost_usd": row.local_runtime_cost_usd,
                    "artifact_storage_gb_month_rate_usd": row.artifact_storage_gb_month_rate_usd,
                    "artifact_storage_cost_usd": row.artifact_storage_cost_usd,
                    "provider_calls": row.provider_calls,
                    "provider_cost_usd": row.provider_cost_usd,
                    "notes": row.notes,
                }
            )


def render_report(raw_csv: Path, rows: list[IngestionReportRow]) -> str:
    measured_rows = [row for row in rows if row.evidence == "measured"]
    measured = measured_rows[0] if measured_rows else None
    success_rate = f"{(measured.success_rate * 100):.2f}%" if measured else "0.00%"
    failures = measured.pages_failed if measured else 0
    chunks = measured.chunks_produced if measured else 0

    table_rows = "\n".join(
        "| {scenario} | {evidence} | {pages_attempted} | {pages_succeeded} | "
        "{pages_failed} | {success_rate:.2%} | {bytes_fetched} | {chunks_produced} | "
        "{retries} | {runtime_ms:.2f} | {artifact_storage_mb:.6f} | "
        "${local_runtime_cost_usd:.4f} | ${artifact_storage_gb_month_rate_usd:.4f} | "
        "${artifact_storage_cost_usd:.8f} | "
        "{provider_calls} | ${provider_cost_usd:.4f} |".format(
            scenario=row.scenario,
            evidence=row.evidence,
            pages_attempted=row.pages_attempted,
            pages_succeeded=row.pages_succeeded,
            pages_failed=row.pages_failed,
            success_rate=row.success_rate,
            bytes_fetched=row.bytes_fetched,
            chunks_produced=row.chunks_produced,
            retries=row.retries,
            runtime_ms=row.runtime_ms,
            artifact_storage_mb=row.artifact_storage_mb,
            local_runtime_cost_usd=row.local_runtime_cost_usd,
            artifact_storage_gb_month_rate_usd=row.artifact_storage_gb_month_rate_usd,
            artifact_storage_cost_usd=row.artifact_storage_cost_usd,
            provider_calls=row.provider_calls,
            provider_cost_usd=row.provider_cost_usd,
        )
        for row in rows
    )

    return f"""# Ingestion Success And Cost Report

This report summarizes docs-to-RAG ingestion success before any provider-backed
path is evaluated.

It separates measured local fixture data from future provider-backed
placeholders. It is not a provider ranking.

## Raw Data

Raw rows are written to:

```text
{raw_csv}
```

## Measured Local Summary

- Success rate: {success_rate}
- Failed pages: {failures}
- Chunks produced: {chunks}

## Cost Inputs

| Input | Why it matters | How to use it |
|---|---|---|
| Runtime | Long runs can become local or hosted execution cost | Track runtime before scaling page counts |
| Artifact storage | HTML and chunk files accumulate over repeated runs | Keep full artifacts for failures and sample successes |
| Retries | Retried pages multiply runtime and provider calls | Classify failures before raising retry budgets |
| Provider calls | Future hosted paths may charge per call or usage unit | Keep provider-backed rows as `not tested` until measured |

## Ingestion Summary

| Scenario | Evidence | Pages attempted | Pages succeeded | Pages failed | Success rate | Bytes fetched | Chunks produced | Retries | Runtime ms | Artifact MB | Local runtime cost | Storage rate / GB-month | Storage cost | Provider calls | Provider cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{table_rows}

## How To Use This Before Scaling

- Review failed pages before increasing page volume.
- Keep local fixture success stable before adding hosted browser or provider-backed runs.
- Use measured artifact size to set storage retention rules.
- Treat provider-backed rows as placeholders until raw benchmark data exists.
- Compare future provider-backed rows only when assumptions are recorded in the CSV.
"""


def write_report(raw_csv: Path, output: Path, rows: list[IngestionReportRow]) -> str:
    write_raw_results(raw_csv, rows)
    report = render_report(raw_csv, rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a docs-to-RAG ingestion success and cost report.")
    parser.add_argument("--fixture", default="benchmarks/fixtures/docs_pages.json")
    parser.add_argument("--artifact-dir", default="artifacts/ingestion-success")
    parser.add_argument("--raw-csv", default="benchmarks/raw/ingestion_success_cost.csv")
    parser.add_argument("--report", default="benchmarks/reports/ingestion-success-cost.md")
    parser.add_argument("--artifact-storage-gb-month-rate-usd", type=float, default=0.02)
    args = parser.parse_args()

    local_row = run_local_ingestion(
        fixture_path=Path(args.fixture),
        artifact_dir=Path(args.artifact_dir),
        artifact_storage_gb_month_rate_usd=args.artifact_storage_gb_month_rate_usd,
    )
    rows = [local_row, future_provider_placeholder()]
    write_report(Path(args.raw_csv), Path(args.report), rows)
    print(
        json.dumps(
            {
                "pages_attempted": local_row.pages_attempted,
                "pages_succeeded": local_row.pages_succeeded,
                "pages_failed": local_row.pages_failed,
                "chunks_produced": local_row.chunks_produced,
                "raw_csv": args.raw_csv,
                "report": args.report,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
