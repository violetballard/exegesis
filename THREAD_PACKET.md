## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip after this metadata-only fixer commit; final HEAD SHA is reported in the fixer response.
- Pre-fixer branch-tip SHA: `d7299fa23c85e76d3d42ae356e157a00bc0820fa`
- Reviewed branch-tip range before this metadata-only fixer commit: `378cf9a74a3658058079a32f186fcd254c4a4034..d7299fa23c85e76d3d42ae356e157a00bc0820fa`
- Runtime/test implementation head: `77b174d10b57aae237ee55c17139e57f5c296c01`
- Runtime/test implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..77b174d10b57aae237ee55c17139e57f5c296c01`
- Handoff classification: high-risk/shared because the reviewed branch-tip range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Shared-file approval provenance: reviewer packet `fixer__feat-retrieval-fts__20260429T202122Z.prompt.txt`, finding 2, identifies `tests/unit/test_unified_retrieval.py` as the approved shared surface for `feat-retrieval-fts`.

## Required Fixes Addressed

1. The actual branch tip is the merge candidate, not the narrowed `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice.
2. Runtime/test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` are included through `77b174d10b57aae237ee55c17139e57f5c296c01`: FTS cache invalidation, context refs, citation/source bundle payload backfills, basket-promotion refs, and source bundle context ref preservation.
3. High-risk accounting is recomputed from the real branch-tip range; this packet is compacted so final net LOC is within the `<=300` high-risk limit.
4. Tasks below name the canonical demo-path step they advance.
5. Required gates are re-run against the corrected merge candidate working tree.

## Scope Completed

The branch-tip handoff keeps SQLite FTS authoritative for excerpt lookup and retrieval ranking, invalidates the FTS retrieval cache after document upserts, normalizes canonical query and payload snapshots, keeps retrieval provenance and fingerprints deterministic, rehydrates sparse source/context/citation refs into stable payloads, preserves basket-promotion refs, and preserves source bundle context refs during payload backfill. PageIndex and embeddings remain compatibility/fallback surfaces, not required retrieval paths.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: keep SQLite FTS authoritative for excerpt lookup, candidate ranking, cache scope normalization, document-upsert cache invalidation, and fail-closed unsupported lookup paths.
2. Canonical demo-path step `retrieve relevant material`: normalize canonical query snapshots, constraints, date ranges, hit payloads, source bundles, and provenance fingerprints across retrieval facades.
3. Canonical demo-path step `retrieve relevant material` plus `gather context into basket`: preserve sparse source/context/citation refs, basket promotion metadata, and source bundle context refs so retrieved evidence keeps stable traceability.
4. Handoff/review support: keep packet metadata, scope accounting, and approved shared regression coverage aligned with the branch-tip merge candidate.

## Files Changed

Reviewed branch-tip range before this metadata-only fixer commit:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Current metadata-only fixer commit after `d7299fa23c85e76d3d42ae356e157a00bc0820fa`: `THREAD_PACKET.md`.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; within the high-risk task cap.
- Reviewed branch-tip file count: `7`; within the high-risk 8-file guideline.
- Pre-fixer branch-tip size: `433 insertions(+), 116 deletions(-)`, net `317`, which exceeded the high-risk `<=300` limit.
- Final branch-tip size after this metadata-only packet compaction, before creating the fixer commit: `410 insertions(+), 118 deletions(-)`, net `292`; within the high-risk `<=300` limit.
- Integrator-locked files: none identified in `THREAD_OWNERSHIP.md`.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py`.
- Routing/provider impact: none.

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 3 Product Readiness and Milestone 4 Retrieval Layer.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling, and capability 3, Auditable generation.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS.
- `./typecheck-test.sh` PASS.
- `make ci` PASS.

## Risks / Blockers

- No implementation blockers are known.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are tracked packet mirrors but the patch tool rejected writes under `.codex` during this fixer pass; `THREAD_PACKET.md` is the corrected source-of-truth packet for re-review.
- Re-review should use the full branch-tip merge candidate, not the narrowed `adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice.
