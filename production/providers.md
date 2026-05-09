# Production Provider Options

This page maps production browser automation problems to provider categories.
It is a decision aid, not a provider ranking.

> Disclosure: Some provider links on production decision pages may be affiliate
> links. If you sign up through them, ProdKit Labs may earn a commission at no
> extra cost to you. Provider placement should be based on workflow fit,
> documented tradeoffs, and benchmark evidence where available.

## When Local Execution Is Enough

Use local execution when:

- fixtures are enough for parser development
- traffic volume is low
- failures are easy to debug
- no region or session requirements exist
- browser worker maintenance is still cheaper than provider usage

The local and mock paths in this repo should stay runnable without paid
services.

## When To Consider A Provider

Consider a provider when:

- retry rate keeps rising
- p95 latency is unstable
- browser workers require too much maintenance
- screenshots, HTML, traces, or logs need retention
- region or session requirements matter
- provider cost is lower than operational cost

## Provider Categories

| Category | Useful for | Example providers | Evidence status | Tradeoffs to document |
|---|---|---|---|---|
| Hosted Crawlee / automation platform | Crawlee workflows, scheduling, datasets, hosted runs | Apify | not tested | platform runtime boundaries, storage model, workflow portability |
| Managed browser API | Playwright or Puppeteer workflows that need hosted browser runtime | Browserbase, Browserless, Scrapfly | not tested | provider cost, browser versions, trace/session support, runtime limits |
| Scraping API | API-first public page extraction and commodity extraction | ScraperAPI, ScrapingBee, ZenRows | not tested | less browser-level control, API limits, retry behavior, rendering support |
| Proxy / data infrastructure | region/session testing, proxy-backed browser jobs, high-volume public data | Decodo, Bright Data, Oxylabs | not tested | terms review, operational complexity, cost, block-rate measurement |
| Deployment platform | self-hosted workers, scheduled jobs, internal tools | Railway, DigitalOcean | not tested | browser dependencies, worker resources, job scheduling, artifact storage |

## Evaluation Fields

Each public provider evaluation should record:

- fixture scope
- setup steps
- credential handling
- adapter metadata and capabilities
- rate limits
- success rate
- p95 latency
- cost per 1k pages
- artifact support
- failure classification
- raw CSV path
- evidence label: `measured`, `estimated`, or `not tested`
- disclosure status for public provider links

External provider benchmarks must be opt-in. They should run only when the
adapter path is passed explicitly and required provider environment variables
are present.

## Link Policy

- Do not place provider links in README hero sections or install commands.
- Do not rank providers without comparable benchmark data.
- Do not use "best provider" language.
- Put public links near scenario-specific production decisions.
- Keep nearby disclosure on every public page that contains affiliate links.
