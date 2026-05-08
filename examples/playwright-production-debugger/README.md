# Playwright Production Debugger

Runnable browser debugging workflow for the failure modes that usually appear after a script leaves local development.

It runs three local fixture pages:

- normal page
- selector drift page
- slow page that exceeds the navigation budget

Run:

```bash
python -m pip install -e '.[browser]'
python -m playwright install chromium
python -m prodkit_browser.jobs.playwright_production_debugger \
  --fixture benchmarks/fixtures/browser_debug_pages.json
```

Example output:

```json
{
  "checked": 3,
  "passed": 1,
  "failed": 2,
  "screenshots": 2,
  "failure_reasons": ["selector_drift", "timeout"],
  "artifact_dir": "artifacts/playwright-production-debugger",
  "benchmark_csv": "artifacts/playwright-production-debugger/benchmark.csv"
}
```

Outputs:

- `artifacts/playwright-production-debugger/html/`
- `artifacts/playwright-production-debugger/screenshots/`
- `artifacts/playwright-production-debugger/benchmark.csv`
- `artifacts/playwright-production-debugger/summary.json`

This example is fixture-first on purpose. Replace fixture URLs with external targets only after reviewing permissions, site/API terms, and rate limits.
