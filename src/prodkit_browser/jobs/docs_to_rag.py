from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path

from prodkit_browser.adapters.provider import LocalFixtureAdapter
from prodkit_browser.artifacts import ArtifactWriter
from prodkit_browser.rag_chunks import chunks_from_records, to_jsonl


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._title = ""
        self._heading_stack: list[str] = []
        self._current_heading: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"h1", "h2", "h3"}:
            self._current_heading = tag

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if cleaned:
            self._parts.append(cleaned)
            if self._current_heading:
                level = int(self._current_heading[1])
                self._heading_stack = self._heading_stack[: level - 1]
                self._heading_stack.append(cleaned)
                if not self._title:
                    self._title = cleaned

    def handle_endtag(self, tag: str) -> None:
        if tag == self._current_heading:
            self._current_heading = None

    @property
    def text(self) -> str:
        return "\n".join(self._parts)

    @property
    def title(self) -> str:
        return self._title

    @property
    def heading_path(self) -> list[str]:
        return self._heading_stack


def load_fixture(path: Path) -> tuple[dict[str, str], list[str]]:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    pages = {page["url"]: page["html"] for page in fixture["pages"]}
    urls = [page["url"] for page in fixture["pages"]]
    return pages, urls


def normalize_record(url: str, html: str) -> dict[str, str]:
    parser = TextExtractor()
    parser.feed(html)
    return {
        "url": url,
        "title": parser.title,
        "heading_path": parser.heading_path,
        "text": parser.text,
    }


def run(fixture_path: Path, artifact_dir: Path) -> list[dict[str, str]]:
    pages, urls = load_fixture(fixture_path)
    adapter = LocalFixtureAdapter(pages)
    writer = ArtifactWriter(artifact_dir)
    records: list[dict[str, str]] = []

    for url in urls:
        result = adapter.fetch(url)
        writer.write_text(f"html/{url.split('/')[-1] or 'index'}.html", result.text)
        if result.ok:
            records.append(normalize_record(url, result.text))

    writer.write_text("docs-to-rag/records.json", json.dumps(records, indent=2))
    chunks = chunks_from_records(records)
    writer.write_text("docs-to-rag/chunks.jsonl", to_jsonl(chunks))
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="benchmarks/fixtures/docs_pages.json")
    parser.add_argument("--artifact-dir", default="artifacts")
    args = parser.parse_args()

    records = run(Path(args.fixture), Path(args.artifact_dir))
    chunks = chunks_from_records(records)
    print(
        json.dumps(
            {"records": len(records), "chunks": len(chunks), "artifact_dir": args.artifact_dir},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
