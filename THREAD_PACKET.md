## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip after this metadata-only fixer commit.
- Branch-tip SHA before this metadata fix: `d7299fa23c87612f4b0cf4d37dc4b0ae57c4981f`
- Reviewed branch-tip range: `378cf9a74a3658058079a32f186fcd254c4a4034..d7299fa23c87612f4b0cf4d37dc4b0ae57c4981f`
- Runtime/test implementation head: `77b174d10b57aae237ee55c17139e57f5c296c01`
- Runtime/test implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..77b174d10b57aae237ee55c17139e57f5c296c01`
- Packet refresh note: this packet keeps the actual branch-tip merge candidate. Runtime/test implementation changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` are included through `77b174d10b57aae237ee55c17139e57f5c296c01`; later commits through `d7299fa23c87612f4b0cf4d37dc4b0ae57c4981f` are packet metadata refreshes. This fixer commit changes packet metadata only; the final HEAD SHA is reported in the fixer response.
- Handoff classification: high-risk/shared because the reviewed implementation includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Shared-file approval provenance: reviewer packet `fixer__feat-retrieval-fts__20260429T202122Z.prompt.txt`, finding 2, identifies `tests/unit/test_unified_retrieval.py` as the approved shared surface for `feat-retrieval-fts`.

## Required Fixes Addressed

1. Chose the actual branch tip as the intended merge candidate and regenerated the packet around branch-tip range `378cf9a74a3658058079a32f186fcd254c4a4034..d7299fa23c87612f4b0cf4d37dc4b0ae57c4981f`.
2. Included every implementation commit after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` in the reviewed range, including FTS cache invalidation, context refs, citation/source bundle payload backfills, basket-promotion refs, and source bundle context ref preservation.
3. Recomputed tasks, scope completed, files changed, risk, and budget accounting against `378cf9a74a3658058079a32f186fcd254c4a4034..d7299fa23c87612f4b0cf4d37dc4b0ae57c4981f`.
4. Re-ran the required gates against the corrected merge candidate working tree; results are reported below.
5. Re-stated plan alignment against `ROADMAP.md` Milestone 3 and `PRODUCT_VISION.md` retrieval-first context handling for the full implementation.
6. Re-stated the canonical demo-path step advanced by the full branch-tip work.

## Scope Completed

The reviewed branch-tip range ships the cumulative FTS-first retrieval handoff through `d7299fa23c87612f4b0cf4d37dc4b0ae57c4981f`. The runtime/test implementation portion through `77b174d10b57aae237ee55c17139e57f5c296c01` keeps SQLite FTS authoritative for excerpt lookup and retrieval ranking, invalidates the FTS retrieval cache after document upserts, normalizes canonical query and payload snapshots, keeps retrieval provenance and fingerprints deterministic, rehydrates sparse source/context/citation refs into stable payloads, preserves basket-promotion refs, and preserves source bundle context refs during payload backfill. PageIndex and embeddings remain compatibility/fallback surfaces, not required retrieval paths.

## Canonical Demo-Path Mapping

- Demo-path step advanced: `retrieve relevant material`.
- Basket/context step advanced: retrieved source, citation, context, and basket-promotion refs are preserved in payload/provenance snapshots so relevant material can be gathered or promoted into the basket without losing traceability.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: keep SQLite FTS authoritative for excerpt lookup, candidate ranking, cache scope normalization, FTS cache invalidation after document upserts, and fail-closed unsupported lookup paths.
2. Canonical demo-path step `retrieve relevant material`: normalize canonical query snapshots, constraints, date ranges, hit payloads, source bundles, and provenance fingerprints across the retrieval and engine retrieval facades.
3. Canonical demo-path step `retrieve relevant material` plus basket handoff: preserve sparse source/context/citation refs, basket promotion metadata, and source bundle context refs so retrieved evidence can be gathered into downstream context with stable traceability.
4. Handoff/review support: update packet planner metadata support and shared regression coverage for the FTS-first retrieval contract, payload normalization, facade exports, excerpt backfill, FTS cache invalidation, context-ref payloads, and source-bundle backfill behavior.

## Files Changed

Reviewed branch-tip range `378cf9a74a3658058079a32f186fcd254c4a4034..d7299fa23c87612f4b0cf4d37dc4b0ae57c4981f`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` branch-tip implementation slice included in this handoff:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Current metadata-only fixer commit after `d7299fa23c87612f4b0cf4d37dc4b0ae57c4981f`:

- `THREAD_PACKET.md`

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; passes the high-risk task cap as a summarized cumulative handoff.
- Reviewed branch-tip file count: `7` files, within the high-risk 8-file size guideline.
- Reviewed branch-tip size: `433 insertions(+), 116 deletions(-)`, above the high-risk 300 net LOC guideline; this must be reviewed as an accumulated branch-tip handoff rather than a narrow metadata refresh.
- Post-`adfa8cd` branch-tip slice: `7` files, `405 insertions(+), 85 deletions(-)`, and is included in this handoff.
- Integrator-locked files: none identified in `THREAD_OWNERSHIP.md`.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py`, used for canonical retrieval regression coverage.
- Routing/provider impact: none.

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 3 Product Readiness: retrieval evidence and provenance shape the output contract needed before drafting/diff generation can be release-ready.
- Roadmap item affected: `ROADMAP.md` Milestone 4 Retrieval Layer: FTS-first retrieval and source attribution for retrieved chunks, with PageIndex/embeddings deferred until after the demo push.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling.
- Vision capability affected: `PRODUCT_VISION.md` capability 3, Auditable generation.
- Proposed `README.md` patch text: none.

## Commands Run

Fresh fixer pass on `2026-04-29` after regenerating the reviewed branch-tip range through `d7299fa23c87612f4b0cf4d37dc4b0ae57c4981f`:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS.
- `./typecheck-test.sh` PASS.
- `make ci` PASS.

## Risks / Blockers

- No implementation blockers are known.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are tracked packet mirrors but were rejected by the patch tool as outside permitted project scope during this fixer pass. `THREAD_PACKET.md` is the corrected source-of-truth packet for re-review.
- This metadata-only fixer commit intentionally changes only packet metadata after branch-tip SHA `d7299fa23c87612f4b0cf4d37dc4b0ae57c4981f`.
- Re-review should use reviewed branch-tip range `378cf9a74a3658058079a32f186fcd254c4a4034..d7299fa23c87612f4b0cf4d37dc4b0ae57c4981f` for merge-candidate scope and the final HEAD SHA reported by this fixer as the branch tip.
