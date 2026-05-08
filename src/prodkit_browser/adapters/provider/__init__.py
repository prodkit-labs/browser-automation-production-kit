"""Provider adapter contracts."""

from .base import FetchResult, ProviderAdapter
from .local import LocalFixtureAdapter

__all__ = ["FetchResult", "LocalFixtureAdapter", "ProviderAdapter"]
