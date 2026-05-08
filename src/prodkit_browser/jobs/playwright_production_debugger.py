from __future__ import annotations

import argparse
import asyncio
import csv
import json
import re
import tempfile
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from time import perf_counter
from typing import Any

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import async_playwright

from prodkit_browser.artifacts import ArtifactWriter


@dataclass(frozen=True)
class DebugPage:
    slug: str
    scenario: str
    previous_price: float
    delay_ms: int
    html: str


def _load_pages(path: Path) -> list[DebugPage]:
    fixture: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return [
        DebugPage(
            slug=page["slug"],
            scenario=page["scenario"],
            previous_price=float(page["previous_price"]),
            delay_ms=int(page["delay_ms"]),
            html=page["html"],
        )
        for page in fixture["pages"]
    ]


class BrowserDebugServer:
    def __init__(self, pages: list[DebugPage]) -> None:
        self.pages = pages
        self._tmpdir = tempfile.TemporaryDirectory()
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.urls: dict[str, str] = {}

    def __enter__(self) -> "BrowserDebugServer":
        page_map = {f"/{page.slug}.html": page for page in self.pages}

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                page = page_map.get(self.path)
                if page is None:
                    self.send_response(404)
                    self.end_headers()
                    return

                if page.delay_ms:
                    time.sleep(page.delay_ms / 1000)

                if page.scenario == "network_error":
                    self.close_connection = True
                    self.connection.close()
                    return

                body = page.html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: object) -> None:
                return

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        host, port = self._server.server_address
        self.urls = {page.slug: f"http://{host}:{port}/{page.slug}.html" for page in self.pages}
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
        if self._thread:
            self._thread.join(timeout=2)
        self._tmpdir.cleanup()


def _parse_price(value: str | None) -> float | None:
    if value is None:
        return None
    match = re.search(r"\d+(?:\.\d+)?", value.replace(",", ""))
    return float(match.group(0)) if match else None


async def _safe_content(page) -> str:
    try:
        await page.evaluate("window.stop()")
    except Exception:
        pass

    try:
        return await page.content()
    except Exception as exc:
        return f"<!-- unable to capture page content: {exc} -->"


async def _safe_screenshot(page, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        await page.screenshot(path=path)
        return str(path)
    except Exception:
        return ""


async def run(
    fixture_path: Path,
    artifact_dir: Path,
    navigation_timeout_ms: int = 800,
    selector_timeout_ms: int = 500,
) -> dict[str, object]:
    pages = _load_pages(fixture_path)
    writer = ArtifactWriter(artifact_dir)
    rows: list[dict[str, object]] = []

    with BrowserDebugServer(pages) as server:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            page = await browser.new_page()

            for debug_page in pages:
                url = server.urls[debug_page.slug]
                html_path = f"playwright-production-debugger/html/{debug_page.slug}.html"
                screenshot_path = artifact_dir / (
                    f"playwright-production-debugger/screenshots/{debug_page.slug}.png"
                )
                start = perf_counter()
                ok = False
                failure_reason = ""
                status_code = 0
                price = None
                request_url = url
                request_method = "GET"
                request_resource_type = "document"
                request_failure = ""

                try:
                    response = await page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=navigation_timeout_ms,
                    )
                    status_code = response.status if response else 0
                    if response:
                        request = response.request
                        request_url = request.url
                        request_method = request.method
                        request_resource_type = request.resource_type
                    price_text = await page.locator("[data-testid='price']").text_content(
                        timeout=selector_timeout_ms
                    )
                    price = _parse_price(price_text)
                    if price is None:
                        failure_reason = "price_parse_failed"
                    else:
                        ok = True
                except PlaywrightTimeoutError as exc:
                    failure_reason = "timeout" if debug_page.scenario == "timeout" else "selector_drift"
                    if debug_page.scenario != "timeout":
                        failure_reason = "selector_drift"
                    failure_reason = failure_reason or str(exc)
                    request_failure = str(exc)
                except PlaywrightError as exc:
                    if debug_page.scenario == "network_error":
                        failure_reason = "network_error"
                    else:
                        failure_reason = "browser_error"
                    request_failure = str(exc)

                html = await _safe_content(page)
                html_artifact = writer.write_text(html_path, html)
                screenshot = ""
                if not ok:
                    screenshot = await _safe_screenshot(page, screenshot_path)

                rows.append(
                    {
                        "scenario": debug_page.scenario,
                        "url": url,
                        "ok": ok,
                        "failure_reason": failure_reason,
                        "request_url": request_url,
                        "request_method": request_method,
                        "request_resource_type": request_resource_type,
                        "request_failure": request_failure,
                        "latency_ms": round((perf_counter() - start) * 1000, 2),
                        "status_code": status_code,
                        "bytes_out": len(html.encode("utf-8")),
                        "previous_price": debug_page.previous_price,
                        "current_price": price,
                        "html_artifact": html_artifact,
                        "screenshot": screenshot,
                    }
                )

            await browser.close()

    output_dir = artifact_dir / "playwright-production-debugger"
    csv_path = output_dir / "benchmark.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer_csv = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer_csv.writeheader()
        writer_csv.writerows(rows)

    summary = {
        "checked": len(rows),
        "passed": sum(1 for row in rows if row["ok"]),
        "failed": sum(1 for row in rows if not row["ok"]),
        "screenshots": sum(1 for row in rows if row["screenshot"]),
        "failure_reasons": sorted({row["failure_reason"] for row in rows if row["failure_reason"]}),
        "artifact_dir": str(output_dir),
        "benchmark_csv": str(csv_path),
    }
    writer.write_text("playwright-production-debugger/summary.json", json.dumps(summary, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="benchmarks/fixtures/browser_debug_pages.json")
    parser.add_argument("--artifact-dir", default="artifacts")
    parser.add_argument("--navigation-timeout-ms", type=int, default=800)
    parser.add_argument("--selector-timeout-ms", type=int, default=500)
    args = parser.parse_args()

    print(
        json.dumps(
            asyncio.run(
                run(
                    Path(args.fixture),
                    Path(args.artifact_dir),
                    args.navigation_timeout_ms,
                    args.selector_timeout_ms,
                )
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
