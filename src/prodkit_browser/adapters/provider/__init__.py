"""Provider adapter contracts."""

from .base import (
    EvidenceLabel,
    FetchResult,
    ProviderAdapter,
    ProviderAdapterMetadata,
    ProviderCapabilities,
    ProviderRuntimeConfig,
    missing_required_env,
)
from .external import ExternalProviderAdapterBase, ProviderConfigurationError
from .local import LocalFixtureAdapter
from .mock_managed import MockManagedProviderAdapter

__all__ = [
    "EvidenceLabel",
    "ExternalProviderAdapterBase",
    "FetchResult",
    "LocalFixtureAdapter",
    "MockManagedProviderAdapter",
    "ProviderAdapter",
    "ProviderAdapterMetadata",
    "ProviderCapabilities",
    "ProviderConfigurationError",
    "ProviderRuntimeConfig",
    "missing_required_env",
]
