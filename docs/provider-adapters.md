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
- local browser adapter
- proxy-backed browser adapter
- managed browser or scraping API adapter

Provider-specific credentials must come from environment variables, not source files.
