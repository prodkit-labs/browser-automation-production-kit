# Deployment

The first production path is a scheduled worker that runs local fixtures, local
browser jobs, or reviewed provider-backed jobs with retained artifacts and raw
benchmark output.

Use this guide to decide where the worker should run and what operational
surface must exist before a browser job becomes production traffic.

## Deployment Modes

| Mode | Good fit | Watch | Evidence to keep |
|---|---|---|---|
| Self-hosted worker | Small scheduled jobs, internal workflows, low-volume public pages | Browser dependencies, disk growth, retries, host restarts | run logs, raw CSV, failure artifacts |
| Lightweight PaaS worker | Teams that want managed runtime and simple scheduled jobs | browser install size, job timeout, ephemeral disk, artifact export | build logs, schedule logs, artifact destination |
| Hosted automation platform | Crawlee-style workflows, hosted scheduling, datasets | platform runtime boundaries, storage model, workflow portability | raw benchmark CSV, cost model, artifact links |
| Managed browser API | Playwright/Puppeteer jobs that need hosted browsers, concurrency, traces, or sessions | cost, provider limits, runtime differences, retention policy | success rate, p95 latency, cost per 1k successful pages, failure classes |

Do not choose a paid provider only because it is available. Move when the raw
evidence shows that reliability, latency, region/session requirements, or
maintenance cost are no longer acceptable locally.

## Self-Hosted Worker Path

Start here when local execution is still cheap to operate.

Minimum setup:

- Install Python dependencies from the selected extra, such as `.[browser]` or `.[crawlee]`.
- Install browser dependencies if the job uses Playwright.
- Run one command per scheduled workflow.
- Persist `artifacts/` or redirect `ARTIFACT_DIR` to durable storage.
- Save raw benchmark CSV from `benchmarks/raw/`.
- Retain logs for every scheduled run.
- Alert on non-zero exit codes, rising retry rate, and missing artifacts.

Example local browser worker command:

```bash
python -m prodkit_browser.jobs.playwright_production_debugger \
  --fixture benchmarks/fixtures/browser_debug_pages.json
```

Example fixture-only worker command:

```bash
python -m prodkit_browser.jobs.ecommerce_price_monitor \
  --fixture benchmarks/fixtures/ecommerce_pages.json
```

## Lightweight PaaS Path

A lightweight PaaS can be enough when a team wants managed scheduling without
rewriting the job around a provider API.

Review these constraints before choosing this path:

- Can the platform install browser system dependencies?
- Does the scheduled job timeout exceed the worst expected run?
- Is disk ephemeral, and where will artifacts be exported?
- Are logs retained long enough to debug a delayed failure?
- Can secrets be scoped to this worker only?
- Can the job be retried manually with the same environment?

Keep the deployment generic unless a platform-specific guide has measured setup
notes, cost inputs, and retention behavior.

## Artifact Retention

Failure artifacts are the debugging surface for browser automation.

Keep:

- HTML snapshots for failed pages.
- Screenshots for browser-backed failures.
- Request metadata and status codes.
- Error class, retry count, and timeout settings.
- Raw benchmark CSV for the run.
- A generated cost report when provider-backed paths are evaluated.

Suggested retention policy:

| Artifact | Retention | Notes |
|---|---:|---|
| Failure HTML | 30 days | Keep longer for recurring failures |
| Failure screenshots | 30 days | Sample if volume grows quickly |
| Raw benchmark CSV | 90 days | Needed for trend and cost review |
| Successful artifacts | 7 days or sampled | Avoid storing every success forever |
| Logs | 30 days | Keep enough context to map failures to artifacts |

Do not store secrets, raw credentials, private account data, or protected-page
content in artifacts.

## Log Handling

Logs should explain what happened without exposing sensitive values.

Record:

- workflow name
- run id
- fixture or target set name
- provider name or `local`
- evidence label
- retry count
- failure class
- artifact path
- cost-model input path

Avoid:

- credential values
- full proxy URLs with credentials
- private cookies
- protected account content
- provider dashboard tokens

## Environment Variables

Use `.env.example` as the public shape of configuration, not as a secret store.

Rules:

- Store provider credentials in the deployment platform's secret manager.
- Scope credentials to the worker and environment that needs them.
- Pass environment variable names in docs, never values.
- Rotate credentials after test providers or sandboxes are retired.
- Keep local/mock mode runnable with no provider credentials.
- External provider benchmarks must stay opt-in and fail closed when required env vars are missing.

Public workflow files should not contain provider credentials. Repository
secrets should be introduced only after provider-backed benchmark scope and
disclosure language are reviewed.

## When To Move To Managed Browser APIs

Move from local browser workers to managed browser APIs only when at least one
of these is true:

- Browser dependency maintenance costs more than provider usage.
- Local browser crashes or timeouts are the main source of failed runs.
- The job needs concurrency beyond the host's practical capacity.
- Region or session requirements are part of the workflow.
- Screenshots, traces, or hosted debugging artifacts reduce investigation time.
- Cost per 1k successful pages is lower after retries and debugging time are included.

Before moving, generate:

```bash
python -m benchmarks.scripts.run_provider_stub_benchmark
python -m benchmarks.scripts.generate_provider_evaluation_report
python -m benchmarks.scripts.generate_cost_per_1k_report
```

Then review:

- [Provider options](providers.md)
- [Provider comparison](provider-comparison.md)
- [Cost control](cost-control.md)
- [Observability](observability.md)

## Production Checklist

- Environment variables configured from `.env.example`.
- Artifact directory or object storage configured.
- Scheduled job runner selected.
- Logs retained.
- Failed runs preserve request metadata and HTML.
- Provider credentials scoped to the job.
- Raw benchmark CSV is retained.
- Cost per 1k successful pages is generated for provider-backed decisions.
- Compliance boundaries are reviewed before new target classes are added.
