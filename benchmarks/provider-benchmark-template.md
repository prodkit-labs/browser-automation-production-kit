# Provider Benchmark Template

This template turns provider evaluation into a benchmark plan before any paid
credentials, affiliate links, or public recommendations are added.

Generate the CSV:

```bash
python -m benchmarks.scripts.generate_provider_benchmark_template
```

The output is written to:

```text
benchmarks/raw/provider_benchmark_template.csv
```

## Evidence Rules

- `measured`: produced by a reproducible benchmark script in this repo.
- `estimated`: based on documented pricing or clearly stated assumptions.
- `not tested`: a candidate for evaluation, not a recommendation.

## Link Rules

- Candidate rows do not include affiliate URLs.
- Public links require nearby disclosure.
- Provider placement should follow workflow fit, benchmark evidence, and
  documented tradeoffs.
- Do not rank providers until comparable benchmark data exists.
- Keep the local and mock paths runnable without paid services.
- Provider adapters should expose metadata and capabilities before a real
  external call is added.
- Required credentials must be listed as environment variable names and
  validated at runtime, not stored in source files.

## Initial Candidate Categories

| Category | Candidate examples | Fixture scope |
|---|---|---|
| Baseline | `local-fixture`, `local-playwright` | Local docs, e-commerce, selector drift, and debugger fixtures |
| Hosted automation platform | Apify | Crawlee and docs-to-RAG workflows |
| Scraping API | ScraperAPI, ScrapingBee | E-commerce price monitor and future SERP-style monitor |
| Proxy / scraping API | Decodo | Region/session and e-commerce workflows |
| Enterprise web data infrastructure | Bright Data | High-volume public data workflows |
| Managed browser API | Browserbase, Browserless | Playwright production debugger |

ScraperAPI is included as a `Scraping API` candidate because it matches the
e-commerce and SERP-style paths. This is not a recommendation or ranking.
