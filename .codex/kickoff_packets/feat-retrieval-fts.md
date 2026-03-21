# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Reviewed implementation commit: `2c16551a6b3576eb9031d55a98525c21e04be255`
- Reviewed commit type: Retrieval implementation for the FTS-first MVP.
- Scope completed: The retrieval FTS implementation returns deterministic excerpt IDs, serves retrieval-backed `fetch_excerpt()` output, preserves `doc_hits` relevance order for document ranking, and has focused unit coverage for deterministic provenance, document ranking, and retrieval-service excerpt fetch behavior. PageIndex and embeddings remain deferred and are not required MVP paths.

### Related implementation files (reference only)
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Priority outcomes
1. State clearly that the reviewed commit is the retrieval implementation commit, not a docs-only cleanup.
2. Keep the compatibility note for `section:` rejection explicit so the packet does not overstate the retrieval contract.
3. Keep the file list aligned with the retrieval implementation diff.

### Tasks
1. Return deterministic FTS excerpt IDs and retrieval-backed `fetch_excerpt()` output inside the retrieval service.
2. Preserve `doc_hits` relevance order so document-level ranking matches the top-ranked underlying excerpt hit.
3. Add focused unit coverage for deterministic provenance, document ranking order, and retrieval-service excerpt fetch behavior.
4. Complete the handoff metadata required by INTEGRATION.md with concrete scope, file, roadmap, and vision mapping for retrieval-owned MVP FTS work.

### Files changed
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

### Compatibility note
- Temporary compatibility guard: `section:` queries are rejected in the reviewed retrieval implementation because PageIndex cannot resolve concrete section targets yet; PageIndex and embeddings remain deferred and are not required paths for the current FTS-first MVP.

### Guardrails
- Keep the handoff tied to the retrieval implementation commit and its owned-path file set.
- Preserve commit accuracy between the packet, lane metadata, and handoff artifacts.
- Do not imply unrelated retrieval tooling scope or resolved `section:` targeting.
