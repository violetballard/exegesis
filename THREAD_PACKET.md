## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed commit(s):
  - `70af1c68bfb22d39bb2cd2341f94167ad97b42f7`
  - `b906bc9917cb0a87a031a8f80851e17328697eb5`
  - `addc72aead4d458748f06497865deef9ab54db26`

## Scope completed

The lane canonicalized the FTS-first retrieval MVP so generation flows receive deterministic excerpt payloads and provenance, matching PRODUCT_VISION.md capability 2, Retrieval-first context handling, and capability 6, Auditable state and workflow. PageIndex and embeddings remain deferred as fallback-only plumbing, and this handoff stays limited to the retrieval-owned feature surface.

## Files changed

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/engine/retrieval/policy.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`

## Tasks completed

1. Canonicalized FTS excerpt lookup so excerpt rehydration returns deterministic payloads and records an audit trail.
2. Normalized retrieval provenance and downstream payload builders so excerpt, source, citation, doc, and context bundles share stable hashes and fingerprints.
3. Locked the retrieval policy to FTS-first and kept PageIndex/embeddings deferred as fallback-only plumbing.
4. Exposed the canonical retrieval entrypoints through the engine/package facades so the FTS-first path remains the stable default.

## Commands run and outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Risk: `LOW`
- Blockers: none

## Roadmap item(s) affected

- ROADMAP.md: Milestone 3: Real workflow loop
- docs/TASKS.md: feat-retrieval-fts -> keep the FTS-first retrieval path authoritative; expose retrieval through the canonical engine contract; keep structured results suitable for deterministic retrieval-backed generation

## Vision capability affected

- PRODUCT_VISION.md: 2. Retrieval-first context handling
- PRODUCT_VISION.md: 6. Auditable state and workflow

## Routing/provider impact note

- None

## Compatibility note

- PageIndex and embeddings remain fallback-only plumbing behind the FTS-first policy for this MVP; they are not required retrieval paths.

## Scope-check / ownership note

- Shared/integrator-locked edits: `NO`
