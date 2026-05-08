# Provider Degradation Runbook

Use this when provider-backed runs suddenly become slower or less reliable.

Checks:

1. Compare local fixture runs with provider-backed runs.
2. Review status codes, latency, and error messages.
3. Check whether failures concentrate in one region or job type.
4. Lower retry pressure if block rate is increasing.
5. Switch to a known working adapter only if benchmark data supports it.

Record:

- affected job
- provider
- first failed run
- success rate change
- latency change
- artifact sample path
