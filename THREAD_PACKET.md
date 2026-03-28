## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet update commit: `893a6264d66dceb184f422debdd4e3b5af0e6c6d` `handoff resubmission` (packet-only)
- Reviewed code commit(s):
  - `c4944661a0a682821c486810918c2c1fabac1a41`
  - `c92025af6e11c396f84356967cea704cadb20f5b`

## Scope completed

This handoff covers the retrieval lane only. The reviewed implementation delta is the FTS-first retrieval MVP in `c4944661a0a682821c486810918c2c1fabac1a41` and `c92025af6e11c396f84356967cea704cadb20f5b`, which adds deterministic excerpt payload rehydration, source-bundle context regression coverage, and excerpt lookup audit context in the retrieval service. PageIndex and embeddings remain deferred as fallback-only plumbing. The work aligns to `Milestone 3: Real workflow loop` in `ROADMAP.md` and `Retrieval-first context handling` in `PRODUCT_VISION.md`.

## Files changed

- `src/qual/engine/retrieval/payload.py`
- `tests/unit/test_unified_retrieval.py`
- `src/qual/retrieval/service.py`

## Tasks completed

1. Accepted source-bundle context fallbacks in the engine payload helpers and verified snapshot safety in regression tests.
2. Added the excerpt lookup audit trail in the retrieval service.
3. Threaded `lookup_entrypoint` through the two public FTS excerpt entrypoints so the audit trail can distinguish them.
4. Recorded `lookup_resolution` in the excerpt audit trail so direct FTS hits and fallback resolution remain distinguishable.

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
