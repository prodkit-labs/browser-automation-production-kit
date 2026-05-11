# Provider Boundary Review Checklist

Use this checklist before moving a browser automation workflow from the local
or fixture path to a proxy-backed, scraping API, managed browser, hosted
automation, or deployment provider path.

This checklist is vendor-neutral. It does not replace legal, security, or
compliance review.

## 1. Workload Scope

- [ ] Workflow is named and documented.
- [ ] Target page types are public and allowed for the intended use.
- [ ] Private, account-gated, sensitive, or protected pages are out of scope.
- [ ] JavaScript rendering requirement is documented.
- [ ] Region, session, login, or proxy requirements are documented.
- [ ] Expected page volume and schedule are documented.

## 2. Local/Open-Source Baseline

- [ ] Local fixture path runs without paid services.
- [ ] Local browser path is tested when browser behavior matters.
- [ ] Failure classes are recorded before provider testing.
- [ ] Artifact policy is documented.
- [ ] Cost assumption worksheet is filled before provider comparison.

Useful references:

- [`reports/cost-assumption-worksheet.md`](../reports/cost-assumption-worksheet.md)
- [`production/ecommerce-price-monitor-decision.md`](ecommerce-price-monitor-decision.md)

## 3. Provider Evidence

- [ ] Provider path has an evidence label: `measured`, `estimated`, or `not tested`.
- [ ] `measured_at` is recorded for measured rows.
- [ ] Fixture scope is documented.
- [ ] Raw CSV or report output is reproducible.
- [ ] Attempted pages and successful pages are separate.
- [ ] Retry rate is recorded.
- [ ] p95 latency is recorded.
- [ ] Cost per 1k successful pages is recorded.
- [ ] Artifact support is recorded.
- [ ] Failure classification is recorded.

## 4. Credentials And Secrets

- [ ] Required environment variable names are documented without values.
- [ ] No credentials are committed to the repo.
- [ ] External provider benchmarks require explicit adapter import paths.
- [ ] Local-only `example.test` fixtures are not sent to external providers.
- [ ] Timeout and retry settings are documented.
- [ ] Region and session settings are documented when used.

## 5. Cost And Retry Boundary

- [ ] Provider billing unit is understood: request, credit, browser minute,
  session, bandwidth, or other unit.
- [ ] Retries are counted as attempted pages when they can affect billing.
- [ ] Retry budget is capped.
- [ ] Deterministic selector drift is not blindly retried.
- [ ] Artifact storage and retention cost is estimated.
- [ ] Debugging time is considered when comparing local vs provider paths.

## 6. Disclosure And Links

- [ ] Public provider links appear only in scenario-specific production decision
  context.
- [ ] Nearby disclosure is present before any commercial provider link.
- [ ] The open-source path remains documented.
- [ ] Provider rows include tradeoffs, not only benefits.
- [ ] No provider is described as universally best.
- [ ] No ranking is published without comparable benchmark evidence.
- [ ] Private affiliate registry details are not copied into public docs.

## 7. Final Decision Record

| Field | Value |
|---|---|
| Workflow |  |
| Provider path under review |  |
| Local baseline result |  |
| Evidence status |  |
| Measured at |  |
| Fixture scope |  |
| Attempted pages |  |
| Successful pages |  |
| Retry rate |  |
| p95 latency |  |
| Cost per 1k successful pages |  |
| Main tradeoff |  |
| Open-source path still documented? |  |
| Disclosure needed? |  |
| Decision |  |
