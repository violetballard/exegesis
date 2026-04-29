## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip after this metadata-only fixer commit; final HEAD SHA is reported in the fixer response.
- Pre-fixer branch-tip SHA: `cd9b8fce5d91468941da0e3fc05c2fbbaf5162d83`
- Reviewed implementation head: `cd9b8fce5d91468941da0e3fc05c2fbbaf5162d83`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..cd9b8fce5d91468941da0e3fc05c2fbbaf5162d83`
- Handoff classification: high-risk/shared because the range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Shared-file approval provenance: reviewer packet `fixer__feat-retrieval-fts__20260429T202122Z.prompt.txt`, finding 2, identifies `tests/unit/test_unified_retrieval.py` as the approved shared surface for `feat-retrieval-fts`.

## Required Fixes Addressed

1. The full branch-tip implementation through `cd9b8fce5d91468941da0e3fc05c2fbbaf5162d83` is the merge candidate; the handoff no longer narrows review to `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. `Reviewed implementation range`, `Files changed`, `Tasks completed`, and size/budget accounting now match the actual runtime/test implementation diff.
3. Post-`adfa8cda` retrieval changes remain in scope and are mapped below to Milestone 3, retrieval-first context handling, and the canonical demo path.
4. Required gates are re-run against the final merge-candidate working tree and recorded below.
5. This fixer commit is metadata-only, so there is no implementation drift after the stated reviewed implementation head.

## Scope Completed

The branch keeps SQLite FTS as the authoritative retrieval path for the MVP. It adds deterministic excerpt lookup, cache invalidation after document upserts, canonical query and constraint snapshots, stable provenance fingerprints, promotion-ready FTS refs, and sparse source/context/citation bundle rehydration. PageIndex and embeddings remain compatibility or fallback surfaces and are not required retrieval paths.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: make FTS authoritative for excerpt lookup, candidate ranking, document ID normalization, unsupported-scope fail-closed behavior, and stale-cache invalidation after document upserts.
2. Canonical demo-path step `retrieve relevant material`: normalize canonical query text, constraints, date ranges, policy aliases, hit snapshots, source bundles, and provenance fingerprints across retrieval facades.
3. Canonical demo-path steps `retrieve relevant material` and `gather context into basket`: preserve sparse source, context, citation, basket-promotion, and promotion-ready FTS refs so retrieved evidence remains traceable through basket construction.
4. Handoff/review support: keep branch-tip packet metadata, high-risk accounting, and approved shared regression coverage aligned with the full merge candidate.

## Files Changed

Reviewed implementation range:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Runtime/test implementation files in `378cf9a7..cd9b8fce5`:

- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Current metadata-only fixer files: `THREAD_PACKET.md`.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; within the high-risk task cap.
- Reviewed branch-tip file count before this fixer: `7`; within the high-risk 8-file guideline.
- Runtime/test implementation file count: `4`.
- Runtime/test implementation size in `378cf9a7..cd9b8fce5`: `250 insertions(+), 31 deletions(-)`, net `219`; within the high-risk `<=300` guideline.
- Integrator-locked files: none identified in `THREAD_OWNERSHIP.md`.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py`.
- Routing/provider impact: none.

## Roadmap / Vision Mapping

- Roadmap items affected: `ROADMAP.md` Milestone 3 Product Readiness and Milestone 4 Retrieval Layer.
- Vision capabilities affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling, and capability 3, Auditable generation.
- Canonical demo-path step advanced: `retrieve relevant material`, with handoff support for `gather context into basket`.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS, including 125 unit tests.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS, including scope-check, format, lint, typecheck, and 125 unit tests.

## Risks / Blockers

- No implementation blockers are known.
- The tracked mirror packet files under `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still contain stale pre-fixer metadata, but this sandbox rejects writes to those paths with `Operation not permitted`; `THREAD_PACKET.md` is the corrected handoff packet for re-review.
- Re-review should use the full implementation range through `cd9b8fce5d91468941da0e3fc05c2fbbaf5162d83`, plus this metadata-only fixer commit at final HEAD.
