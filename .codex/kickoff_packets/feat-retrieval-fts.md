# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: Apply the reviewer-required packet fixes for the retrieval FTS MVP handoff by separating feature code files from handoff artifacts and documenting the `section:` compatibility boundary.
- Reviewed implementation commit: `2c16551a6b3576eb9031d55a98525c21e04be255`
- Reviewed commit type: Retrieval FTS handoff alignment.
- Scope completed: The retrieval FTS MVP work stays in retrieval-owned code paths, with FTS as the only active runtime strategy. `pageindex` and `embeddings` remain deferred in `FTS_FIRST_POLICY.deferred_strategy_ids`, so they are not required runtime paths. The packet now lists handoff artifacts separately so the ownership boundary is explicit, and `section:` queries remain rejected as a compatibility safeguard until PageIndex can resolve concrete section targets.

### Priority outcomes
1. State clearly that the packet separates feature code files from handoff artifacts.
2. Keep the compatibility note for `section:` rejection explicit so the retrieval contract is not overstated.
3. Avoid implying `section:` resolution exists before PageIndex can support concrete section targets.

### Tasks
1. Rewrite the packet scope to distinguish retrieval feature code files from handoff artifacts.
2. Keep the file list aligned with the retrieval MVP handoff while preserving the boundary between code and packet metadata.
3. Add a compatibility note so the packet does not imply broader retrieval-contract changes than the roadmap authorizes.

### Files changed
- Feature code files:
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Handoff artifacts:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`

### Compatibility note
- `section:` queries are intentionally rejected for now; callers should use excerpt or document scopes until PageIndex can resolve concrete section targets.
- `pageindex` and `embeddings` stay deferred-only in the FTS-first policy snapshot and do not become required runtime paths for this MVP.

### Guardrails
- Keep the change limited to the retrieval MVP handoff boundary and packet metadata consistency.
- Preserve commit accuracy between the packet, lane metadata, and handoff artifacts.
- Do not imply unrelated retrieval implementation scope or resolved `section:` targeting.
