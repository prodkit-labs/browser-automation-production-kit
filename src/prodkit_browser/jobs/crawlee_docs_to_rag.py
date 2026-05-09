from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

from prodkit_browser.artifacts import ArtifactWriter
from prodkit_browser.fixtures import FixtureHttpServer
from prodkit_browser.rag_chunks import chunks_from_records, to_jsonl


def _text_from_soup(context: BeautifulSoupCrawlingContext) -> str:
    main = context.soup.find("main") or context.soup.body or context.soup
    return "\n".join(part.strip() for part in main.stripped_strings if part.strip())


def _heading_path(context: BeautifulSoupCrawlingContext) -> list[str]:
    main = context.soup.find("main") or context.soup.body or context.soup
    return [heading.get_text(" ", strip=True) for heading in main.find_all(["h1", "h2", "h3"])]


def _response_status(context: BeautifulSoupCrawlingContext) -> int:
    response = getattr(context, "http_response", None)
    status_code = getattr(response, "status_code", None)
    return int(status_code or 200)


async def run_crawlee_docs_to_rag(fixture_path: Path, artifact_dir: Path) -> list[dict[str, object]]:
    writer = ArtifactWriter(artifact_dir)
    records: list[dict[str, object]] = []
    crawl_metadata: list[dict[str, object]] = []

    storage_dir = artifact_dir / "crawlee-storage"
    crawl_run_id = f"local-fixture:{fixture_path.stem}"
    old_storage = os.environ.get("CRAWLEE_STORAGE_DIR")
    os.environ["CRAWLEE_STORAGE_DIR"] = str(storage_dir)
    try:
        with FixtureHttpServer(fixture_path) as server:
            crawler = BeautifulSoupCrawler(max_request_retries=1, max_requests_per_crawl=len(server.urls))
            source_urls = server.source_urls

            @crawler.router.default_handler
            async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
                heading_path = _heading_path(context)
                source_url = source_urls.get(context.request.url, context.request.url)
                title = heading_path[0] if heading_path else ""
                record = {
                    "url": source_url,
                    "title": title,
                    "heading_path": heading_path,
                    "text": _text_from_soup(context),
                }
                records.append(record)
                crawl_metadata.append(
                    {
                        "crawl_run_id": crawl_run_id,
                        "request_url": context.request.url,
                        "response_status": _response_status(context),
                        "storage_path": str(storage_dir),
                        "discovered_source_url": source_url,
                    }
                )
                await context.push_data(record)

            await crawler.run(server.urls)
    finally:
        if old_storage is None:
            os.environ.pop("CRAWLEE_STORAGE_DIR", None)
        else:
            os.environ["CRAWLEE_STORAGE_DIR"] = old_storage

    records = sorted(records, key=lambda record: str(record["url"]))
    crawl_metadata = sorted(crawl_metadata, key=lambda item: str(item["discovered_source_url"]))
    writer.write_text("crawlee-docs-to-rag/records.json", json.dumps(records, indent=2))
    chunks = chunks_from_records(records)
    writer.write_text("crawlee-docs-to-rag/chunks.jsonl", to_jsonl(chunks))
    metadata_by_source_url = {str(item["discovered_source_url"]): item for item in crawl_metadata}
    chunk_metadata = [
        {"chunk_id": chunk.chunk_id, **metadata_by_source_url.get(chunk.source_url, {})}
        for chunk in chunks
    ]
    writer.write_text(
        "crawlee-docs-to-rag/chunk_metadata.json",
        json.dumps(chunk_metadata, indent=2, sort_keys=True),
    )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="benchmarks/fixtures/docs_pages.json")
    parser.add_argument("--artifact-dir", default="artifacts")
    args = parser.parse_args()

    records = asyncio.run(run_crawlee_docs_to_rag(Path(args.fixture), Path(args.artifact_dir)))
    chunks = chunks_from_records(records)
    print(
        json.dumps(
            {"records": len(records), "chunks": len(chunks), "artifact_dir": args.artifact_dir},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
