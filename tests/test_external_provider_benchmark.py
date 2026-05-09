from prodkit_browser.adapters.provider import (
    ExternalProviderAdapterBase,
    FetchResult,
    ProviderAdapterMetadata,
    ProviderCapabilities,
)

from benchmarks.scripts.run_external_provider_benchmark import run_external_benchmark


class ExampleExternalBenchmarkAdapter(ExternalProviderAdapterBase):
    metadata = ProviderAdapterMetadata(
        name="example-external-provider",
        category="managed browser API",
        execution_mode="hosted browser runtime",
        evidence="not tested",
        required_env=("EXAMPLE_PROVIDER_API_KEY",),
    )
    capabilities = ProviderCapabilities(html_artifacts=True)

    def fetch(self, url: str) -> FetchResult:
        self.credential("EXAMPLE_PROVIDER_API_KEY")
        return FetchResult(
            provider=self.name,
            url=url,
            ok=True,
            latency_ms=12,
            status_code=200,
            bytes_out=42,
            text="<html></html>",
            cost_usd=0.002,
        )


ADAPTER_PATH = "tests.test_external_provider_benchmark:ExampleExternalBenchmarkAdapter"


def test_external_benchmark_skips_when_required_env_is_missing(tmp_path) -> None:
    result = run_external_benchmark(
        adapter_path=ADAPTER_PATH,
        fixture_path=tmp_path / "missing.json",
        output=tmp_path / "external.csv",
        environ={},
    )

    assert result["ok"] is False
    assert result["missing_env"] == ["EXAMPLE_PROVIDER_API_KEY"]
    assert not (tmp_path / "external.csv").exists()


def test_external_benchmark_writes_raw_csv_when_env_is_present(tmp_path) -> None:
    fixture = tmp_path / "fixture.json"
    fixture.write_text(
        '{"pages":[{"url":"https://example.test/a","html":"<html>A</html>"}]}',
        encoding="utf-8",
    )
    output = tmp_path / "external.csv"

    result = run_external_benchmark(
        adapter_path=ADAPTER_PATH,
        fixture_path=fixture,
        output=output,
        environ={"EXAMPLE_PROVIDER_API_KEY": "secret"},
    )

    assert result["ok"] is True
    assert result["provider"] == "example-external-provider"
    assert result["evidence"] == "not tested"
    assert result["summary"]["success_rate"] == 1.0
    assert result["summary"]["cost_per_1k_requests_usd"] == 2
    assert result["summary"]["cost_per_1k_successful_pages_usd"] == 2
    assert output.read_text(encoding="utf-8").startswith("evidence,provider,url")
