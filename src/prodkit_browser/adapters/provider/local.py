from __future__ import annotations

from time import perf_counter

from .base import FetchResult, ProviderAdapterMetadata, ProviderCapabilities


class LocalFixtureAdapter:
    name = "local-fixture"
    metadata = ProviderAdapterMetadata(
        name=name,
        category="baseline",
        execution_mode="local HTTP / fixture",
        evidence="measured",
        notes=("fixture-only baseline; does not represent live-site behavior",),
    )
    capabilities = ProviderCapabilities(html_artifacts=True, artifact_types=("html",))

    def __init__(self, pages: dict[str, str]) -> None:
        self._pages = pages

    def fetch(self, url: str) -> FetchResult:
        start = perf_counter()
        text = self._pages.get(url, "")
        latency_ms = (perf_counter() - start) * 1000

        if not text:
            return FetchResult(
                provider=self.name,
                url=url,
                ok=False,
                latency_ms=latency_ms,
                status_code=404,
                bytes_out=0,
                text="",
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
        )
