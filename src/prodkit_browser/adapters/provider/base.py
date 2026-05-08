from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class FetchResult:
    provider: str
    url: str
    ok: bool
    latency_ms: float
    status_code: int
    bytes_out: int
    text: str
    artifact_path: str | None = None
    cost_usd: float | None = None
    error: str | None = None


class ProviderAdapter(Protocol):
    name: str

    def fetch(self, url: str) -> FetchResult:
        """Fetch a URL or fixture and return normalized execution metadata."""
