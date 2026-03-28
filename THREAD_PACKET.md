## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed code commit(s):
  - `47b3977d271e3f7faacb6ba3082ab94a2d327fcb`

## Scope completed

This handoff covers the retrieval lane only. The reviewed implementation delta is the FTS-first retrieval MVP in `47b3977d271e3f7faacb6ba3082ab94a2d327fcb`, which adds deterministic excerpt payload rehydration, source-bundle context regression coverage, excerpt lookup audit context in the retrieval service, and canonical query constructor export through both retrieval facades. PageIndex and embeddings remain deferred as fallback-only plumbing. The reviewed file list below is commit-accurate and excludes packet/tooling metadata edits from the feature delta. The work aligns to `Milestone 3: Real workflow loop` in `ROADMAP.md` and `Retrieval-first context handling` in `PRODUCT_VISION.md`.

## Files changed

These are the reviewed code files only.

- `src/qual/engine/retrieval/payload.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/retrieval/__init__.py`
- `tests/unit/test_unified_retrieval.py`
- `src/qual/retrieval/service.py`

## Tasks completed

1. Accepted source-bundle context fallbacks in the engine payload helpers and verified snapshot safety in regression tests.
2. Added the excerpt lookup audit trail in the retrieval service.
3. Exported the canonical retrieval query constructor through both the engine and package facades.
4. Added regression coverage for source bundle fallback, canonical query sharing, and package re-exports.

## Commands run with results

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks/blockers

- Risk: `LOW`
- Blockers: none

## Roadmap item(s) affected

- `ROADMAP.md`: `Milestone 3: Real workflow loop`
- `docs/TASKS.md`: `feat-retrieval-fts`
- `THREAD_OWNERSHIP.md`: `codex/feat-retrieval-fts*`

## Vision capability affected

- 2. Retrieval-first context handling
- 6. Auditable state and workflow

## Routing/provider impact note

- None

## Compatibility note

- PageIndex and embeddings remain fallback-only plumbing behind the FTS-first policy for this MVP; they are not required retrieval paths.

## Scope-check / ownership note

- Shared/integrator-locked edits: `NO`
