from __future__ import annotations

import argparse
import json
from pathlib import Path

from prodkit_browser.jobs import docs_to_rag
from prodkit_browser.rag_chunks import chunks_from_records
from prodkit_browser.retrieval_benchmark import (
    load_queries,
    query_summary,
    run_retrieval_benchmark,
    write_raw_results,
    write_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local retrieval benchmark for docs-to-RAG chunks.")
    parser.add_argument("--fixture", default="benchmarks/fixtures/docs_pages.json")
    parser.add_argument("--queries", default="benchmarks/fixtures/retrieval_queries.json")
    parser.add_argument("--artifact-dir", default="artifacts")
    parser.add_argument("--raw-csv", default="benchmarks/raw/retrieval_benchmark.csv")
    parser.add_argument("--report", default="benchmarks/reports/retrieval-benchmark.md")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    records = docs_to_rag.run(Path(args.fixture), Path(args.artifact_dir))
    chunks = chunks_from_records(records)
    queries = load_queries(Path(args.queries))
    results = run_retrieval_benchmark(queries, chunks, top_k=args.top_k)
    raw_csv = Path(args.raw_csv)
    report = Path(args.report)

    write_raw_results(raw_csv, results)
    write_report(raw_csv, report, results)

    summary = query_summary(results)
    hits = sum(1 for expected_found in summary.values() if expected_found)
    print(
        json.dumps(
            {
                "queries": len(summary),
                "hits": hits,
                "hit_rate": hits / len(summary) if summary else 0,
                "raw_csv": str(raw_csv),
                "report": str(report),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
