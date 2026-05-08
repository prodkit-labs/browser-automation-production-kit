import csv

from benchmarks.scripts import generate_provider_benchmark_template


def test_provider_benchmark_template_includes_scraperapi_without_links(tmp_path) -> None:
    output = tmp_path / "provider_benchmark_template.csv"

    generate_provider_benchmark_template.write_template(output)

    rows = list(csv.DictReader(output.open(encoding="utf-8")))
    scraperapi = [row for row in rows if row["provider"] == "ScraperAPI"]

    assert scraperapi
    assert scraperapi[0]["category"] == "scraping API"
    assert scraperapi[0]["evidence"] == "not tested"
    assert "affiliate link" in scraperapi[0]["public_link_policy"]
    assert "http" not in "\n".join(row["public_link_policy"] for row in rows)
