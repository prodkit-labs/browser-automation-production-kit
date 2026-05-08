import pytest

from prodkit_browser.adapters.provider import (
    ExternalProviderAdapterBase,
    FetchResult,
    LocalFixtureAdapter,
    MockManagedProviderAdapter,
    ProviderAdapterMetadata,
    ProviderCapabilities,
    ProviderConfigurationError,
    ProviderRuntimeConfig,
    missing_required_env,
)


class ExampleManagedBrowserAdapter(ExternalProviderAdapterBase):
    metadata = ProviderAdapterMetadata(
        name="example-managed-browser",
        category="managed browser API",
        execution_mode="hosted Playwright/browser runtime",
        evidence="not tested",
        required_env=("EXAMPLE_BROWSER_API_KEY",),
    )
    capabilities = ProviderCapabilities(
        javascript_rendering=True,
        screenshots=True,
        html_artifacts=True,
        sessions=True,
        artifact_types=("html", "screenshot"),
    )

    def fetch(self, url: str) -> FetchResult:
        return FetchResult(
            provider=self.name,
            url=url,
            ok=True,
            latency_ms=1,
            status_code=200,
            bytes_out=0,
            text="",
        )


def test_external_provider_requires_env_credentials() -> None:
    with pytest.raises(ProviderConfigurationError, match="EXAMPLE_BROWSER_API_KEY"):
        ExampleManagedBrowserAdapter(environ={})


def test_external_provider_exposes_runtime_config_and_credentials() -> None:
    adapter = ExampleManagedBrowserAdapter(
        environ={"EXAMPLE_BROWSER_API_KEY": "secret"},
        runtime_config=ProviderRuntimeConfig(timeout_seconds=5, region="us"),
    )

    assert adapter.name == "example-managed-browser"
    assert adapter.credential("EXAMPLE_BROWSER_API_KEY") == "secret"
    assert adapter.runtime_config.timeout_seconds == 5
    assert adapter.runtime_config.region == "us"
    assert adapter.metadata.evidence == "not tested"


def test_missing_required_env_reports_only_missing_values() -> None:
    metadata = ProviderAdapterMetadata(
        name="example",
        category="scraping API",
        execution_mode="API-first extraction",
        evidence="not tested",
        required_env=("API_KEY", "API_REGION"),
    )

    assert missing_required_env(metadata, {"API_KEY": "secret"}) == ("API_REGION",)


def test_builtin_adapters_expose_metadata_and_capabilities() -> None:
    local = LocalFixtureAdapter({"https://example.test": "<html></html>"})
    mock = MockManagedProviderAdapter("mock-provider", {"https://example.test": "ok"}, 100, 1.5)

    assert local.metadata.evidence == "measured"
    assert local.capabilities.html_artifacts is True
    assert mock.metadata.evidence == "estimated"
    assert mock.capabilities.javascript_rendering is True
