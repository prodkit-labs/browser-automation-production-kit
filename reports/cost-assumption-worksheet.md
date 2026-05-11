# Browser Automation Cost Assumption Worksheet

Use this worksheet before comparing local browser workers, proxy-backed browser
workers, scraping APIs, or managed browser providers.

It is a planning worksheet, not a provider ranking or billing guarantee. Replace
the example numbers with measured workload data whenever possible.

## Workflow

| Field | Value |
|---|---|
| Workflow name | `<e-commerce price monitor / docs crawl / SERP-style monitor / other>` |
| Data type | `<public product pages / public docs / public search results / other>` |
| JavaScript required | `<yes / no / mixed>` |
| Artifact policy | `<failures only / sampled successes / all pages>` |
| Retention period | `<days>` |
| Evidence status | `<measured / estimated / not tested>` |

## Volume And Retry Assumptions

| Input | Example | Your value | Notes |
|---|---:|---:|---|
| Successful pages | `1000` |  | Pages that produce usable output |
| Retries | `70` |  | Retry attempts after failures |
| Attempted pages | `1070` |  | `successful_pages + retries` |
| Retry rate | `0.0700` |  | `retries / successful_pages` |
| Runs per day | `1` |  | Scheduled runs or batches |
| Days per month | `30` |  | Use your billing window |

## Cost Inputs

| Input | Example | Your value | Notes |
|---|---:|---:|---|
| Browser minutes | `210` |  | Runtime minutes for the modeled run |
| Browser minute cost USD | `0.002` |  | Local infra or managed runtime cost |
| Provider/API calls | `1070` |  | Count attempted pages if billed per attempt |
| Provider/API call cost USD | `0.003` |  | Per call, request, credit, or equivalent unit |
| Artifact storage MB | `180` |  | HTML, screenshots, traces, logs |
| Artifact storage GB-month cost USD | `0.02` |  | Use storage provider pricing |
| Debugging minutes | `20` |  | Human review time for failures and drift |
| Debugging hour cost USD | `0` |  | Optional internal planning cost |
| Fixed monitoring cost USD | `0` |  | Alerts, uptime checks, logs, or dashboards |

## Formula

```text
attempted_pages = successful_pages + retries
retry_rate = retries / successful_pages
artifact_storage_gb = artifact_storage_mb / 1024
debugging_hours = debugging_minutes / 60

total_cost =
  browser_minutes * browser_minute_cost_usd
  + provider_calls * provider_call_cost_usd
  + artifact_storage_gb * artifact_storage_gb_month_cost_usd
  + debugging_hours * debugging_hour_cost_usd
  + fixed_monitoring_cost_usd

cost_per_1k_pages =
  total_cost / successful_pages * 1000
```

## Path Comparison

| Path | When it fits | Cost risks | Evidence needed before recommending |
|---|---|---|---|
| Local browser worker | Low to moderate volume with controllable targets | Host resources, retries, maintenance time | Local benchmark, artifact size, failure classes |
| Proxy-backed browser worker | Browser logic works locally but needs network routing | Proxy spend, block rate, retry growth | Block-rate test, retry budget, region behavior |
| Scraping API | Teams want API-first public page extraction | Request credits, rendering options, provider-specific behavior | Success rate, p95 latency, cost per successful page |
| Managed browser provider | Playwright/Puppeteer-heavy workflows need managed runtime | Browser minutes, sessions, artifacts, concurrency | Runtime cost, screenshots/traces, failure artifacts |

## Decision Notes

- What assumption is measured:
- What assumption is estimated:
- What is not tested yet:
- Which failures are worth retrying:
- Which artifacts are worth storing:
- Which path remains local/open-source:
- Which provider-backed path needs another benchmark:
