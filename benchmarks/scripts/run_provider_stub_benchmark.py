from __future__ import annotations

import csv
import json
from pathlib import Path

from prodkit_browser.adapters.provider import LocalFixtureAdapter, MockManagedProviderAdapter
from prodkit_browser.metrics import cost_per_1k_requests, cost_per_1k_successful_pages, summarize


def _load_pages() -> dict[str, str]:
    fixture = json.loads(Path("benchmarks/fixtures/docs_pages.json").read_text(encoding="utf-8"))
    return {page["url"]: page["html"] for page in fixture["pages"]}


def main() -> None:
    pages = _load_pages()
    urls = list(pages)
    providers = [
        ("measured", LocalFixtureAdapter(pages)),
        ("estimated", MockManagedProviderAdapter("mock-managed-browser", pages, 420, 3.25)),
        (
            "estimated",
            MockManagedProviderAdapter(
                "mock-provider-with-throttle",
                pages,
                650,
                5.50,
                fail_urls={urls[-1]},
            ),
        ),
    ]

    raw_dir = Path("benchmarks/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    output = raw_dir / "provider_stub_results.csv"

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
        summaries = {}
        for evidence, adapter in providers:
            rows = [adapter.fetch(url) for url in urls]
            summary = summarize(rows)
            summary["cost_per_1k_requests_usd"] = cost_per_1k_requests(rows)
            summary["cost_per_1k_successful_pages_usd"] = cost_per_1k_successful_pages(rows)
            summaries[adapter.name] = {"evidence": evidence, "summary": summary}
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

    print(json.dumps({"providers": summaries, "raw_csv": str(output)}, indent=2))


if __name__ == "__main__":
    main()
