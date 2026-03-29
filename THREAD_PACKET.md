## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Final HEAD SHA: `7dbd062c7b98e28963a87ea00d8fd7906b752094`
- Reviewed implementation commit(s):
  - `175ebc8a7484db1edaede05ac2f98d7715b4eb66`
  - `c92025af6e11c396f84356967cea704cadb20f5b`
  - `c4944661a0a682821c486810918c2c1fabac1a41`
  - `47b3977d271e3f7faacb6ba3082ab94a2d327fcb`
  - `7dbd062c7b98e28963a87ea00d8fd7906b752094`

## Scope goal

Keep the FTS-first retrieval lane scoped to deterministic excerpt and provenance output for engine generation flows, with PageIndex and embeddings deferred as fallback-only plumbing.

## Scope completed

This handoff covers the retrieval lane only.

- Added excerpt lookup audit context and deterministic excerpt payload rehydration in the retrieval service.
- Added source-bundle context regression coverage and canonical query export through the engine and package retrieval facades.
- Added citation-bundle export through the same retrieval entrypoints.
- Added retrieval-constraint object support through the same engine and package facades, with regression coverage for the dataclass-shaped constraints path.
- Kept the canonical retrieval package as the source of truth while exposing stable engine-side facades.
- Kept PageIndex and embeddings deferred as fallback-only plumbing rather than required paths.
- Kept the work aligned to `Milestone 3: Real workflow loop` in `ROADMAP.md` and `Retrieval-first context handling` in `PRODUCT_VISION.md`.
- Excluded packet-planner/tooling artifacts from this handoff; those belong in a separate review packet.

Implementation file mapping:

- `c92025af6e11c396f84356967cea704cadb20f5b` -> `src/qual/retrieval/service.py`
- `c4944661a0a682821c486810918c2c1fabac1a41` -> `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `47b3977d271e3f7faacb6ba3082ab94a2d327fcb` -> `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `7dbd062c7b98e28963a87ea00d8fd7906b752094` -> `src/qual/engine/retrieval/__init__.py`, `src/qual/retrieval/__init__.py`, `tests/unit/test_unified_retrieval.py`

## Files changed

These are the reviewed retrieval code files only, deduplicated across the reviewed implementation commits.

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
5. Exported the auto retrieval citation bundle through both retrieval facades.
6. Accepted retrieval-constraint objects in both retrieval facades and added regression coverage for the dataclass-shaped constraints path.

## Budget alignment

- The thread finished within the low-risk cap of 8 tasks.
- No shared or integrator-locked files were edited.

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

## Vision capability affected

- 2. Retrieval-first context handling
- 6. Auditable state and workflow

## Routing/provider impact note

- None

## Compatibility note

- PageIndex and embeddings remain fallback-only plumbing behind the FTS-first policy for this MVP; they are not required retrieval paths.

## Scope-check / ownership note

- Shared/integrator-locked edits: `NO`
