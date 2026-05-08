from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping, Protocol


EvidenceLabel = Literal["measured", "estimated", "not tested"]


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


@dataclass(frozen=True)
class ProviderAdapterMetadata:
    name: str
    category: str
    execution_mode: str
    evidence: EvidenceLabel
    required_env: tuple[str, ...] = ()
    optional_env: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProviderCapabilities:
    javascript_rendering: bool = False
    screenshots: bool = False
    html_artifacts: bool = False
    proxy_regions: bool = False
    sessions: bool = False
    artifact_types: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProviderRuntimeConfig:
    timeout_seconds: float = 30.0
    max_retries: int = 0
    region: str | None = None
    session_id: str | None = None


def missing_required_env(
    metadata: ProviderAdapterMetadata,
    environ: Mapping[str, str],
) -> tuple[str, ...]:
    return tuple(name for name in metadata.required_env if not environ.get(name))


class ProviderAdapter(Protocol):
    name: str
    metadata: ProviderAdapterMetadata
    capabilities: ProviderCapabilities

    def fetch(self, url: str) -> FetchResult:
        """Fetch a URL or fixture and return normalized execution metadata."""
