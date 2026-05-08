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

Crawlee fixture run:

```bash
python -m pip install -e '.[crawlee]'
python -m prodkit_browser.jobs.crawlee_docs_to_rag --fixture benchmarks/fixtures/docs_pages.json
```

Tracked metrics:

- `success_rate`
- `p95_latency_ms`
- `cost_per_1k_pages`
- `captcha_or_block_rate`
- `retry_rate`
- `bytes_out`
- `artifact_storage_mb`

Provider comparison pages should label every number as `measured`, `estimated`, or `not tested`.
