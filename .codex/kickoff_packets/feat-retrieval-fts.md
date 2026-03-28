# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Reviewed commit(s):
  - `70af1c68bfb22d39bb2cd2341f94167ad97b42f7`
  - `b906bc9917cb0a87a031a8f80851e17328697eb5`

## Scope completed

The lane canonicalized the FTS-first retrieval MVP so generation flows receive deterministic excerpt payloads and provenance. PageIndex and embeddings remain deferred as fallback-only plumbing, and this handoff is limited to the retrieval-owned feature surface rather than packet-planner/tooling edits.

### Reviewed implementation files
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/engine/retrieval/policy.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`

### Handoff correction note
- This packet covers the retrieval-owned feature surface only. Packet-planner/tooling edits and any other out-of-lane verification files are split out rather than bundled here.

### Priority outcomes
1. Keep retrieval FTS-first for the MVP.
2. Canonicalize excerpt lookup and provenance payloads for deterministic generation outputs.
3. Keep PageIndex and embeddings deferred as fallback-only plumbing.
4. Keep the handoff scoped to lane-owned retrieval files.

### Tasks
1. Canonicalized FTS excerpt lookup so excerpt rehydration returns deterministic payloads and records an audit trail.
2. Normalized retrieval provenance and downstream payload builders so excerpt, source, citation, doc, and context bundles share stable hashes and fingerprints.
3. Locked the retrieval policy to FTS-first and kept PageIndex/embeddings deferred as fallback-only plumbing.
4. Regenerated the handoff metadata so the packet lists only the retrieval-owned feature surface.

### Files changed
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/engine/retrieval/policy.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`

### Compatibility note
- PageIndex and embeddings remain fallback-only plumbing behind the FTS-first policy for this MVP; they are not required retrieval paths.

### Guardrails
- Keep the handoff tied to the retrieval implementation and its lane-owned file set.
- Preserve commit accuracy between the packet, lane metadata, and handoff artifacts.
- Do not imply cross-lane `section:` targeting.
- Ownership note: this handoff stays within `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`.

### Scope-check / ownership note
- No non-retrieval tooling edits are approved for this handoff.
- No out-of-lane tooling files are included in this resubmission.
