from __future__ import annotations

from time import perf_counter

from .base import FetchResult, ProviderAdapterMetadata, ProviderCapabilities


class MockManagedProviderAdapter:
    """Deterministic provider-shaped adapter for benchmark scaffolding."""

    def __init__(
        self,
        name: str,
        pages: dict[str, str],
        latency_ms: float,
        cost_per_1k_pages_usd: float,
        fail_urls: set[str] | None = None,
    ) -> None:
        self.name = name
        self.metadata = ProviderAdapterMetadata(
            name=name,
            category="managed browser API",
            execution_mode="mock managed provider",
            evidence="estimated",
            notes=("deterministic mock for report shape validation",),
        )
        self.capabilities = ProviderCapabilities(
            javascript_rendering=True,
            screenshots=True,
            html_artifacts=True,
            sessions=True,
            artifact_types=("html", "screenshot"),
        )
        self._pages = pages
        self._latency_ms = latency_ms
        self._cost_per_page = cost_per_1k_pages_usd / 1000
        self._fail_urls = fail_urls or set()

    def fetch(self, url: str) -> FetchResult:
        start = perf_counter()
        text = self._pages.get(url, "")
        elapsed_ms = (perf_counter() - start) * 1000
        latency_ms = round(self._latency_ms + elapsed_ms, 2)

        if url in self._fail_urls:
            return FetchResult(
                provider=self.name,
                url=url,
                ok=False,
                latency_ms=latency_ms,
                status_code=429,
                bytes_out=0,
                text="",
                cost_usd=self._cost_per_page,
                error="simulated provider throttle",
            )

        if not text:
            return FetchResult(
                provider=self.name,
                url=url,
                ok=False,
                latency_ms=latency_ms,
                status_code=404,
                bytes_out=0,
                text="",
                cost_usd=self._cost_per_page,
                error="fixture not found",
            )

        return FetchResult(
            provider=self.name,
            url=url,
            ok=True,
            latency_ms=latency_ms,
            status_code=200,
            bytes_out=len(text.encode("utf-8")),
            text=text,
            cost_usd=self._cost_per_page,
        )
