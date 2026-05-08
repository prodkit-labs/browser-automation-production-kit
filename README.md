# Browser Automation Production Kit

Production-ready patterns for browser automation and scraping workflows: workers, artifacts, metrics, benchmark data, provider boundaries, and runbooks.

This repo starts with a Python local track and is designed to grow into Crawlee Python, Playwright, Selenium, and managed browser/provider tracks without binding examples to one vendor.

## What This Helps You Do

- Run browser automation jobs with clear inputs, outputs, and artifacts.
- Measure success rate, latency, retry behavior, and cost-related signals.
- Compare local execution with provider-backed execution through adapters.
- Debug failures with saved HTML, screenshots, logs, and structured metadata.
- Move from self-hosted execution to managed providers without rewriting job logic.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m prodkit_browser.jobs.docs_to_rag --fixture benchmarks/fixtures/docs_pages.json
python -m benchmarks.scripts.run_local_benchmark
```

Outputs are written to `artifacts/` and `benchmarks/raw/`.

To run the Crawlee Python track against the same local fixture pages:

```bash
python -m pip install -e '.[crawlee]'
python -m prodkit_browser.jobs.crawlee_docs_to_rag --fixture benchmarks/fixtures/docs_pages.json
```

## First Track

The first implementation track is `crawlee-python`. The local fixture mode keeps examples runnable without paid credentials, and the Crawlee track runs against the same fixture through a local HTTP server.

See:

- [Crawlee Python track](docs/crawlee-python-track.md)
- [Provider adapters](docs/provider-adapters.md)
- [Compliance boundaries](docs/compliance-boundaries.md)

## Included Examples

- `examples/docs-to-rag`: crawl public documentation-style pages and emit normalized records.
- `examples/ecommerce-price-monitor`: planned price monitoring workflow with selector drift notes.
- `examples/serp-monitor`: planned SERP-style monitoring workflow with extra compliance boundaries.

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
