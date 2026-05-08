from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path

from prodkit_browser.adapters.provider import LocalFixtureAdapter
from prodkit_browser.artifacts import ArtifactWriter


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if cleaned:
            self._parts.append(cleaned)

    @property
    def text(self) -> str:
        return "\n".join(self._parts)


def load_fixture(path: Path) -> tuple[dict[str, str], list[str]]:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    pages = {page["url"]: page["html"] for page in fixture["pages"]}
    urls = [page["url"] for page in fixture["pages"]]
    return pages, urls


def normalize_record(url: str, html: str) -> dict[str, str]:
    parser = TextExtractor()
    parser.feed(html)
    return {"url": url, "text": parser.text}


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
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="benchmarks/fixtures/docs_pages.json")
    parser.add_argument("--artifact-dir", default="artifacts")
    args = parser.parse_args()

    records = run(Path(args.fixture), Path(args.artifact_dir))
    print(json.dumps({"records": len(records), "artifact_dir": args.artifact_dir}, indent=2))


if __name__ == "__main__":
    main()
