# FAQ

## Is this tied to one provider?

No. Provider-specific code belongs behind adapters, and benchmarks should preserve raw data.

## Is Crawlee required?

No. The repo has three runnable paths:

- local fixture workflows
- Crawlee Python fixture workflows
- Playwright browser workflows

Crawlee is useful for crawler-style jobs that need request handling, datasets,
and worker patterns. Playwright is useful when a browser runtime is required.
Local fixture mode keeps examples runnable before provider or framework-specific
code is added.

## Where should commercial recommendations appear?

Only in production decision pages such as provider comparison, cost control, observability, and benchmark documentation.
