from __future__ import annotations

import os
from collections.abc import Mapping

from .base import (
    FetchResult,
    ProviderAdapterMetadata,
    ProviderCapabilities,
    ProviderRuntimeConfig,
    missing_required_env,
)


class ProviderConfigurationError(ValueError):
    """Raised when a provider adapter is missing required runtime configuration."""


class ExternalProviderAdapterBase:
    """Base class for provider adapters that call external managed services."""

    metadata: ProviderAdapterMetadata
    capabilities: ProviderCapabilities

    def __init__(
        self,
        environ: Mapping[str, str] | None = None,
        runtime_config: ProviderRuntimeConfig | None = None,
    ) -> None:
        self._environ = environ if environ is not None else os.environ
        self.runtime_config = runtime_config or ProviderRuntimeConfig()
        missing = missing_required_env(self.metadata, self._environ)
        if missing:
            joined = ", ".join(missing)
            raise ProviderConfigurationError(
                f"{self.metadata.name} requires environment variables: {joined}"
            )

    @property
    def name(self) -> str:
        return self.metadata.name

    def credential(self, name: str) -> str:
        value = self._environ.get(name)
        if not value:
            raise ProviderConfigurationError(
                f"{self.metadata.name} requires environment variable: {name}"
            )
        return value

    def optional_setting(self, name: str) -> str | None:
        return self._environ.get(name)

    def fetch(self, url: str) -> FetchResult:
        raise NotImplementedError("External provider adapters must implement fetch().")
