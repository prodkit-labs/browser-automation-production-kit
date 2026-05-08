"""Provider adapter contracts."""

from .base import FetchResult, ProviderAdapter
from .local import LocalFixtureAdapter
from .mock_managed import MockManagedProviderAdapter

__all__ = ["FetchResult", "LocalFixtureAdapter", "MockManagedProviderAdapter", "ProviderAdapter"]
