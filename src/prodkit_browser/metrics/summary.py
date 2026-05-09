from __future__ import annotations

import statistics

from prodkit_browser.adapters.provider import FetchResult


def percentile_95(values: list[float]) -> float:
    if not values:
        return 0.0
    if len(values) < 20:
        return round(max(values), 2)
    return round(statistics.quantiles(values, n=20)[18], 2)


def cost_per_1k_requests(rows: list[FetchResult]) -> float:
    if not rows:
        return 0.0
    total_cost = sum(row.cost_usd or 0 for row in rows)
    return round((total_cost / len(rows)) * 1000, 4)


def cost_per_1k_successful_pages(rows: list[FetchResult]) -> float:
    successful_pages = sum(1 for row in rows if row.ok)
    if successful_pages <= 0:
        return 0.0
    total_cost = sum(row.cost_usd or 0 for row in rows)
    return round((total_cost / successful_pages) * 1000, 4)


def summarize(rows: list[FetchResult]) -> dict[str, float | int]:
    if not rows:
        return {"count": 0, "success_rate": 0.0, "p95_latency_ms": 0.0, "bytes_out": 0}

    success_count = sum(1 for row in rows if row.ok)
    latencies = [row.latency_ms for row in rows]

    return {
        "count": len(rows),
        "success_rate": round(success_count / len(rows), 4),
        "p95_latency_ms": percentile_95(latencies),
        "bytes_out": sum(row.bytes_out for row in rows),
    }
