from __future__ import annotations

import json
import tempfile
import threading
from contextlib import AbstractContextManager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


def load_pages(path: Path) -> list[dict[str, str]]:
    fixture: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return [{"url": page["url"], "html": page["html"]} for page in fixture["pages"]]


class FixtureHttpServer(AbstractContextManager["FixtureHttpServer"]):
    def __init__(self, fixture_path: Path) -> None:
        self.fixture_path = fixture_path
        self._tmpdir = tempfile.TemporaryDirectory()
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.urls: list[str] = []

    def __enter__(self) -> "FixtureHttpServer":
        root = Path(self._tmpdir.name)
        pages = load_pages(self.fixture_path)

        for index, page in enumerate(pages, start=1):
            source_name = page["url"].rstrip("/").split("/")[-1] or f"page-{index}"
            file_name = f"{index:03d}-{source_name}.html"
            (root / file_name).write_text(page["html"], encoding="utf-8")

        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args: object, **kwargs: object) -> None:
                super().__init__(*args, directory=str(root), **kwargs)

            def log_message(self, format: str, *args: object) -> None:
                return

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        host, port = self._server.server_address
        self.urls = [f"http://{host}:{port}/{path.name}" for path in sorted(root.glob("*.html"))]

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
