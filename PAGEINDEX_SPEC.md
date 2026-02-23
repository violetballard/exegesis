# PageIndex Retrieval Spec

## Purpose

- Structured, auditable within-document retrieval for long sources.
- Optimized for qualitative workflows that need stable evidence provenance.
- Offline-first and encrypted at rest in confidential mode.

## Data Model

- `DocumentIndexRecord`:
  - `doc_id`
  - `index_type=pageindex`
  - `version=pageindex_v1`
  - source/index hashes
  - status (`building|ready|failed|stale`)
- `PageIndexPayload` (encrypted):
  - tree nodes and ranges
  - optional node summaries
  - page-to-excerpt references
  - build metadata
- Encrypted excerpt blobs with integrity hashes

## API

- `docindex.build(doc_id, source_bytes, options) -> JobRef`
- `docindex.query(doc_id, source_bytes, query, constraints, options) -> PageIndexResult`
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

