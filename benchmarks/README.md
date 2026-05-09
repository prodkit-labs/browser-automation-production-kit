# Benchmarks

Benchmarks in this repo are generated from raw data, not hand-edited comparison tables.

Current local run:

```bash
python -m benchmarks.scripts.run_local_benchmark
```

Provider-shaped comparison scaffold:

```bash
python -m benchmarks.scripts.run_provider_stub_benchmark
```

This uses local and deterministic mock adapters only. It is for validating the comparison format before real provider credentials or external calls are introduced.

Provider benchmark planning template:

```bash
python -m benchmarks.scripts.generate_provider_benchmark_template
```

The template writes candidate provider rows to `benchmarks/raw/provider_benchmark_template.csv`.
Candidate rows are not recommendations and do not include affiliate URLs.

Provider evaluation report:

```bash
python -m benchmarks.scripts.generate_provider_evaluation_report
```

This turns raw provider benchmark CSV into a readable Markdown report. The
generated report is written to `benchmarks/reports/provider-evaluation-report.md`.
The tracked template lives at
[`../reports/provider-evaluation-report-template.md`](../reports/provider-evaluation-report-template.md).

Cost per 1k pages report:

```bash
python -m benchmarks.scripts.generate_cost_per_1k_report
```

This writes raw assumptions to `benchmarks/raw/cost_per_1k_pages.csv` and a
readable report to `benchmarks/reports/cost-per-1k-pages.md`.

Retrieval benchmark scaffold:

```bash
python -m benchmarks.scripts.run_retrieval_benchmark
```

This scores local docs-to-RAG chunks against fixture queries with deterministic
token overlap. It writes raw rows to `benchmarks/raw/retrieval_benchmark.csv`
and a report to `benchmarks/reports/retrieval-benchmark.md`. It does not call
hosted LLMs, embedding APIs, vector databases, or external providers.

Opt-in external provider benchmark harness:

```bash
python -m benchmarks.scripts.run_external_provider_benchmark \
  --adapter your_package.your_module:YourProviderAdapter \
  --fixture benchmarks/fixtures/external_provider_urls.example.json \
  --run-evidence measured
```

Run only provider adapters you trust. Adapter imports execute Python code in
your local environment before any benchmark calls are made.

The harness does not run by default in CI. It validates the adapter's required
environment variables before loading fixtures or making external calls. If
credentials are missing, it exits with a JSON error and writes no CSV.

Default `example.test` fixtures are local-only. External provider benchmarks
must use a reviewed public URL fixture, or an adapter that explicitly maps test
URLs to local fixture HTML without external calls. The example public URL
fixture is a placeholder shape; replace it before measuring a real provider.

External raw CSV separates:

- `run_evidence`: whether this benchmark run actually measured, estimated, or
  skipped the provider.
- `provider_candidate_evidence`: the provider row's default candidate status
  before this run.

Crawlee fixture run:

```bash
python -m pip install -e '.[crawlee]'
python -m prodkit_browser.jobs.crawlee_docs_to_rag --fixture benchmarks/fixtures/docs_pages.json
```

Tracked metrics:

- `success_rate`
- `p95_latency_ms`
- `cost_per_1k_requests`
- `cost_per_1k_successful_pages`
- `captcha_or_block_rate`
- `retry_rate`
- `bytes_out`
- `artifact_storage_mb`
- `retrieval_hit_rate`

Provider comparison pages should label every number as `measured`, `estimated`, or `not tested`.

Ingestion success and cost report:

```bash
python -m benchmarks.scripts.generate_ingestion_success_report
```

This runs the local docs-to-RAG fixture ingestion path, writes raw rows to
`benchmarks/raw/ingestion_success_cost.csv`, and writes a Markdown report to
`benchmarks/reports/ingestion-success-cost.md`. The report records pages
attempted, pages succeeded, pages failed, bytes fetched, chunks produced,
retries, runtime, and artifact size. Future provider-backed rows stay labeled
`not tested` until raw benchmark data exists.

Run the full local-first sequence in
[`../production/rag-ingestion.md`](../production/rag-ingestion.md).
