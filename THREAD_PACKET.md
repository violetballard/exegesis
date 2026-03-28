## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed commit(s):
  - `70af1c68bfb22d39bb2cd2341f94167ad97b42f7`
  - `b906bc9917cb0a87a031a8f80851e17328697eb5`

## Scope completed

The lane canonicalized the FTS-first retrieval MVP so deterministic excerpt payloads and provenance now come from `src/qual/retrieval/service.py`, matching PRODUCT_VISION.md capability 2, Retrieval-first context handling, and capability 3, Auditable generation. PageIndex and embeddings remain deferred as fallback-only plumbing, and this handoff stays limited to the retrieval-owned feature surface.

## Files changed

- `src/qual/retrieval/service.py`

## Tasks completed

1. Added the excerpt lookup audit trail and deterministic rehydration path in the retrieval service.
2. Canonicalized excerpt provenance so downstream payloads carry stable hashes and fingerprints.
3. Kept retrieval FTS-first and left PageIndex/embeddings as fallback-only plumbing.

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

- Milestone 4: Retrieval Layer (Planned)

## Vision capability affected

- 2. Retrieval-first context handling
- 3. Auditable generation

## Routing/provider impact note

- None

## Compatibility note

- PageIndex and embeddings remain fallback-only plumbing behind the FTS-first policy for this MVP; they are not required retrieval paths.

## Scope-check / ownership note

- Shared/integrator-locked edits: `NO`
