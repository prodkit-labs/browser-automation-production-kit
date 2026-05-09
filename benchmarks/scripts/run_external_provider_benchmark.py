from __future__ import annotations

import argparse
import csv
import importlib
import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from prodkit_browser.adapters.provider import (
    ProviderAdapter,
    ProviderAdapterMetadata,
    ProviderRuntimeConfig,
    missing_required_env,
)
from prodkit_browser.metrics import summarize


def _load_pages(fixture_path: Path) -> dict[str, str]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    return {page["url"]: page["html"] for page in fixture["pages"]}


def _load_adapter_class(import_path: str) -> type[ProviderAdapter]:
    if ":" not in import_path:
        raise ValueError("Adapter path must use the format 'module.path:ClassName'.")
    module_name, class_name = import_path.split(":", 1)
    module = importlib.import_module(module_name)
    adapter_class = getattr(module, class_name)
    return adapter_class


def _metadata_for(adapter_class: type[ProviderAdapter]) -> ProviderAdapterMetadata:
    metadata = getattr(adapter_class, "metadata", None)
    if not isinstance(metadata, ProviderAdapterMetadata):
        raise TypeError("External benchmark adapters must define ProviderAdapterMetadata.")
    if metadata.evidence == "measured":
        raise ValueError("External provider benchmark adapters must not declare measured evidence.")
    return metadata


def _cost_per_1k(rows: list) -> float:
    total_cost = sum(row.cost_usd or 0 for row in rows)
    return round((total_cost / len(rows)) * 1000, 4) if rows else 0.0


def _write_rows(output: Path, evidence: str, rows: list) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as file:
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
        for row in rows:
            writer.writerow(
                [
                    evidence,
                    row.provider,
                    row.url,
                    row.ok,
                    row.latency_ms,
                    row.status_code,
                    row.bytes_out,
                    row.cost_usd,
                    row.error,
                ]
            )


def run_external_benchmark(
    adapter_path: str,
    fixture_path: Path,
    output: Path,
    environ: Mapping[str, str] | None = None,
    runtime_config: ProviderRuntimeConfig | None = None,
) -> dict[str, Any]:
    env = environ if environ is not None else os.environ
    adapter_class = _load_adapter_class(adapter_path)
    metadata = _metadata_for(adapter_class)
    missing = missing_required_env(metadata, env)
    if missing:
        return {
            "ok": False,
            "provider": metadata.name,
            "evidence": metadata.evidence,
            "missing_env": list(missing),
            "message": "Required provider environment variables are missing; no external call was made.",
        }

    pages = _load_pages(fixture_path)
    adapter = adapter_class(environ=env, runtime_config=runtime_config or ProviderRuntimeConfig())
    rows = [adapter.fetch(url) for url in pages]
    summary = summarize(rows)
    summary["cost_per_1k_pages_usd"] = _cost_per_1k(rows)
    _write_rows(output, metadata.evidence, rows)
    return {
        "ok": True,
        "provider": metadata.name,
        "evidence": metadata.evidence,
        "summary": summary,
        "raw_csv": str(output),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run an opt-in external provider benchmark from an adapter import path."
    )
    parser.add_argument("--adapter", required=True, help="Adapter import path, e.g. package.module:Class")
    parser.add_argument("--fixture", default="benchmarks/fixtures/docs_pages.json")
    parser.add_argument("--output", default="benchmarks/raw/external_provider_results.csv")
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--max-retries", type=int, default=0)
    parser.add_argument("--region")
    parser.add_argument("--session-id")
    args = parser.parse_args()

    result = run_external_benchmark(
        adapter_path=args.adapter,
        fixture_path=Path(args.fixture),
        output=Path(args.output),
        runtime_config=ProviderRuntimeConfig(
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
            region=args.region,
            session_id=args.session_id,
        ),
    )
    print(json.dumps(result, indent=2))
    if not result["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
