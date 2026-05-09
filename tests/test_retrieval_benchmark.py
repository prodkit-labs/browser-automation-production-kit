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


ROOT = Path(__file__).resolve().parents[1]


def test_local_retrieval_benchmark_finds_expected_sources(tmp_path) -> None:
    records = docs_to_rag.run(ROOT / "benchmarks/fixtures/docs_pages.json", tmp_path)
    chunks = chunks_from_records(records)
    queries = load_queries(ROOT / "benchmarks/fixtures/retrieval_queries.json")

    results = run_retrieval_benchmark(queries, chunks, top_k=3)
    summary = query_summary(results)

    assert summary == {
        "install-worker": True,
        "production-metrics": True,
        "failure-artifacts": True,
    }
    assert {result.rank for result in results} == {1, 2, 3}
    assert all(result.score >= 0 for result in results)


def test_retrieval_benchmark_writes_raw_csv_and_report(tmp_path) -> None:
    records = docs_to_rag.run(ROOT / "benchmarks/fixtures/docs_pages.json", tmp_path / "artifacts")
    chunks = chunks_from_records(records)
    queries = load_queries(ROOT / "benchmarks/fixtures/retrieval_queries.json")
    results = run_retrieval_benchmark(queries, chunks, top_k=2)
    raw_csv = tmp_path / "raw/retrieval_benchmark.csv"
    report_path = tmp_path / "reports/retrieval-benchmark.md"

    write_raw_results(raw_csv, results)
    report = write_report(raw_csv, report_path, results)

    raw_text = raw_csv.read_text(encoding="utf-8")
    assert "query_id,query,expected_source_url,returned_source_url" in raw_text
    assert "install-worker" in raw_text
    assert "Retrieval Benchmark Report" in report
    assert "Hit rate: 100.00%" in report
    assert report_path.exists()
