## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Final HEAD SHA: `cc16c21692b7ca4af9e7866a659b45fc18b87f63`
- Reviewed implementation commit(s):
  - `cc16c21692b7ca4af9e7866a659b45fc18b87f63`

## Scope goal

Normalize retrieval payload snapshots so query, policy, provenance, and derived bundles remain deterministic across engine retrieval flows.

## Scope completed

This handoff covers the payload-snapshot normalization patch under review.

- Canonicalized tuple- and list-shaped query constraint and strategy fields when rebuilding retrieval payload snapshots.
- Normalized derived source and provenance bundles so downstream payload consumers see stable list-like values.
- Added regression coverage for tuple-shaped query, policy, and provenance snapshots in the retrieval payload helpers.

## Files changed

These are the exact files changed by the reviewed commit.

- `src/qual/engine/retrieval/payload.py`
- `tests/unit/test_unified_retrieval.py`

## Tasks completed

1. Normalized list-like retrieval payload fields so derived bundles stay deterministic across payload rebuilds.
2. Added regression coverage for tuple-shaped query, policy, and provenance snapshots in retrieval payload helpers.

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

- `ROADMAP.md`: `Milestone 3: Product Readiness (Planned)`

## Vision capability affected

- 2. Retrieval-first context handling
- 3. Auditable generation

## Routing/provider impact note

- None

## Compatibility note

- PageIndex and embeddings remain fallback-only plumbing behind the FTS-first policy for this MVP; they are not required retrieval paths.

## Scope-check / ownership note

- Shared/integrator-locked edits: `NO`
