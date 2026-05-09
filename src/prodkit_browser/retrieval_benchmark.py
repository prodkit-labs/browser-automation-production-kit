from __future__ import annotations

import csv
from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Iterable

from prodkit_browser.rag_chunks import DocumentChunk


TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class RetrievalQuery:
    query_id: str
    query: str
    expected_source_url: str
    notes: str


@dataclass(frozen=True)
class RetrievalResult:
    query_id: str
    query: str
    expected_source_url: str
    returned_source_url: str
    returned_chunk_id: str
    rank: int
    hit: bool
    score: int
    expected_found: bool
    notes: str


def tokenize(text: str) -> set[str]:
    return set(TOKEN_RE.findall(text.lower()))


def load_queries(path: Path) -> list[RetrievalQuery]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [
        RetrievalQuery(
            query_id=str(row["id"]),
            query=str(row["query"]),
            expected_source_url=str(row["expected_source_url"]),
            notes=str(row.get("notes", "")),
        )
        for row in payload["queries"]
    ]


def score_chunk(query: str, chunk: DocumentChunk) -> int:
    query_tokens = tokenize(query)
    chunk_tokens = tokenize(" ".join([chunk.title, *chunk.heading_path, chunk.text]))
    return len(query_tokens & chunk_tokens)


def rank_chunks(query: RetrievalQuery, chunks: Iterable[DocumentChunk]) -> list[tuple[DocumentChunk, int]]:
    scored = [(chunk, score_chunk(query.query, chunk)) for chunk in chunks]
    return sorted(
        scored,
        key=lambda row: (-row[1], row[0].source_url, row[0].chunk_id),
    )


def run_retrieval_benchmark(
    queries: Iterable[RetrievalQuery],
    chunks: list[DocumentChunk],
    top_k: int = 3,
) -> list[RetrievalResult]:
    results: list[RetrievalResult] = []

    for query in queries:
        ranked = rank_chunks(query, chunks)[:top_k]
        expected_found = any(chunk.source_url == query.expected_source_url for chunk, _ in ranked)
        for rank, (chunk, score) in enumerate(ranked, start=1):
            results.append(
                RetrievalResult(
                    query_id=query.query_id,
                    query=query.query,
                    expected_source_url=query.expected_source_url,
                    returned_source_url=chunk.source_url,
                    returned_chunk_id=chunk.chunk_id,
                    rank=rank,
                    hit=chunk.source_url == query.expected_source_url,
                    score=score,
                    expected_found=expected_found,
                    notes=query.notes,
                )
            )

    return results


CSV_FIELDS = [
    "query_id",
    "query",
    "expected_source_url",
    "returned_source_url",
    "returned_chunk_id",
    "rank",
    "hit",
    "score",
    "expected_found",
    "notes",
]


def write_raw_results(path: Path, results: list[RetrievalResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "query_id": result.query_id,
                    "query": result.query,
                    "expected_source_url": result.expected_source_url,
                    "returned_source_url": result.returned_source_url,
                    "returned_chunk_id": result.returned_chunk_id,
                    "rank": result.rank,
                    "hit": result.hit,
                    "score": result.score,
                    "expected_found": result.expected_found,
                    "notes": result.notes,
                }
            )


def query_summary(results: list[RetrievalResult]) -> dict[str, bool]:
    summary: dict[str, bool] = {}
    for result in results:
        summary[result.query_id] = summary.get(result.query_id, False) or result.expected_found
    return summary


def render_report(raw_csv: Path, results: list[RetrievalResult]) -> str:
    summary = query_summary(results)
    total_queries = len(summary)
    hits = sum(1 for expected_found in summary.values() if expected_found)
    hit_rate = (hits / total_queries) if total_queries else 0
    failed_queries = [query_id for query_id, expected_found in summary.items() if not expected_found]

    top_rows = "\n".join(
        "| {query_id} | {rank} | {hit} | {score} | {source} |".format(
            query_id=result.query_id,
            rank=result.rank,
            hit="yes" if result.hit else "no",
            score=result.score,
            source=result.returned_source_url,
        )
        for result in results
        if result.rank == 1
    )
    failed = "\n".join(f"- `{query_id}`" for query_id in failed_queries) or "- None"

    return f"""# Retrieval Benchmark Report

This local benchmark scores docs-to-RAG chunks with deterministic token overlap.
It does not call hosted LLMs, embedding APIs, vector databases, or external
providers.

## Raw CSV

```text
{raw_csv}
```

## Summary

- Queries: {total_queries}
- Queries with expected source in top-k: {hits}
- Hit rate: {hit_rate:.2%}

## Top Result Per Query

| Query | Rank | Hit | Score | Returned source |
|---|---:|---|---:|---|
{top_rows}

## Missing Expected Sources

{failed}

## Notes

- This is a local fixture benchmark for retrieval plumbing and report shape.
- Scores are keyword/token overlap counts, not semantic relevance scores.
- Use the same query set when comparing future chunking or retrieval changes.
"""


def write_report(raw_csv: Path, output: Path, results: list[RetrievalResult]) -> str:
    report = render_report(raw_csv, results)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    return report
