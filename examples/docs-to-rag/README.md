# Docs To RAG Example

This example crawls documentation-style pages, extracts readable text, and writes normalized records plus deterministic document chunks for later retrieval work.

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
- `artifacts/docs-to-rag/chunks.jsonl`
- `artifacts/crawlee-docs-to-rag/records.json`
- `artifacts/crawlee-storage/`

Production notes:

- Start with public documentation pages you are allowed to crawl.
- Keep raw HTML snapshots for debugging.
- Keep chunk output deterministic before adding embeddings or vector stores.
- Track success rate, latency, retries, and bytes written.
- Move provider access behind adapters when local execution is not enough.

Schema:

- [`../../docs/docs-to-rag-chunk-schema.md`](../../docs/docs-to-rag-chunk-schema.md)
