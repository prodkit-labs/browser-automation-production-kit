# Docs To RAG Example

This example crawls documentation-style pages, extracts readable text, and writes normalized records for later ingestion.

Run:

```bash
python -m prodkit_browser.jobs.docs_to_rag --fixture benchmarks/fixtures/docs_pages.json
```

Run with Crawlee Python:

```bash
python -m pip install -e '.[crawlee]'
python -m prodkit_browser.jobs.crawlee_docs_to_rag --fixture benchmarks/fixtures/docs_pages.json
```

Outputs:

- `artifacts/html/`
- `artifacts/docs-to-rag/records.json`
- `artifacts/crawlee-docs-to-rag/records.json`
- `artifacts/crawlee-storage/`

Production notes:

- Start with public documentation pages you are allowed to crawl.
- Keep raw HTML snapshots for debugging.
- Track success rate, latency, retries, and bytes written.
- Move provider access behind adapters when local execution is not enough.
