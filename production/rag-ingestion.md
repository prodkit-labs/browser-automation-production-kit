# Local-First RAG Ingestion

Use this guide to run the docs-to-RAG path locally before adding hosted
embeddings, vector stores, or provider-backed browser execution.

The default path uses fixture pages and local files only. It is designed to make
parsing, chunking, retrieval checks, and cost inputs reproducible from a clean
checkout.

## Clean Checkout Run

Start with the fixture-only install:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Run the local docs-to-RAG ingestion job:

```bash
python -m prodkit_browser.jobs.docs_to_rag --fixture benchmarks/fixtures/docs_pages.json
```

This writes:

```text
artifacts/html/
artifacts/docs-to-rag/records.json
artifacts/docs-to-rag/chunks.jsonl
```

Run the local retrieval benchmark:

```bash
python -m benchmarks.scripts.run_retrieval_benchmark
```

This writes:

```text
benchmarks/raw/retrieval_benchmark.csv
benchmarks/reports/retrieval-benchmark.md
```

Run the ingestion success and cost-input report:

```bash
python -m benchmarks.scripts.generate_ingestion_success_report
```

This writes:

```text
benchmarks/raw/ingestion_success_cost.csv
benchmarks/reports/ingestion-success-cost.md
```

If you need crawler runtime behavior while keeping the same chunk shape, run the
Crawlee fixture path:

```bash
python -m pip install -e '.[crawlee]'
python -m prodkit_browser.jobs.crawlee_docs_to_rag --fixture benchmarks/fixtures/docs_pages.json
```

This writes:

```text
artifacts/crawlee-docs-to-rag/records.json
artifacts/crawlee-docs-to-rag/chunks.jsonl
artifacts/crawlee-docs-to-rag/chunk_metadata.json
artifacts/crawlee-storage/
```

## Pipeline Shape

```text
fixture pages
  -> normalized records
  -> shared-schema chunks
  -> retrieval benchmark
  -> ingestion success and cost-input report
  -> later adapters, only after local outputs are stable
```

The local runner and Crawlee runner both produce shared-schema chunks. Crawlee
adds request and storage details in a metadata sidecar instead of changing the
chunk schema.

## Reproducibility Rules

- Keep fixture pages under `benchmarks/fixtures/`.
- Keep normalized records and chunks deterministic.
- Keep raw benchmark rows under `benchmarks/raw/`.
- Keep generated Markdown reports under `benchmarks/reports/`.
- Label every benchmark row as `measured`, `estimated`, or `not tested`.
- Keep provider-backed rows as `not tested` until raw benchmark data exists.

## Artifact Retention

Keep these artifacts for local debugging:

- raw HTML from successful and failed fixture pages
- normalized records
- chunk JSONL
- Crawlee request metadata, when using the Crawlee runner
- raw benchmark CSV files
- generated reports used for production decisions

For larger runs, keep full artifacts for failures and sampled artifacts for
successful pages. Re-run the ingestion success report when page volume, retry
budget, or artifact retention changes.

## External Service Boundary

Hosted embeddings, vector stores, and provider-backed browser execution can be
added later behind adapters. Do not add them until the local pipeline can answer
these questions:

- Are fixture pages parsed into the expected records?
- Are chunks stable across repeated runs?
- Does the retrieval benchmark return expected sources?
- What is the local success rate?
- How many pages failed, and why?
- How much artifact storage does the run produce?
- Which future provider-backed rows still lack measured data?

When external services are added, keep the local path runnable without
credentials and keep raw assumptions in CSV before writing comparison notes.

## Readiness Checklist

- [ ] Local docs-to-RAG command runs from a clean checkout.
- [ ] `artifacts/docs-to-rag/chunks.jsonl` exists and follows the shared schema.
- [ ] Retrieval benchmark report is generated from local fixture queries.
- [ ] Ingestion success report includes pages attempted, succeeded, failed,
      chunks produced, runtime, bytes fetched, and artifact size.
- [ ] Crawlee runner is used only when crawler runtime behavior is needed.
- [ ] Provider-backed rows are labeled `not tested` until measured.
- [ ] External services are behind adapters and are not required for local use.
- [ ] Cost and success decisions link to raw CSV evidence.
