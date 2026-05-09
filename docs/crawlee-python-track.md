# Crawlee Python Track

Crawlee Python is one workflow track in this kit. It is useful for
crawler-style jobs that need request handling, datasets, and worker-style
execution.

Current implementation:

```bash
python -m pip install -e '.[crawlee]'
python -m prodkit_browser.jobs.crawlee_docs_to_rag --fixture benchmarks/fixtures/docs_pages.json
```

The Crawlee job:

- starts a local HTTP server from `benchmarks/fixtures/docs_pages.json`
- runs `BeautifulSoupCrawler` against fixture URLs
- stores Crawlee dataset output under `artifacts/crawlee-storage/`
- writes normalized records to `artifacts/crawlee-docs-to-rag/records.json`
- writes shared-schema chunks to `artifacts/crawlee-docs-to-rag/chunks.jsonl`
- writes crawl metadata to `artifacts/crawlee-docs-to-rag/chunk_metadata.json`

Use the local docs-to-RAG runner when you only need deterministic extraction
from known HTML fixtures. Use the Crawlee runner when you also want crawler
runtime behavior, request handling, dataset storage, and crawl metadata while
keeping the same chunk shape.

Chunk output uses the shared docs-to-RAG schema. Crawlee-specific details stay
in the metadata sidecar so downstream retrieval code can read the same chunk
fields from local and Crawlee runs.

Crawlee metadata includes:

- crawl run ID
- request URL served by the local fixture server
- response status
- Crawlee storage path
- discovered source URL from the original fixture page

How this track fits:

- Keep the provider and benchmark boundary independent.
- Reuse the same artifact writer and metric summary format.
- Use Playwright/browser execution only where a page requires browser runtime.
- Add provider-backed adapters only after local and Crawlee fixture runs are stable.

The local fixture adapter exists so examples and benchmarks remain runnable without paid credentials.
