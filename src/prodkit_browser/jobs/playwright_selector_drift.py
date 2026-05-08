from __future__ import annotations

import argparse
import asyncio
import json
import re
from pathlib import Path
from time import perf_counter

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from prodkit_browser.artifacts import ArtifactWriter
from prodkit_browser.fixtures import FixtureHttpServer
from prodkit_browser.jobs.ecommerce_price_monitor import _load_fixture, _product_slug
from prodkit_browser.metrics import summarize
from prodkit_browser.adapters.provider import FetchResult


def _parse_price(value: str | None) -> float | None:
    if value is None:
        return None
    match = re.search(r"\d+(?:\.\d+)?", value.replace(",", ""))
    return float(match.group(0)) if match else None


async def run(fixture_path: Path, artifact_dir: Path) -> dict[str, object]:
    products = _load_fixture(fixture_path)
    writer = ArtifactWriter(artifact_dir)
    price_events: list[dict[str, object]] = []
    selector_drift: list[dict[str, object]] = []
    rows: list[FetchResult] = []

    with FixtureHttpServer(fixture_path) as server:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            page = await browser.new_page()

            for product, url in zip(products, server.urls, strict=True):
                start = perf_counter()
                slug = _product_slug(product.url)
                html_path = f"playwright-selector-drift/html/{slug}.html"
                screenshot_path = artifact_dir / f"playwright-selector-drift/screenshots/{slug}.png"

                try:
                    response = await page.goto(url, wait_until="domcontentloaded", timeout=5000)
                    title = await page.locator("[data-testid='product-title']").text_content(timeout=500)
                    price_text = await page.locator("[data-testid='price']").text_content(timeout=500)
                    current_price = _parse_price(price_text)
                    html = await page.content()
                    html_artifact = writer.write_text(html_path, html)
                    latency_ms = (perf_counter() - start) * 1000

                    if current_price is None:
                        raise PlaywrightTimeoutError("price text did not contain a numeric value")

                    if current_price != product.previous_price:
                        price_events.append(
                            {
                                "url": product.url,
                                "title": title or slug,
                                "previous_price": product.previous_price,
                                "current_price": current_price,
                                "delta": round(current_price - product.previous_price, 2),
                                "html_artifact": html_artifact,
                            }
                        )

                    rows.append(
                        FetchResult(
                            provider="local-playwright",
                            url=product.url,
                            ok=True,
                            latency_ms=latency_ms,
                            status_code=response.status if response else 0,
                            bytes_out=len(html.encode("utf-8")),
                            text=html,
                            artifact_path=html_artifact,
                        )
                    )
                except PlaywrightTimeoutError as exc:
                    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                    await page.screenshot(path=screenshot_path)
                    html = await page.content()
                    html_artifact = writer.write_text(html_path, html)
                    latency_ms = (perf_counter() - start) * 1000
                    selector_drift.append(
                        {
                            "url": product.url,
                            "reason": str(exc),
                            "expected_selector": "[data-testid='price']",
                            "html_artifact": html_artifact,
                            "screenshot": str(screenshot_path),
                        }
                    )
                    rows.append(
                        FetchResult(
                            provider="local-playwright",
                            url=product.url,
                            ok=False,
                            latency_ms=latency_ms,
                            status_code=0,
                            bytes_out=len(html.encode("utf-8")),
                            text=html,
                            artifact_path=html_artifact,
                            error="selector drift",
                        )
                    )

            await browser.close()

    metrics = summarize(rows)
    summary = {
        "checked": len(products),
        "price_changes": len(price_events),
        "selector_drift": len(selector_drift),
        "screenshots": len(selector_drift),
        "success_rate": metrics["success_rate"],
        "p95_latency_ms": metrics["p95_latency_ms"],
        "artifact_dir": str(artifact_dir / "playwright-selector-drift"),
    }
    writer.write_text("playwright-selector-drift/price_events.json", json.dumps(price_events, indent=2))
    writer.write_text("playwright-selector-drift/selector_drift.json", json.dumps(selector_drift, indent=2))
    writer.write_text("playwright-selector-drift/summary.json", json.dumps(summary, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="benchmarks/fixtures/ecommerce_pages.json")
    parser.add_argument("--artifact-dir", default="artifacts")
    args = parser.parse_args()

    print(json.dumps(asyncio.run(run(Path(args.fixture), Path(args.artifact_dir))), indent=2))


if __name__ == "__main__":
    main()
