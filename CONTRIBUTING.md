# Contributing

Contributions should keep the repo useful before it becomes commercial.

Guidelines:

- Keep local/mock execution working without paid services.
- Do not add provider credentials, secrets, or private endpoints.
- Add raw benchmark data generation before adding comparison claims.
- Use scenario-specific provider language, not "best provider" claims.
- Keep compliance boundaries visible in scraping and browser automation examples.

Run before opening a pull request:

```bash
python -m pip install -e '.[dev,crawlee,browser]'
python -m playwright install chromium
python -m ruff check .
python -m pytest
python -m prodkit_browser.jobs.playwright_selector_drift --fixture benchmarks/fixtures/ecommerce_pages.json
python -m prodkit_browser.jobs.playwright_production_debugger --fixture benchmarks/fixtures/browser_debug_pages.json
python -m benchmarks.scripts.run_local_benchmark
python -m benchmarks.scripts.run_provider_stub_benchmark
```
