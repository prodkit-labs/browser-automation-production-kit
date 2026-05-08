from prodkit_browser.adapters.provider import LocalFixtureAdapter


def test_local_fixture_adapter_returns_page_metadata() -> None:
    adapter = LocalFixtureAdapter({"https://example.test/page": "<html>Hello</html>"})

    result = adapter.fetch("https://example.test/page")

    assert result.ok is True
    assert result.provider == "local-fixture"
    assert result.status_code == 200
    assert result.bytes_out > 0


def test_local_fixture_adapter_reports_missing_page() -> None:
    adapter = LocalFixtureAdapter({})

    result = adapter.fetch("https://example.test/missing")

    assert result.ok is False
    assert result.status_code == 404
    assert result.error == "fixture not found"
