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

How this track fits:

- Keep the provider and benchmark boundary independent.
- Reuse the same artifact writer and metric summary format.
- Use Playwright/browser execution only where a page requires browser runtime.
- Add provider-backed adapters only after local and Crawlee fixture runs are stable.

The local fixture adapter exists so examples and benchmarks remain runnable without paid credentials.
