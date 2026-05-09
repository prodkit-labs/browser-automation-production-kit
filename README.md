# Browser Automation Production Kit

[![Benchmark](https://github.com/prodkit-labs/browser-automation-production-kit/actions/workflows/benchmark.yml/badge.svg)](https://github.com/prodkit-labs/browser-automation-production-kit/actions/workflows/benchmark.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Ruff](https://img.shields.io/badge/lint-ruff-46a2f1)

A Python/Crawlee/Playwright starter for turning browser automation scripts into production jobs.

Most examples stop at "it works locally." This repo focuses on what breaks next: artifacts, retries, selector drift, metrics, provider handoffs, cost tracking, and compliance boundaries.

Current release: [v0.1.0](https://github.com/prodkit-labs/browser-automation-production-kit/releases/tag/v0.1.0) - fixture-first browser automation workflows with Playwright, Crawlee, artifacts, and benchmarks.

This kit helps you answer:

- What failed: selector drift, 403/429, timeout, retry budget, or provider issue?
- Should this job run locally, with Playwright, through proxies, or with a managed browser API?
- What are the success rate, p95 latency, artifact size, and cost per 1k pages?
- When is self-hosting no longer worth it?

Ships today:

- Local fixture runner
- Crawlee Python fixture runner
- Playwright production debugger
- Playwright selector drift demo
- E-commerce price monitor
- Docs-to-RAG crawler
- Artifact writer
- Benchmark CSV output
- Provider comparison scaffold
- Compliance-first runbooks

## Quickstart

Recommended first run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[browser]'
python -m playwright install chromium
python -m prodkit_browser.jobs.playwright_production_debugger \
  --fixture benchmarks/fixtures/browser_debug_pages.json
```

Outputs are written to `artifacts/playwright-production-debugger/`.

For lightweight fixture-only runs:

```bash
python -m pip install -e .
python -m prodkit_browser.jobs.docs_to_rag --fixture benchmarks/fixtures/docs_pages.json
python -m prodkit_browser.jobs.ecommerce_price_monitor --fixture benchmarks/fixtures/ecommerce_pages.json
python -m benchmarks.scripts.run_local_benchmark
python -m benchmarks.scripts.run_provider_stub_benchmark
python -m benchmarks.scripts.generate_provider_benchmark_template
python -m benchmarks.scripts.generate_provider_evaluation_report
```

Outputs are written to `artifacts/` and `benchmarks/raw/`.

To run the Crawlee Python track against the same local fixture pages:

```bash
python -m pip install -e '.[crawlee]'
python -m prodkit_browser.jobs.crawlee_docs_to_rag --fixture benchmarks/fixtures/docs_pages.json
```

To run the Playwright selector drift demo:

```bash
python -m pip install -e '.[browser]'
python -m playwright install chromium
python -m prodkit_browser.jobs.playwright_selector_drift --fixture benchmarks/fixtures/ecommerce_pages.json
```

## What You Can Run Today

| Workflow | Command | Output |
|---|---|---|
| Docs to RAG | `python -m prodkit_browser.jobs.docs_to_rag --fixture benchmarks/fixtures/docs_pages.json` | Normalized records and HTML artifacts |
| E-commerce price monitor | `python -m prodkit_browser.jobs.ecommerce_price_monitor --fixture benchmarks/fixtures/ecommerce_pages.json` | Price-change events and selector drift report |
| Playwright production debugger | `python -m prodkit_browser.jobs.playwright_production_debugger --fixture benchmarks/fixtures/browser_debug_pages.json` | Screenshot artifacts, failure reasons, and benchmark CSV |
| Playwright selector drift | `python -m prodkit_browser.jobs.playwright_selector_drift --fixture benchmarks/fixtures/ecommerce_pages.json` | Screenshots, HTML, metrics, and drift report |
| Crawlee Python fixture run | `python -m prodkit_browser.jobs.crawlee_docs_to_rag --fixture benchmarks/fixtures/docs_pages.json` | Crawlee dataset plus normalized records |
| Local benchmark | `python -m benchmarks.scripts.run_local_benchmark` | Raw CSV and summary metrics |
| Provider scaffold benchmark | `python -m benchmarks.scripts.run_provider_stub_benchmark` | Provider comparison scaffold with evidence labels |
| Provider benchmark template | `python -m benchmarks.scripts.generate_provider_benchmark_template` | Candidate provider rows without affiliate URLs |
| Provider evaluation report | `python -m benchmarks.scripts.generate_provider_evaluation_report` | Markdown report from raw provider benchmark CSV |

Example ecommerce output:

```json
{
  "checked": 3,
  "price_changes": 1,
  "selector_drift": 1,
  "artifact_dir": "artifacts/ecommerce-price-monitor"
}
```

Provider comparison scaffold included. Real provider reports should be added only with benchmark evidence and disclosure.

## Artifact Preview

The Playwright debugger preserves the files you need when a browser job fails:

```text
artifacts/playwright-production-debugger/
  html/
    normal-product.html
    dropped-response-product.html
    selector-drift-product.html
    slow-product.html
  screenshots/
    selector-drift-product.png
    slow-product.png
  benchmark.csv
  summary.json
```

Example failure summary:

```json
{
  "checked": 4,
  "passed": 1,
  "failed": 3,
  "screenshots": 3,
  "failure_reasons": ["network_error", "selector_drift", "timeout"]
}
```

## Architecture

The kit starts with deterministic local fixtures so every workflow can run without paid credentials.

Browser, Crawlee, and provider-backed tracks share the same shape: clear inputs, saved artifacts, structured metrics, and explicit compliance boundaries.

### Tracks

- Local fixture track
- [Crawlee Python track](docs/crawlee-python-track.md)
- Playwright browser track
- [Provider adapters](docs/provider-adapters.md)
- [Compliance boundaries](docs/compliance-boundaries.md)

## Included Examples

- `examples/docs-to-rag`: crawl public documentation-style pages and emit normalized records.
- `examples/ecommerce-price-monitor`: monitor fixture product pages, emit price changes, and report selector drift.
- `examples/playwright-production-debugger`: run normal, selector drift, timeout, and network error pages through Chromium and preserve debugging artifacts.
- `examples/playwright-selector-drift`: open fixture pages in Chromium, capture screenshots on selector drift, and report browser-run metrics.
- `examples/serp-monitor`: planned SERP-style monitoring workflow with extra compliance boundaries.

## Production Decision Map

| Mode | Best for | Warning signs | Metrics to watch | When to upgrade |
|---|---|---|---|---|
| Local HTTP / fixture | Parser development | Not real-world enough | Parse accuracy, bytes out | Before external tests |
| Local browser | Small scheduled jobs | Crashes, timeouts | p95 latency, retry rate | When maintenance grows |
| Proxy-backed browser | Region/session testing | 403/429 spikes | Block rate, retry cost | When ops cost grows |
| Managed browser API | Reliability-sensitive workflows | Provider cost | Success rate, p95, cost per 1k pages | When reliability matters |
| Scraping API | Commodity extraction | Less control | Success rate, latency | When speed matters |
| SERP API | Search result monitoring | Review site/API terms first | Quota, cost, freshness | When SERP is core data |

## Production Guides

- [Deployment](production/deployment.md)
- [Observability](production/observability.md)
- [Cost control](production/cost-control.md)
- [Provider options](production/providers.md)
- [Provider comparison](production/provider-comparison.md)
- [Provider evaluation report template](reports/provider-evaluation-report-template.md)
- [Disclosure policy](production/disclosure.md)

## Non-Goals

This repo is not for credential harvesting, account automation, social platform abuse, bypassing protected accounts, or claiming that any provider guarantees lawful access to third-party data.

Review [compliance boundaries](docs/compliance-boundaries.md) before adapting the examples.

## License

MIT
