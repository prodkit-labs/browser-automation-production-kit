# Cost Per 1k Pages Report Template

Use this report to explain the cost model behind a production browser
automation workflow. It is a cost-control document, not a provider ranking.

Local/open-source execution should stay documented before paid provider options.

## Cost Inputs

| Input | Why it matters | How to reduce it |
|---|---|---|
| Successful pages | The denominator for cost per 1k pages | Improve selector coverage and fixture tests before live runs |
| Retries | Retried pages can multiply provider and browser costs | Set retry budgets and classify failures before retrying |
| Browser minutes | Local and managed browser runtimes are often time-based | Reuse contexts, reduce waits, block unused assets where appropriate |
| Proxy/API calls | Provider pricing may be call-based or usage-based | Cache stable pages and avoid re-fetching unchanged data |
| Artifact storage | HTML, screenshots, traces, and logs can accumulate | Retain full artifacts only for failures or sampled runs |
| Debugging time | Human investigation can dominate low-volume workflows | Preserve failure reasons and artifacts so debugging is faster |

## Raw Model Fields

| Field | Description |
|---|---|
| `scenario` | Local fixture, local browser, mock managed browser, or future provider-backed run |
| `evidence` | `measured`, `estimated`, or `not tested` |
| `successful_pages` | Count of pages that produced usable output |
| `attempted_pages` | `successful_pages + retries`; useful when providers bill attempts |
| `retries` | Retry attempts included in the cost model |
| `retry_rate` | `retries / successful_pages`; use `0` when no pages succeeded |
| `browser_minutes` | Browser runtime minutes included in the model |
| `provider_calls` | Proxy/API/provider calls included in the model |
| `artifact_storage_mb` | Stored artifact volume in MB |
| `debugging_minutes` | Estimated human debugging time |
| `total_cost_usd` | Sum of modeled costs |
| `cost_per_1k_pages_usd` | `total_cost_usd / successful_pages * 1000` |

## Cost Summary

| Scenario | Evidence | Successful pages | Attempted pages | Retries | Retry rate | Browser minutes | Provider calls | Artifact MB | Debugging minutes | Total cost | Cost per 1k pages |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `<scenario>` | `<evidence>` | `<count>` | `<count>` | `<count>` | `<rate>` | `<minutes>` | `<count>` | `<mb>` | `<minutes>` | `<usd>` | `<usd>` |

## Formula

```text
attempted_pages = successful_pages + retries
retry_rate = retries / successful_pages

total_cost =
  browser_minutes * browser_minute_cost_usd
  + provider_calls * provider_call_cost_usd
  + artifact_storage_gb * artifact_storage_gb_month_cost_usd
  + debugging_hours * debugging_hour_cost_usd

cost_per_1k_pages = total_cost / successful_pages * 1000
```

## Cost Reduction Notes

Before choosing a provider, try to reduce spend with:

- Fixture coverage for parser and selector changes.
- Failure classification before retries.
- Smaller retry budgets for deterministic failures.
- Artifact retention rules that keep full artifacts for failures and samples.
- Stable page caching where terms and workflow requirements allow it.
- Browser wait tuning and resource limits.
- Separate benchmark runs for local fixtures, local browser, and provider-backed paths.

## Decision Notes

Write scenario-specific notes:

- Which cost input is growing fastest:
- Which failures are worth retrying:
- Which artifacts are worth keeping:
- Which local/open-source path remains enough:
- Which provider-backed path needs more benchmark evidence:
