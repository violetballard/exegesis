# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: Apply the reviewer-required packet fixes for the retrieval FTS handoff metadata by clearly labeling the docs-only cleanup commit and keeping the reviewed file list aligned with the cleanup diff.
- Reviewed implementation commit: `2c16551a6b3576eb9031d55a98525c21e04be255`
- Reviewed cleanup commit: `300bd4c7053b5fd221d6c87a1be98bf5b5f9bc74`
- Reviewed commit type: Metadata-only cleanup of retrieval handoff packet.
- Scope completed: This cleanup only updates packet metadata. It does not change retrieval runtime behavior, and it does not add or modify `src/qual/engine/retrieval/pageindex_strategy.py` or `src/qual/engine/retrieval/embeddings_strategy.py`; `pageindex` and `embeddings` remain deferred in `FTS_FIRST_POLICY.deferred_strategy_ids` and are not required runtime paths. The packet now separates the implementation history from the docs-only cleanup and keeps the `section:` compatibility note explicit.

### Priority outcomes
1. State clearly that the reviewed commit is docs-only cleanup, not a retrieval code change.
2. Keep the compatibility note for `section:` rejection explicit so the retrieval contract is not overstated.
3. Avoid implying `section:` resolution exists before PageIndex can support concrete section targets.

### Tasks
1. Rewrite the packet scope to distinguish the retrieval implementation history from the docs-only cleanup.
2. Keep the file list aligned with the actual docs-only cleanup diff.
3. Add a standalone scope-completed summary so the packet includes the required handoff outcome field.

### Files changed
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

### Compatibility note
- `section:` queries are intentionally rejected for now; callers should use excerpt or document scopes until PageIndex can resolve concrete section targets.
- `src/qual/engine/retrieval/pageindex_strategy.py` and `src/qual/engine/retrieval/embeddings_strategy.py` are not present in this worktree, so no cleanup changes were made there.
- `pageindex` and `embeddings` stay deferred-only in the FTS-first policy snapshot and do not become required runtime paths for this MVP.

### Guardrails
- Keep the change limited to the retrieval MVP handoff boundary and packet metadata consistency.
- Preserve commit accuracy between the packet, lane metadata, and handoff artifacts.
- Do not imply unrelated retrieval implementation scope or resolved `section:` targeting.
