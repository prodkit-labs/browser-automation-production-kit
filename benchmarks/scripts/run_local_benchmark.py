from __future__ import annotations

import csv
import json
from pathlib import Path

from prodkit_browser.adapters.provider import LocalFixtureAdapter
from prodkit_browser.metrics import summarize


def main() -> None:
    fixture = json.loads(Path("benchmarks/fixtures/docs_pages.json").read_text(encoding="utf-8"))
    pages = {page["url"]: page["html"] for page in fixture["pages"]}
    adapter = LocalFixtureAdapter(pages)
    rows = [adapter.fetch(url) for url in pages]

    raw_dir = Path("benchmarks/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    output = raw_dir / "local_fixture_results.csv"

    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["provider", "url", "ok", "latency_ms", "status_code", "bytes_out", "cost_usd", "error"])
        for row in rows:
            writer.writerow([
                row.provider,
                row.url,
                row.ok,
                round(row.latency_ms, 2),
                row.status_code,
                row.bytes_out,
                row.cost_usd,
                row.error,
            ])

    print(json.dumps({"summary": summarize(rows), "raw_csv": str(output)}, indent=2))


if __name__ == "__main__":
    main()
