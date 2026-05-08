# Provider Adapters

Provider adapters keep job logic separate from infrastructure choices.

Every adapter should return:

- provider name
- URL or fixture id
- success/failure
- latency
- status code
- bytes out
- artifact path when available
- cost estimate when available
- error message when failed

Every adapter should also expose metadata:

- provider name
- provider category
- execution mode
- evidence label: `measured`, `estimated`, or `not tested`
- required environment variables
- optional environment variables
- capability flags for JavaScript rendering, screenshots, HTML artifacts,
  proxy regions, and sessions

Initial categories:

- local fixture adapter
- mock managed provider adapter for benchmark scaffolding
- local browser adapter
- proxy-backed browser adapter
- managed browser or scraping API adapter

Provider-specific credentials must come from environment variables, not source files.

External provider adapters should inherit from `ExternalProviderAdapterBase` so
required credentials are validated before a run starts:

```python
from prodkit_browser.adapters.provider import (
    ExternalProviderAdapterBase,
    FetchResult,
    ProviderAdapterMetadata,
    ProviderCapabilities,
)


class ExampleManagedBrowserAdapter(ExternalProviderAdapterBase):
    metadata = ProviderAdapterMetadata(
        name="example-managed-browser",
        category="managed browser API",
        execution_mode="hosted Playwright/browser runtime",
        evidence="not tested",
        required_env=("EXAMPLE_BROWSER_API_KEY",),
    )
    capabilities = ProviderCapabilities(
        javascript_rendering=True,
        screenshots=True,
        html_artifacts=True,
        sessions=True,
        artifact_types=("html", "screenshot"),
    )

    def fetch(self, url: str) -> FetchResult:
        raise NotImplementedError
```

Run the provider-shaped benchmark scaffold:

```bash
python -m benchmarks.scripts.run_provider_stub_benchmark
```

Generate the provider benchmark planning template:

```bash
python -m benchmarks.scripts.generate_provider_benchmark_template
```

The mock adapters are not provider recommendations. They exist so the CSV format, evidence labels, and reporting workflow can be tested before adding real external integrations.
