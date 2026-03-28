# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Reviewed commit(s):
  - `70af1c68bfb22d39bb2cd2341f94167ad97b42f7`
  - `b906bc9917cb0a87a031a8f80851e17328697eb5`

## Scope completed

The lane canonicalized the FTS-first retrieval MVP so generation flows receive deterministic excerpt payloads and provenance, matching PRODUCT_VISION.md capability 2, Retrieval-first context handling, and capability 6, Auditable state and workflow. PageIndex and embeddings remain deferred as fallback-only plumbing, and this handoff is limited to the retrieval-owned feature surface rather than packet-planner/tooling edits.

### Roadmap / vision mapping
- ROADMAP.md: Milestone 3: Real workflow loop
- docs/TASKS.md: feat-retrieval-fts -> keep the FTS-first retrieval path authoritative; expose retrieval through the canonical engine contract; keep structured results suitable for workflow cards and basket promotion
- PRODUCT_VISION.md: 2. Retrieval-first context handling
- PRODUCT_VISION.md: 6. Auditable state and workflow

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
