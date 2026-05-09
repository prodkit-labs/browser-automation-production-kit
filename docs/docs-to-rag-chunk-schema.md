# Docs-To-RAG Chunk Schema

The docs-to-RAG workflow writes deterministic document chunks to:

```text
artifacts/docs-to-rag/chunks.jsonl
```

Each line is one JSON object. The output stays local-first and does not require
an embeddings API, vector database, or hosted browser provider.

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `chunk_id` | string | Stable 16-character hash for the source URL, chunk index, and chunk text. |
| `source_url` | string | Original page URL from the fixture or crawl result. |
| `title` | string | First page heading, or a readable fallback derived from the URL. |
| `heading_path` | array | Heading path available for this chunk. |
| `text` | string | Chunk text. |
| `token_count` | number | Whitespace token count for quick local sizing. |
| `char_count` | number | Character count for the chunk text. |
| `content_hash` | string | SHA-256 hash of the chunk text. |

## Example

```json
{
  "chunk_id": "5d0d2a7c5cbb8a1f",
  "source_url": "https://example.test/docs/getting-started",
  "title": "Getting Started",
  "heading_path": ["Getting Started"],
  "text": "Getting Started\nInstall the package, configure a worker...",
  "token_count": 12,
  "char_count": 86,
  "content_hash": "..."
}
```

## Boundary

This schema is intentionally provider-neutral. Add embeddings, vector stores,
or hosted browser execution behind later adapters after the local fixture output
is reproducible.

Crawlee runs use the same chunk fields in
`artifacts/crawlee-docs-to-rag/chunks.jsonl`. Crawl-specific details are written
to `artifacts/crawlee-docs-to-rag/chunk_metadata.json` as a sidecar keyed by
`chunk_id`.

For the full local pipeline from fixture pages to retrieval and cost-input
reports, see [`Local-first RAG ingestion`](../production/rag-ingestion.md).
