# Ecommerce Price Monitor

Runnable fixture workflow for scheduled product page checks.

Run:

```bash
python -m prodkit_browser.jobs.ecommerce_price_monitor \
  --fixture benchmarks/fixtures/ecommerce_pages.json
```

Example output:

```json
{
  "checked": 3,
  "price_changes": 1,
  "selector_drift": 1,
  "artifact_dir": "artifacts/ecommerce-price-monitor"
}
```

Outputs:

- `artifacts/ecommerce-price-monitor/html/`
- `artifacts/ecommerce-price-monitor/price_events.json`
- `artifacts/ecommerce-price-monitor/selector_drift.json`
- `artifacts/ecommerce-price-monitor/summary.json`

Production requirements:

- selector drift detection
- screenshot and HTML artifact on failure
- retry budget
- price-change event output
- provider comparison only after benchmark evidence exists

Production decision note:

- [`production/ecommerce-price-monitor-decision.md`](../../production/ecommerce-price-monitor-decision.md)
