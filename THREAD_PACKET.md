## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Final HEAD SHA: `7dbd062c7b98e28963a87ea00d8fd7906b752094`
- Reviewed implementation commit(s):
  - `7dbd062c7b98e28963a87ea00d8fd7906b752094`

## Scope goal

Accept `RetrievalConstraints` objects in the retrieval query constructors while preserving the canonical engine/package retrieval facade behavior.

## Scope completed

This handoff covers the exact constraints-object patch under review.

- Extended the engine retrieval query constructor to accept `RetrievalConstraints` objects directly.
- Updated the public retrieval facade to accept the same constraints object shape and forward it through the canonical engine path.
- Added regression coverage for the dataclass-shaped constraints path and verified both facades construct equivalent queries.

## Files changed

These are the exact files changed by the reviewed commit.

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/retrieval/__init__.py`
- `tests/unit/test_unified_retrieval.py`

## Tasks completed

1. Extended `build_retrieval_query` in the engine retrieval facade to accept `RetrievalConstraints` objects alongside mappings.
2. Updated the public retrieval facade to accept `RetrievalConstraints` objects and route them through the canonical engine constructor.
3. Added regression coverage for the dataclass-shaped constraints path so both facades stay equivalent.

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
