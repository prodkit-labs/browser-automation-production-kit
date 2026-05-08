from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

from prodkit_browser.artifacts import ArtifactWriter
from prodkit_browser.fixtures import FixtureHttpServer


def _text_from_soup(context: BeautifulSoupCrawlingContext) -> str:
    main = context.soup.find("main") or context.soup.body or context.soup
    return "\n".join(part.strip() for part in main.stripped_strings if part.strip())


async def run_crawlee_docs_to_rag(fixture_path: Path, artifact_dir: Path) -> list[dict[str, str]]:
    writer = ArtifactWriter(artifact_dir)
    records: list[dict[str, str]] = []

    storage_dir = artifact_dir / "crawlee-storage"
    old_storage = os.environ.get("CRAWLEE_STORAGE_DIR")
    os.environ["CRAWLEE_STORAGE_DIR"] = str(storage_dir)
    try:
        with FixtureHttpServer(fixture_path) as server:
            crawler = BeautifulSoupCrawler(max_request_retries=1, max_requests_per_crawl=len(server.urls))

            @crawler.router.default_handler
            async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
                title = context.soup.title.string if context.soup.title else None
                record = {
                    "url": context.request.url,
                    "title": title or "",
                    "text": _text_from_soup(context),
                }
                records.append(record)
                await context.push_data(record)

            await crawler.run(server.urls)
    finally:
        if old_storage is None:
            os.environ.pop("CRAWLEE_STORAGE_DIR", None)
        else:
            os.environ["CRAWLEE_STORAGE_DIR"] = old_storage

    writer.write_text("crawlee-docs-to-rag/records.json", json.dumps(records, indent=2))
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="benchmarks/fixtures/docs_pages.json")
    parser.add_argument("--artifact-dir", default="artifacts")
    args = parser.parse_args()

    records = asyncio.run(run_crawlee_docs_to_rag(Path(args.fixture), Path(args.artifact_dir)))
    print(json.dumps({"records": len(records), "artifact_dir": args.artifact_dir}, indent=2))


if __name__ == "__main__":
    main()
