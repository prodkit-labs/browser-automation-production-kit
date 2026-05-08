# Crawlee Python Track

The first implementation track is Crawlee Python because it has strong fit for production scraping workflows and a clear bridge from local crawler logic to worker-style execution.

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

Next implementation steps:

1. Keep the provider and benchmark boundary independent.
2. Reuse the same artifact writer and metric summary format.
3. Add Playwright/browser execution only where a real page requires it.
4. Add provider-backed adapters after local and Crawlee fixture runs are stable.

The local fixture adapter exists so examples and benchmarks remain runnable without paid credentials.
