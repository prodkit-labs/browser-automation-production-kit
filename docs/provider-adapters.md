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

Initial categories:

- local fixture adapter
- mock managed provider adapter for benchmark scaffolding
- local browser adapter
- proxy-backed browser adapter
- managed browser or scraping API adapter

Provider-specific credentials must come from environment variables, not source files.

Run the provider-shaped benchmark scaffold:

```bash
python -m benchmarks.scripts.run_provider_stub_benchmark
```

Generate the provider benchmark planning template:

```bash
python -m benchmarks.scripts.generate_provider_benchmark_template
```

The mock adapters are not provider recommendations. They exist so the CSV format, evidence labels, and reporting workflow can be tested before adding real external integrations.
