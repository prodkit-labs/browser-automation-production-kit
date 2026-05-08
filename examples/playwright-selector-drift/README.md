# Playwright Selector Drift

Runnable browser example for catching selector drift and preserving failure artifacts.

Run:

```bash
python -m pip install -e '.[browser]'
python -m playwright install chromium
python -m prodkit_browser.jobs.playwright_selector_drift \
  --fixture benchmarks/fixtures/ecommerce_pages.json
```

Example output:

```json
{
  "checked": 3,
  "price_changes": 1,
  "selector_drift": 1,
  "screenshots": 1,
  "success_rate": 0.6667,
  "p95_latency_ms": 120.5,
  "artifact_dir": "artifacts/playwright-selector-drift"
}
```

Outputs:

- `artifacts/playwright-selector-drift/html/`
- `artifacts/playwright-selector-drift/screenshots/`
- `artifacts/playwright-selector-drift/price_events.json`
- `artifacts/playwright-selector-drift/selector_drift.json`
- `artifacts/playwright-selector-drift/summary.json`

This example uses local fixture pages. Replace fixtures with real URLs only after reviewing site terms, rate limits, and data permissions.
