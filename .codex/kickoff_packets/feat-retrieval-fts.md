# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: Apply the reviewer-required packet fixes for the retrieval FTS handoff metadata by clearly labeling the docs-only cleanup commit, while naming the related FTS implementation files in a separate reference set.
- Reviewed cleanup commit: `300bd4c7053b5fd221d6c87a1be98bf5b5f9bc74`
- Related implementation commit: `2c16551a6b3576eb9031d55a98525c21e04be255`
- Reviewed commit type: Metadata-only cleanup of retrieval handoff packet.
- Scope completed: The related retrieval FTS implementation returns deterministic excerpt IDs, serves retrieval-backed `fetch_excerpt()` output, preserves `doc_hits` relevance order for document ranking, and has focused unit coverage for provenance and service behavior. This cleanup only updates packet metadata so the handoff points at that implementation cleanly, and it keeps PageIndex/embeddings deferred rather than required MVP paths.

### Related implementation files (reference only)
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Priority outcomes
1. State clearly that the reviewed commit is docs-only cleanup, not a retrieval code change.
2. Keep the compatibility note for `section:` rejection explicit so the packet does not overstate the retrieval contract.
3. Keep the file list aligned with the docs-only cleanup diff.

### Tasks
1. Rewrite the packet scope so it no longer implies retrieval implementation changes.
2. Keep the file list aligned with the docs-only cleanup diff.
3. Add a standalone scope-completed summary so the packet includes the required handoff outcome field.

### Files changed
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

### Compatibility note
- Temporary compatibility guard: `section:` queries are rejected in the reviewed retrieval implementation because PageIndex cannot resolve concrete section targets yet; PageIndex and embeddings remain deferred and are not required paths for the current FTS-first MVP.

### Guardrails
- Keep the change limited to the handoff metadata boundary and commit-label consistency.
- Preserve commit accuracy between the packet, lane metadata, and handoff artifacts.
- Do not imply unrelated retrieval implementation scope or resolved `section:` targeting.
