from __future__ import annotations

import statistics

from prodkit_browser.adapters.provider import FetchResult


def summarize(rows: list[FetchResult]) -> dict[str, float | int]:
    if not rows:
        return {"count": 0, "success_rate": 0.0, "p95_latency_ms": 0.0, "bytes_out": 0}

    success_count = sum(1 for row in rows if row.ok)
    latencies = [row.latency_ms for row in rows]
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)

    return {
        "count": len(rows),
        "success_rate": round(success_count / len(rows), 4),
        "p95_latency_ms": round(p95, 2),
        "bytes_out": sum(row.bytes_out for row in rows),
    }
