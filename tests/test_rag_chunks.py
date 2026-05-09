from prodkit_browser.rag_chunks import chunks_from_record, slug_from_url


def test_chunks_from_record_preserves_metadata() -> None:
    chunks = chunks_from_record(
        {
            "url": "https://example.test/docs/getting-started",
            "title": "Getting Started",
            "text": "Getting Started\nInstall the package.",
        }
    )

    assert len(chunks) == 1
    assert chunks[0].source_url == "https://example.test/docs/getting-started"
    assert chunks[0].title == "Getting Started"
    assert chunks[0].heading_path == ["Getting Started"]
    assert chunks[0].token_count == 5
    assert chunks[0].char_count == len("Getting Started\nInstall the package.")
    assert len(chunks[0].content_hash) == 64
    assert len(chunks[0].chunk_id) == 16


def test_chunks_split_on_paragraph_boundaries() -> None:
    chunks = chunks_from_record(
        {
            "url": "https://example.test/docs/long",
            "title": "Long",
            "text": "first paragraph\nsecond paragraph\nthird paragraph",
        },
        max_chars=25,
    )

    assert [chunk.text for chunk in chunks] == [
        "first paragraph",
        "second paragraph",
        "third paragraph",
    ]


def test_slug_from_url_uses_index_for_root() -> None:
    assert slug_from_url("https://example.test/") == "index"
