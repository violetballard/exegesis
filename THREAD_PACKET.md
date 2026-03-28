## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet update commit: `5d7af2b697f9777f7fd0b182d5c26acd6fc88e3f` `metadata-only`
- Reviewed commit(s):
  - `c4944661a0a682821c486810918c2c1fabac1a41`
  - `c92025af6e11c396f84356967cea704cadb20f5b`

## Scope completed

This handoff is for retrieval behavior only. The current commit updates `THREAD_PACKET.md` as metadata only so packet cleanup stays separate from the reviewed feature delta. The reviewed implementation delta is the FTS-first retrieval MVP code in `c4944661a0a682821c486810918c2c1fabac1a41` and `c92025af6e11c396f84356967cea704cadb20f5b`, which added the source-bundle context regression, payload fallback acceptance, and deterministic excerpt lookup audit context in the retrieval service. PageIndex and embeddings remain deferred as fallback-only plumbing, and the handoff stays limited to the retrieval-owned feature surface aligned to Milestone 3 in `ROADMAP.md` and capability 2 in `PRODUCT_VISION.md`.

## Files changed in the reviewed implementation commits

These entries capture only the retrieval code-bearing paths from the reviewed commits. They exclude packet/tooling artifacts such as `THREAD_PACKET.md` and `.codex/*`.

- `src/qual/engine/retrieval/payload.py`
- `tests/unit/test_unified_retrieval.py`
- `src/qual/retrieval/service.py`

The packet-only commit does not change the reviewed implementation file list above.

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
