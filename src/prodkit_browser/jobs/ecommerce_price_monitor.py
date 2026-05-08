from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from prodkit_browser.adapters.provider import LocalFixtureAdapter
from prodkit_browser.artifacts import ArtifactWriter


@dataclass(frozen=True)
class ProductPage:
    url: str
    html: str
    previous_price: float


class ProductParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._capture_title = False
        self._capture_price = False
        self.title: str | None = None
        self.price_text: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        test_id = attr_map.get("data-testid")
        if test_id == "product-title":
            self._capture_title = True
        if test_id == "price":
            self._capture_price = True

    def handle_endtag(self, tag: str) -> None:
        self._capture_title = False
        self._capture_price = False

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        if self._capture_title:
            self.title = cleaned
        if self._capture_price:
            self.price_text = cleaned


def _load_fixture(path: Path) -> list[ProductPage]:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    return [
        ProductPage(
            url=page["url"],
            html=page["html"],
            previous_price=float(page["previous_price"]),
        )
        for page in fixture["pages"]
    ]


def _parse_price(value: str | None) -> float | None:
    if value is None:
        return None
    match = re.search(r"\d+(?:\.\d+)?", value.replace(",", ""))
    return float(match.group(0)) if match else None


def _product_slug(url: str) -> str:
    return url.rstrip("/").split("/")[-1] or "product"


def run(fixture_path: Path, artifact_dir: Path) -> dict[str, object]:
    products = _load_fixture(fixture_path)
    pages = {product.url: product.html for product in products}
    previous_prices = {product.url: product.previous_price for product in products}
    adapter = LocalFixtureAdapter(pages)
    writer = ArtifactWriter(artifact_dir)

    price_events: list[dict[str, object]] = []
    selector_drift: list[dict[str, object]] = []

    for product in products:
        result = adapter.fetch(product.url)
        slug = _product_slug(product.url)
        html_artifact = writer.write_text(f"ecommerce-price-monitor/html/{slug}.html", result.text)

        parser = ProductParser()
        parser.feed(result.text)
        current_price = _parse_price(parser.price_text)

        if current_price is None:
            drift = {
                "url": product.url,
                "reason": "price selector not found",
                "expected_selector": "[data-testid='price']",
                "html_artifact": html_artifact,
                "screenshot_placeholder": f"artifacts/ecommerce-price-monitor/screenshots/{slug}.png",
            }
            selector_drift.append(drift)
            continue

        previous_price = previous_prices[product.url]
        if current_price != previous_price:
            price_events.append(
                {
                    "url": product.url,
                    "title": parser.title or slug,
                    "previous_price": previous_price,
                    "current_price": current_price,
                    "delta": round(current_price - previous_price, 2),
                    "html_artifact": html_artifact,
                }
            )

    summary = {
        "checked": len(products),
        "price_changes": len(price_events),
        "selector_drift": len(selector_drift),
        "artifact_dir": str(artifact_dir / "ecommerce-price-monitor"),
    }
    writer.write_text("ecommerce-price-monitor/price_events.json", json.dumps(price_events, indent=2))
    writer.write_text("ecommerce-price-monitor/selector_drift.json", json.dumps(selector_drift, indent=2))
    writer.write_text("ecommerce-price-monitor/summary.json", json.dumps(summary, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="benchmarks/fixtures/ecommerce_pages.json")
    parser.add_argument("--artifact-dir", default="artifacts")
    args = parser.parse_args()

    print(json.dumps(run(Path(args.fixture), Path(args.artifact_dir)), indent=2))


if __name__ == "__main__":
    main()
