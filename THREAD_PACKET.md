## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Final HEAD SHA: `78b27dd3ce244e99e12a336c0719a6e0bfc99a77`
- Reviewed implementation commit(s):
  - `f8a32d372301be4a7c67b97a66ddc8e04f36011f`
  - `c7ca5bcdb3a1b829712c4b3d2f3a39e2bd26c14f`
  - `98ec3f4c0f475308b3ebb528551de923cba549ad`
  - `1c01a74b58888f408e9fa1134a10a29478c6f39a`
  - `cc16c21692b7ca4af9e7866a659b45fc18b87f63`
  - `23e4e4273b8808f5cc5a2f9adab1a7eb2d821b75`

## Scope goal

Build the FTS-first retrieval MVP with deterministic excerpt and provenance output for engine generation flows, aligned to ROADMAP.md Milestone 3: Real workflow loop and PRODUCT_VISION.md capability 2.

## Scope completed

The lane now keeps SQLite FTS as the authoritative retrieval path, exports the canonical retrieval query constructor through both facades, and normalizes downstream retrieval payload snapshots and excerpt fallback rehydration so excerpt and provenance bundles stay deterministic.

## Files changed

These are the exact files changed across the reviewed retrieval implementation commits.

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Tasks completed

1. Added FTS provenance retrieval bundles and retrieval service support for deterministic excerpt/provenance output.
2. Exported the canonical retrieval query constructor through the engine and package facades.
3. Enforced FTS-only hit strategies while keeping PageIndex and embeddings as fallback-only plumbing.
4. Normalized downstream retrieval payload snapshots so tuple-shaped query and policy data rehydrates deterministically.
5. Normalized excerpt fallback rehydration so deterministic excerpt output survives the payload snapshot path.
6. Added regression coverage for the normalized payload snapshots and retrieval facade exports.

## Budget alignment

- The thread finished within the low-risk cap of 8 tasks.
- No shared or integrator-locked files were edited.
- Later metadata-only commits aligned the packet and lane metadata to the current branch tip; they did not change retrieval behavior.

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
