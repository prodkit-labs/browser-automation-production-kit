"""Production patterns for browser automation workflows."""

from importlib.metadata import PackageNotFoundError, version

__all__ = ["__version__"]

try:
    __version__ = version("browser-automation-production-kit")
except PackageNotFoundError:
    __version__ = "0.0.0"
