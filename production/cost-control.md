# Cost Control

Browser automation costs usually grow through retries, browser minutes, provider calls, artifact storage, and region routing.

Generate the reproducible cost model:

```bash
python -m benchmarks.scripts.generate_cost_per_1k_report
```

The raw assumptions are written to `benchmarks/raw/cost_per_1k_pages.csv`.
The generated report is written to `benchmarks/reports/cost-per-1k-pages.md`.
The tracked template is available at
[`reports/cost-per-1k-pages-template.md`](../reports/cost-per-1k-pages-template.md).

For docs-to-RAG ingestion runs, generate the success and cost-input report:

```bash
python -m benchmarks.scripts.generate_ingestion_success_report
```

The raw ingestion rows are written to
`benchmarks/raw/ingestion_success_cost.csv`. The generated report is written to
`benchmarks/reports/ingestion-success-cost.md`.

For the full docs-to-RAG command sequence, use
[`Local-first RAG ingestion`](rag-ingestion.md).

Control points:

- set retry budgets per job
- record bytes and artifact volume
- separate fixture, local, and provider-backed runs
- check ingestion success rate before scaling page volume
- estimate cost per 1k pages
- stop jobs when block rate crosses a threshold
- compare providers with raw benchmark data
- keep full artifacts for failures and sampled successes
- cache stable public pages where terms and workflow requirements allow it

## Cost Inputs

| Input | Why it matters | How to reduce it |
|---|---|---|
| Retries | Retried pages can multiply browser and provider usage | classify failures before retrying |
| Browser minutes | Browser runtime can become the main operating cost | reduce waits and keep fixture tests fast |
| Proxy/API calls | Provider-backed paths may charge per call or usage unit | avoid re-fetching stable pages |
| Artifact storage | HTML, screenshots, traces, and logs accumulate | keep full artifacts for failures and sample successes |
| Debugging time | Human investigation can dominate low-volume jobs | preserve failure reasons and artifacts |

Do not compare providers only by sticker price. A cheaper call can become more
expensive when retries, failed pages, artifacts, or debugging time increase.
