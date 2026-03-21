# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Feature implementation commit: `36893f06df85409c4595d64adb8af60455c086a6`
- Deferred-policy cleanup commit: `dc8f79e4abeb30de51854fdd84d35b97993955b8`
- Handoff alignment commit: `203906231e9c47371b6d7bc4028bc4f60e764581`
- Reviewed commit type: Retrieval feature implementation with deferred-policy cleanup.

## Scope completed

Delivered behavior: FTS-first retrieval is active for `vault`, `collection:`, and `doc:` scopes. `src/qual/retrieval/service.py` forwards those queries to the owned retrieval engine, `src/qual/engine/retrieval/__init__.py` exposes the canonical retrieval surface, and `src/qual/engine/retrieval/policy.py` keeps `fts` active while leaving `pageindex` and `embeddings` deferred. `section:` remains rejected until fallback support exists. The handoff files are limited to `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`.

### Prior commit references (reference only)
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/retrieval/service.py`

### Cleanup boundary note
- `src/qual/engine/retrieval/policy.py`

### Code-diff evidence
- `src/qual/engine/retrieval/__init__.py`: exposes the canonical FTS-first retrieval surface.
- `src/qual/retrieval/service.py`: routes retrieval queries through the FTS-first engine path.
- `src/qual/engine/retrieval/policy.py`: defines the active FTS strategy and deferred strategies.
- Roadmap/vision mapping: documents the Milestone 4 retrieval boundary while keeping `PageIndex` and embeddings out of the required MVP path.

### Priority outcomes
1. Keep the handoff tied to the lane-owned retrieval paths only.
2. Keep the reviewed file list constrained to the lane-owned retrieval paths.
3. Treat `PageIndex` and embeddings mentions as deferred markers only, not active MVP paths.
4. Make the roadmap and vision fields read as delivered retrieval behavior, not a provider or routing change.

### Tasks
1. Re-anchor the packet to the retrieval feature commit and keep the lane-owned file list narrow.
2. Keep the handoff surface within the lane-owned retrieval paths only.
3. Add a concrete scope-completed summary that explains the delivered FTS-first behavior.
4. Preserve the roadmap and vision mapping while keeping `PageIndex` and embeddings deferred.
5. Document the `section:` compatibility boundary as an intentional MVP limitation until fallback support is restored.

### Files changed
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/policy.py`

### Compatibility note
- Breaking compatibility note: `section:` scopes are intentionally rejected in the owned retrieval service until section fallback support exists. Callers that depend on section targeting must switch to `vault`, `collection:`, or `doc:` scopes for the current FTS-first MVP path.

### Guardrails
- Keep the handoff tied to the retrieval implementation and its lane-owned file set.
- Preserve commit accuracy between the packet, lane metadata, and handoff artifacts.
- Do not imply unrelated retrieval tooling scope or cross-lane `section:` targeting.
- Ownership note: this handoff stays within `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`.
