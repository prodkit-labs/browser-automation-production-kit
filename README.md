# Browser Automation Production Kit

A runnable Python/Crawlee starter for production web automation.

Most browser automation examples stop at "it works locally." Production jobs need artifacts, metrics, retries, provider boundaries, cost tracking, and compliance checks.

This kit helps you answer:

- Should this job run locally, through proxies, or through a managed browser API?
- What failed: selector drift, 403/429, timeout, retry budget, or provider issue?
- What are the success rate, p95 latency, artifact size, and estimated cost per 1k pages?
- When is self-hosting no longer worth it?

Current track:

- Local fixture runner
- Crawlee Python runner
- Ecommerce price monitor
- Artifact writer
- Benchmark CSV output
- Provider adapter interface
- Compliance-first runbooks

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m prodkit_browser.jobs.docs_to_rag --fixture benchmarks/fixtures/docs_pages.json
python -m prodkit_browser.jobs.ecommerce_price_monitor --fixture benchmarks/fixtures/ecommerce_pages.json
python -m benchmarks.scripts.run_local_benchmark
python -m benchmarks.scripts.run_provider_stub_benchmark
```

Outputs are written to `artifacts/` and `benchmarks/raw/`.

To run the Crawlee Python track against the same local fixture pages:

```bash
python -m pip install -e '.[crawlee]'
python -m prodkit_browser.jobs.crawlee_docs_to_rag --fixture benchmarks/fixtures/docs_pages.json
```

## What You Can Run Today

| Workflow | Command | Output |
| --- | --- | --- |
| Docs to RAG | `python -m prodkit_browser.jobs.docs_to_rag --fixture benchmarks/fixtures/docs_pages.json` | normalized records and HTML artifacts |
| Ecommerce price monitor | `python -m prodkit_browser.jobs.ecommerce_price_monitor --fixture benchmarks/fixtures/ecommerce_pages.json` | price-change events and selector drift report |
| Crawlee Python fixture run | `python -m prodkit_browser.jobs.crawlee_docs_to_rag --fixture benchmarks/fixtures/docs_pages.json` | Crawlee dataset plus normalized records |
| Local benchmark | `python -m benchmarks.scripts.run_local_benchmark` | raw CSV and summary metrics |
| Provider scaffold benchmark | `python -m benchmarks.scripts.run_provider_stub_benchmark` | provider-shaped raw CSV with evidence labels |

Example ecommerce output:

```json
{
  "checked": 3,
  "price_changes": 1,
  "selector_drift": 1,
  "artifact_dir": "artifacts/ecommerce-price-monitor"
}
```

Example provider scaffold output:

| Provider | Evidence | Success rate | p95 latency | Cost per 1k pages |
| --- | --- | ---: | ---: | ---: |
| local-fixture | measured | 1.0 | 0 ms | $0.00 |
| mock-managed-browser | estimated | 1.0 | 420 ms | $3.25 |
| mock-provider-with-throttle | estimated | 0.6667 | 650 ms | $5.50 |

The provider scaffold uses deterministic mock adapters. It is not a ranking and does not recommend a vendor.

## First Track

The first implementation track is `crawlee-python`. The local fixture mode keeps examples runnable without paid credentials, and the Crawlee track runs against the same fixture through a local HTTP server.

See:

- [Crawlee Python track](docs/crawlee-python-track.md)
- [Provider adapters](docs/provider-adapters.md)
- [Compliance boundaries](docs/compliance-boundaries.md)

## Included Examples

- `examples/docs-to-rag`: crawl public documentation-style pages and emit normalized records.
- `examples/ecommerce-price-monitor`: monitor fixture product pages, emit price changes, and report selector drift.
- `examples/serp-monitor`: planned SERP-style monitoring workflow with extra compliance boundaries.

## Production Decision Map

| Mode | Best for | Warning signs | Metrics to watch | When to upgrade |
| --- | --- | --- | --- | --- |
| Local HTTP / fixture | parser development | not real-world enough | parse accuracy, bytes out | before external tests |
| Local browser | small scheduled jobs | crashes, timeouts | p95 latency, retry rate | when maintenance grows |
| Proxy-backed browser | region/session testing | 403/429 spikes | block rate, retry cost | when ops cost grows |
| Managed browser API | reliability-sensitive workflows | provider cost | success rate, p95, cost per 1k pages | when reliability matters |
| Scraping API | commodity extraction | less control | success rate, latency | when speed matters |
| SERP API | search result monitoring | terms review needed | quota, cost, freshness | when SERP is core data |

## Production Guides

- [Deployment](production/deployment.md)
- [Observability](production/observability.md)
- [Cost control](production/cost-control.md)
- [Provider comparison](production/provider-comparison.md)
- [Disclosure policy](production/disclosure.md)

## Non-Goals

This repo is not for credential harvesting, account automation, social platform abuse, bypassing protected accounts, or claiming that any provider guarantees lawful access to third-party data.

Review [compliance boundaries](docs/compliance-boundaries.md) before adapting the examples.

## License

MIT
