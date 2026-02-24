# Unified Retrieval Interface Spec

## Goal

- Single retrieval contract for FTS, PageIndex, and embeddings.
- Deterministic auto pipeline with no UI strategy selector.
- Always return actionable excerpt-centric hits for context set assembly.
- PageIndex runs as an internal retrieval strategy inside the existing sidecar process (not a second agent).

## Core Types

- `RetrievalQuery`
- `RetrievalHit`
- `RetrievalResult`

Unified hit shape includes:
- `doc_id`
- `excerpt_id` when available (preferred)
- span (`page_range` or `char_range`)
- `source_strategy` (`fts|pageindex|embeddings`)
- optional `node_path` for PageIndex

## Auto Pipeline

1. Corpus shortlist:
- FTS + embeddings (merged shortlist contract)

2. Within-document deep retrieval:
- PageIndex query for long structured docs with ready index
- doc-scoped fallback to FTS excerpt hits when PageIndex is unavailable

3. Merge and cap:
- Prefer excerpt-backed hits
- de-duplicate by excerpt id
- cap to `constraints.max_results`

## Policy

- Confidential profile is local-only.
- Audit event `retrieval_executed` stores query hash + strategy diagnostics, not raw query text.
- PageIndex strategy must use shared engine services:
  - `PolicyGate`
  - `OpenAICompatClient`
  - `VaultStore`
