# Observability

Browser automation jobs need enough telemetry to explain what failed and what it cost.

Track:

| Metric | Why it matters | Example field |
|---|---|---|
| Run count | Confirms schedule volume and benchmark sample size | `runs` |
| Success rate | Shows whether the workflow is production-stable | `success_rate` |
| p95 latency | Catches slow tails before averages hide them | `p95_latency_ms` |
| Retry rate | Shows whether retries are masking root causes | `retry_rate` |
| Block or throttle rate | Separates target/provider pressure from code bugs | `block_rate`, `provider_throttle_rate` |
| Bytes written | Helps estimate transfer and artifact size | `bytes_out` |
| Artifact storage volume | Drives retention and storage cost decisions | `artifact_storage_mb` |
| Provider and region metadata | Explains provider-specific behavior | `provider`, `region`, `session_used` |

Save failure artifacts:

- HTML snapshot
- screenshot when a browser is used
- request metadata
- error message
- retry count

## Failure Classes

| Class | Meaning | Retry? | Artifact |
|---|---|---|---|
| `selector_drift` | Expected selector is missing or no longer returns parseable content | no | HTML + screenshot |
| `timeout` | Navigation, response, or selector wait exceeded the budget | limited | HTML + screenshot |
| `network_error` | Request failed before a usable response was available | yes, limited | request metadata |
| `provider_throttle` | Provider quota, rate, or usage limit blocked the run | no immediate retry | provider metadata |
| `parse_error` | Page loaded but parsing rules did not produce expected data | no | HTML + normalized error |
| `cost_budget_exceeded` | Run would exceed the configured cost budget | no | cost summary |

## Artifact Retention

| Artifact | Keep for successes | Keep for failures | Notes |
|---|---:|---:|---|
| HTML | sampled | yes | Needed for selector and parser debugging |
| Screenshot | sampled browser runs | yes | Useful when layout or consent banners matter |
| Trace/video | no by default | selected failures | Can grow quickly; retain only when debugging |
| Raw CSV | yes | yes | Required for reproducible benchmark claims |
| Summary JSON | yes | yes | Small, useful for dashboards and release notes |

## Alert Examples

- Success rate drops below the release baseline.
- p95 latency exceeds the configured browser timeout budget.
- `selector_drift` appears in two consecutive scheduled runs.
- `provider_throttle` appears after a provider plan or quota change.
- Artifact storage growth exceeds the retention budget.
- Cost per 1k successful pages rises faster than cost per 1k requests.

## Dashboard Fields

```json
{
  "workflow": "playwright-production-debugger",
  "provider": "local-playwright",
  "success_rate": 0.75,
  "p95_latency_ms": 2400.0,
  "failure_classes": {
    "selector_drift": 1,
    "network_error": 1
  },
  "artifact_storage_mb": 12.5,
  "cost_per_1k_successful_pages_usd": 0.0
}
```
