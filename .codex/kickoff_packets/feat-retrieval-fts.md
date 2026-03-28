# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Handoff type: packet correction only; this commit updates handoff metadata, not retrieval code.
- Reviewed commit(s):
  - `70af1c68bfb22d39bb2cd2341f94167ad97b42f7`
  - `b906bc9917cb0a87a031a8f80851e17328697eb5`

## Scope completed

The lane canonicalized the FTS-first retrieval MVP so generation flows receive deterministic excerpt payloads and provenance, matching PRODUCT_VISION.md capability 2, Retrieval-first context handling, and capability 6, Auditable state and workflow. PageIndex and embeddings remain deferred as fallback-only plumbing, and this resubmission stays limited to the retrieval-owned feature surface. Packet-planner/tooling edits are not part of this handoff.

### Roadmap / vision mapping
- ROADMAP.md: Milestone 4: Retrieval Layer (Planned)
- PRODUCT_VISION.md: 2. Retrieval-first context handling
- PRODUCT_VISION.md: 6. Auditable state and workflow

### Implementation surface validated by the lane
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/engine/retrieval/policy.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`

### Handoff correction note
- This packet correction only updates handoff metadata. The retrieval implementation itself remains in the earlier lane commits listed above.

### Priority outcomes
1. Keep retrieval FTS-first for the MVP.
2. Canonicalize excerpt lookup and provenance payloads for deterministic generation outputs.
3. Keep PageIndex and embeddings deferred as fallback-only plumbing.
4. Keep the handoff scoped to lane-owned retrieval files.

### Tasks
1. Canonicalized FTS excerpt lookup so excerpt rehydration returns deterministic payloads and records an audit trail.
2. Normalized retrieval provenance and downstream payload builders so excerpt, source, citation, doc, and context bundles share stable hashes and fingerprints.
3. Locked the retrieval policy to FTS-first and kept PageIndex/embeddings deferred as fallback-only plumbing.
4. Exposed the canonical retrieval entrypoints through the engine/package facades so the FTS-first path remains the stable default.

### Files changed
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

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
