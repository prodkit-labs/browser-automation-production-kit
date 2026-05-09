from __future__ import annotations

import argparse
import csv
import importlib
import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from prodkit_browser.adapters.provider import (
    EvidenceLabel,
    ProviderAdapter,
    ProviderAdapterMetadata,
    ProviderRuntimeConfig,
    missing_required_env,
)
from prodkit_browser.metrics import cost_per_1k_requests, cost_per_1k_successful_pages, summarize


def _load_urls(fixture_path: Path) -> list[str]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    return [str(page["url"]) for page in fixture["pages"]]


def _reject_local_only_urls(urls: list[str]) -> None:
    local_only_hosts = {"example.test", "shop.example.test"}
    blocked = [
        url
        for url in urls
        if (urlparse(url).hostname or "").lower() in local_only_hosts
    ]
    if blocked:
        raise ValueError(
            "example.test fixtures are local-only. Use a reviewed public URL fixture "
            "for external provider benchmarks."
        )


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
    return metadata


def _write_rows(
    output: Path,
    *,
    run_evidence: EvidenceLabel,
    metadata: ProviderAdapterMetadata,
    rows: list,
    fixture_scope: str,
    runtime_config: ProviderRuntimeConfig,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "run_evidence",
                "provider_candidate_evidence",
                "provider",
                "category",
                "execution_mode",
                "fixture_scope",
                "url",
                "ok",
                "latency_ms",
                "status_code",
                "bytes_out",
                "cost_usd",
                "artifact_path",
                "error",
                "timeout_seconds",
                "max_retries",
                "region",
                "session_used",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    run_evidence,
                    metadata.evidence,
                    row.provider,
                    metadata.category,
                    metadata.execution_mode,
                    fixture_scope,
                    row.url,
                    row.ok,
                    row.latency_ms,
                    row.status_code,
                    row.bytes_out,
                    row.cost_usd,
                    row.artifact_path,
                    row.error,
                    runtime_config.timeout_seconds,
                    runtime_config.max_retries,
                    runtime_config.region or "",
                    bool(runtime_config.session_id),
                ]
            )


def run_external_benchmark(
    adapter_path: str,
    fixture_path: Path,
    output: Path,
    environ: Mapping[str, str] | None = None,
    runtime_config: ProviderRuntimeConfig | None = None,
    run_evidence: EvidenceLabel = "measured",
    fixture_scope: str = "reviewed public URL fixture",
) -> dict[str, Any]:
    env = environ if environ is not None else os.environ
    adapter_class = _load_adapter_class(adapter_path)
    metadata = _metadata_for(adapter_class)
    runtime_config = runtime_config or ProviderRuntimeConfig()
    missing = missing_required_env(metadata, env)
    if missing:
        return {
            "ok": False,
            "provider": metadata.name,
            "run_evidence": "not tested",
            "provider_candidate_evidence": metadata.evidence,
            "missing_env": list(missing),
            "message": "Required provider environment variables are missing; no external call was made.",
        }

    urls = _load_urls(fixture_path)
    _reject_local_only_urls(urls)
    adapter = adapter_class(environ=env, runtime_config=runtime_config)
    rows = [adapter.fetch(url) for url in urls]
    summary = summarize(rows)
    summary["cost_per_1k_requests_usd"] = cost_per_1k_requests(rows)
    summary["cost_per_1k_successful_pages_usd"] = cost_per_1k_successful_pages(rows)
    _write_rows(
        output,
        run_evidence=run_evidence,
        metadata=metadata,
        rows=rows,
        fixture_scope=fixture_scope,
        runtime_config=runtime_config,
    )
    return {
        "ok": True,
        "provider": metadata.name,
        "run_evidence": run_evidence,
        "provider_candidate_evidence": metadata.evidence,
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
    parser.add_argument("--run-evidence", choices=["measured", "estimated", "not tested"], default="measured")
    parser.add_argument("--fixture-scope", default="reviewed public URL fixture")
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
        run_evidence=args.run_evidence,
        fixture_scope=args.fixture_scope,
    )
    print(json.dumps(result, indent=2))
    if not result["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
