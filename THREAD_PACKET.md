## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Final HEAD SHA (reviewed implementation head): `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Handoff type: branch-level cumulative full-thread retrieval handoff

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- Branch-level cumulative handoff from `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`: SQLite FTS remains authoritative, the canonical retrieval query constructor and `retrieve_auto` helper are exported through both retrieval facades, retrieval payloads/provenance/hit snapshots are deterministic enough for downstream engine flows, sparse source and context bundles rehydrate deterministically, and the excerpt lookup surface now uses the canonical FTS-only path so PageIndex-only excerpt IDs fail closed under shared regression coverage. PageIndex and embeddings remain compatibility-only fallback shims that fail closed.
- The only shared-by-approval edit is `tests/unit/test_unified_retrieval.py`; no other shared-by-approval files are part of the reviewed retrieval implementation range.

## Approved exception note
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract. No other shared-by-approval files are part of the reviewed retrieval implementation range.

## Files changed

### Reviewed implementation files

These are the source files changed across the reviewed cumulative range.

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py` (approved shared regression coverage)

### Reviewed handoff and tooling files

These files keep the cumulative branch-level handoff packet and its generator aligned.

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`

## Tasks completed

1. Added FTS-only excerpt lookup support and deterministic excerpt/provenance output.
2. Canonicalized excerpt provenance so downstream payloads carry stable hashes and fingerprints.
3. Kept retrieval FTS-first, hardened FTS cache isolation, and made excerpt lookup FTS-only while leaving PageIndex and embeddings fallback-only.
4. Exported the canonical retrieval query constructor and `retrieve_auto` helper through both retrieval facades and hardened query normalization.
5. Added source bundle context regression coverage and deterministic rehydration helpers for sparse source and context bundles.
6. Tightened retrieval hit snapshots to carry the canonical `retrieval_source_strategy` alias, list-like provenance fields, and downstream `source_strategy` attribution.
7. Added regression coverage for normalized payload snapshots, facade exports, citation/provenance helpers, and the sparse context backfill path.
8. Canonicalized payload bundle snapshots for deterministic downstream rehydration, including source-bundle fallbacks, source-bundle-only downstream payload reconstruction, sparse context backfill, and direct doc/excerpt/context bundle helper normalization.

## Budget alignment
- The thread finished within the low-risk cap of `8` tasks.
- The reviewed range includes the approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- No other shared or integrator-locked files were edited in the reviewed retrieval implementation.

## Commands run and outcomes
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
- Constraint inputs remain mapping/dataclass-shaped, and iterable `doc_types`/`date_range` values are normalized deterministically by the public retrieval helpers.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (approved `tests/unit/test_unified_retrieval.py` regression coverage only).
