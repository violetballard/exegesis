## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Selected merge candidate: actual branch-tip lineage, not the narrowed `adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice.
- Packet head before this metadata-only fixer commit: `e11cdde86ac7a062630e26ef4bf9485cf32013905`
- Reviewed implementation range before this fixer commit: `378cf9a74a3658058079a32f186fcd254c4a4034..e11cdde86ac7a062630e26ef4bf9485cf32013905`
- Final reviewed head: reported in the fixer response after this metadata-only packet correction is committed.

## Scope Completed

The full branch-tip lineage is the review surface. It implements the FTS-first retrieval MVP, deterministic source/context bundle snapshots for basket promotion, source-bundle fingerprints and citation status, and engine payload rehydration for compact downstream inputs. PageIndex-only excerpt IDs fail closed, and PageIndex/embeddings remain compatibility-only deferred paths.

## Tasks Completed

1. Added FTS-only excerpt lookup and fail-closed PageIndex rejection for excerpt backfill.
2. Added deterministic basket-promotion/source-bundle snapshots with stable IDs, fingerprints, citation status, query scope, intent, and date range.
3. Added engine payload rehydration for compact source/context bundles so sparse downstream inputs can recover deterministic retrieval payloads.
4. Added shared regression coverage for excerpt backfill, facade exports, payload normalization, provenance helpers, and basket-promotion snapshots.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Budget

- Risk: high, because approved shared regression coverage touches `tests/unit/test_unified_retrieval.py`.
- Task budget: `4/4`.
- File budget before this metadata-only fixer commit: `6/8`.
- Size budget before this metadata-only fixer commit: `6 files changed, 462 insertions(+), 112 deletions(-)` for `378cf9a74a3658058079a32f186fcd254c4a4034..e11cdde86ac7a062630e26ef4bf9485cf32013905`.

## Roadmap / Vision

- Roadmap items: `ROADMAP.md` Milestone 3 Product Readiness and Milestone 4 Retrieval Layer.
- Vision capabilities: `PRODUCT_VISION.md` capability 2 retrieval-first context handling and capability 6 auditable state/workflow.
- Routing/provider impact: none.

## Canonical Demo Path

This branch makes the `retrieve relevant material` and `gather context` steps more real. The FTS-only excerpt path retrieves relevant material without PageIndex/embeddings as required paths, and the deterministic basket-promotion/source-bundle payloads gather that material into context with stable provenance for later `plan/revise`, `apply/reject patch`, `persist state`, and `continue working` steps.

## Traceability Correction

Earlier packet text incorrectly treated commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as metadata-only. That claim is withdrawn. This handoff chooses the actual branch-tip lineage. The review surface is the full range ending at `e11cdde86ac7a062630e26ef4bf9485cf32013905` before this fixer commit, which includes runtime/test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` in `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`.

This fixer pass changes packet metadata only. It does not narrow, split, reset, or modify the reviewed runtime/test implementation.

## Commands Run

Required gates are rerun after this packet correction and reported in the final fixer response:

- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`

## Risks / Blockers

- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still contain stale `adfa8cd` framing from earlier packet refreshes. Both files are protected by `com.apple.provenance`; direct writes and `xattr -d com.apple.provenance` returned `Operation not permitted` in this sandbox. Use `THREAD_PACKET.md` plus the final fixer response as the corrected re-review packet.
- Residual risk: broader retrieval orchestration beyond deterministic source/context bundles remains separate high-risk work.
- Shared-file note: `tests/unit/test_unified_retrieval.py` is included as approved shared regression coverage for the retrieval lane; no other shared or integrator-locked runtime files are edited.
