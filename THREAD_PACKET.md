## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed commit(s):
  - `c4944661a0a682821c486810918c2c1fabac1a41`
  - `c92025af6e11c396f84356967cea704cadb20f5b`

## Scope completed

This handoff covers only the reviewed FTS-first retrieval MVP commits: `c4944661a0a682821c486810918c2c1fabac1a41` added the source-bundle context regression and payload fallback acceptance, and `c92025af6e11c396f84356967cea704cadb20f5b` added deterministic excerpt lookup audit context in the retrieval service. PageIndex and embeddings remain deferred as fallback-only plumbing, and the handoff stays limited to the retrieval-owned feature surface.

Packet-only cleanup commits on this branch are not part of the feature delta and are intentionally excluded from the scope summary below.

Coordination artifacts under `.codex/` are excluded from this retrieval handoff and belong to lane planning or packet generation, not the retrieval feature scope.

## Files changed

- `src/qual/engine/retrieval/payload.py`
- `tests/unit/test_unified_retrieval.py`
- `src/qual/retrieval/service.py`

The handoff does not include `.codex/` packet or lane-metadata artifacts.

## Tasks completed

1. Accepted source-bundle context fallbacks in the engine payload helpers and verified snapshot safety in regression tests.
2. Added the excerpt lookup audit trail in the retrieval service.
3. Threaded `lookup_entrypoint` through the two public FTS excerpt entrypoints so the audit trail can distinguish them.
4. Recorded `lookup_resolution` in the excerpt audit trail so direct FTS hits and fallback resolution remain distinguishable.

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

- `ROADMAP.md`: `feat-retrieval-fts` under `MVP Focus Through 2026-05-04`

## Vision capability affected

- 2. Retrieval-first context handling
- 3. Auditable generation

## Routing/provider impact note

- None

## Compatibility note

- PageIndex and embeddings remain fallback-only plumbing behind the FTS-first policy for this MVP; they are not required retrieval paths.

## Scope-check / ownership note

- Shared/integrator-locked edits: `NO`
