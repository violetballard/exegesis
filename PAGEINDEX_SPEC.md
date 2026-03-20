# PageIndex Retrieval Spec (Deferred)

Status: deferred until after the current MVP / demo push.

Current MVP retrieval is SQLite FTS-first with excerpt provenance. PageIndex is not part of the active near-term implementation plan.

## Purpose

- Structured, auditable within-document retrieval for long sources.
- Optimized for qualitative workflows that need stable evidence provenance.
- Offline-first and encrypted at rest in confidential mode.
- Adds local vision/OCR fallback for scanned PDFs when capability-gated support is present.

## Data Model

- `DocumentIndexRecord`:
  - `doc_id`
  - `index_type=pageindex`
  - `version=pageindex_v2`
  - source/index hashes
  - status (`building|ready|failed|stale`)
  - `requires_ocr`
  - `vision_enabled_at_build`
  - `model_used` metadata
- `PageIndexPayload` (encrypted):
  - tree nodes and ranges
  - optional node summaries
  - page-to-excerpt references
  - optional vision artifacts (`page -> excerpt_ids`)
  - build metadata
- Encrypted excerpt blobs with integrity hashes

## API

- `docindex.build(doc_id, source_bytes, options) -> JobRef`
- `docindex.query(doc_id, source_bytes, query, constraints, options) -> PageIndexResult`
- `vision_read_pages(doc_id, page_numbers, output_format, max_pages, options)`
- `fetch_excerpt(excerpt_id) -> {text, provenance}`
- `pin_to_context_set(context_set_id, excerpt_id)`

`docindex.query` returns node paths + ranges + `excerpt_ids`, not large raw text dumps.

## Policy / Confidential Mode

- Confidential mode requires:
  - `offline_only`
  - local text extraction
  - `openai_compat` provider
  - localhost endpoint (`127.0.0.1` or `localhost`)
- Non-local endpoints are denied.
- Vision fallback is enabled only when BOTH runtime image input and Magistral vision model capability are true.

## Caching and Invalidation

- Query cache key:
  - `doc_id + query_hash + constraints_hash + index_hash`
- Cache TTL: 1 hour (encrypted cache store)
- If source hash changes, index is marked `stale`.

## Audit Events

- `docindex_build_started`
- `docindex_build_completed`
- `docindex_build_failed`
- `docindex_query_executed` (query hash only; no raw prompt logging)
- `vision_read_pages_executed` (page numbers only; no extracted text logging)
