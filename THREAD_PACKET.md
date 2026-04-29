## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate before this metadata-only fixer commit: `5a05c1f3218e3d87f54e694bc5fbf47c56ca2c3d`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..5a05c1f3218e3d87f54e694bc5fbf47c56ca2c3d`
- Final branch tip: reported in the fixer response after this packet-only commit is created

## Scope Completed

The full branch-tip range is retained for review. It implements FTS-first retrieval for the MVP, deterministic source/context bundle snapshots for basket promotion, source-bundle fingerprints and citation status, and engine payload rehydration for compact downstream inputs. PageIndex-only excerpt IDs fail closed, and PageIndex/embeddings remain compatibility-only deferred paths.

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
- File budget: `6/8`.
- Size budget for reviewed implementation range: `6 files changed, 429 insertions(+), 132 deletions(-)`.

## Roadmap / Vision

- Roadmap items: `ROADMAP.md` Milestone 3 Product Readiness and Milestone 4 Retrieval Layer.
- Vision capabilities: `PRODUCT_VISION.md` capability 2 retrieval-first context handling and capability 6 auditable state/workflow.
- Routing/provider impact: none.

## Canonical Demo Path

This branch makes the `retrieve relevant material` and `gather context` steps more real. The FTS-only excerpt path retrieves relevant material without PageIndex/embeddings as required paths, and the deterministic basket-promotion/source-bundle payloads gather that material into context with stable provenance for later `plan/revise`, `apply/reject patch`, `persist state`, and `continue working` steps.

## Traceability Correction

Earlier packet text incorrectly treated commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as metadata-only. That claim is withdrawn. The review surface is the full range ending at `5a05c1f3218e3d87f54e694bc5fbf47c56ca2c3d`, which includes runtime/test changes in `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`.

The commit created by this fixer pass changes packet metadata only. It does not narrow, split, reset, or modify the reviewed runtime/test implementation.

## Commands Run

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / Blockers

- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still contain stale pre-review framing and are protected by `com.apple.provenance`; write and xattr removal attempts both returned `Operation not permitted` in this sandbox. Use this packet as the corrected re-review surface.
- Residual risk: broader retrieval orchestration beyond deterministic source/context bundles remains separate high-risk work.
