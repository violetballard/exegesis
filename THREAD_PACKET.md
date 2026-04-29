## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip after this metadata-only fixer commit.
- Branch-tip SHA before this metadata fix: `77b174d10f981fae57850ba91335b933638adbd2`
- Reviewed implementation head: `77b174d10f981fae57850ba91335b933638adbd2`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..77b174d10f981fae57850ba91335b933638adbd2`
- Packet refresh note: this packet keeps the actual branch-tip implementation, including every runtime/test change after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` through `77b174d10f981fae57850ba91335b933638adbd2`. This fixer commit changes packet metadata only; the final HEAD SHA is reported in the fixer response.
- Handoff classification: high-risk/shared because the reviewed implementation includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Shared-file approval provenance: reviewer packet `fixer__feat-retrieval-fts__20260429T202122Z.prompt.txt`, finding 2, identifies `tests/unit/test_unified_retrieval.py` as the approved shared surface for `feat-retrieval-fts`.

## Required Fixes Addressed

1. Chose the actual branch tip as the intended merge candidate and regenerated the packet around reviewed implementation head `77b174d10f981fae57850ba91335b933638adbd2`.
2. Included every implementation commit after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` in the reviewed range, including FTS cache invalidation, context refs, citation/source bundle payload backfills, basket-promotion refs, and source bundle context ref preservation.
3. Recomputed tasks, scope completed, files changed, risk, and budget accounting against `378cf9a74a3658058079a32f186fcd254c4a4034..77b174d10f981fae57850ba91335b933638adbd2`.
4. Re-ran the required gates against the corrected merge candidate working tree; results are reported below.
5. Re-stated plan alignment against `ROADMAP.md` Milestone 3 and `PRODUCT_VISION.md` retrieval-first context handling for the full implementation.
6. Re-stated the canonical demo-path step advanced by the full branch-tip work.

## Scope Completed

The reviewed implementation range ships the cumulative FTS-first retrieval handoff through `77b174d10f981fae57850ba91335b933638adbd2`: SQLite FTS remains authoritative for excerpt lookup and retrieval ranking, document upserts invalidate the FTS retrieval cache, canonical query and payload snapshots are normalized, retrieval provenance and fingerprints are deterministic, sparse source/context/citation refs rehydrate into stable payloads, basket-promotion refs are preserved, and source bundle context refs survive payload backfill. PageIndex and embeddings remain compatibility/fallback surfaces, not required retrieval paths.

## Canonical Demo-Path Mapping

- Demo-path step advanced: `retrieve relevant material`.
- Basket/context step advanced: retrieved source, citation, context, and basket-promotion refs are preserved in payload/provenance snapshots so relevant material can be gathered or promoted into the basket without losing traceability.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: keep SQLite FTS authoritative for excerpt lookup, candidate ranking, cache scope normalization, FTS cache invalidation after document upserts, and fail-closed unsupported lookup paths.
2. Canonical demo-path step `retrieve relevant material`: normalize canonical query snapshots, constraints, date ranges, hit payloads, source bundles, and provenance fingerprints across the retrieval and engine retrieval facades.
3. Canonical demo-path step `retrieve relevant material` plus basket handoff: preserve sparse source/context/citation refs, basket promotion metadata, and source bundle context refs so retrieved evidence can be gathered into downstream context with stable traceability.
4. Handoff/review support: update packet planner metadata support and shared regression coverage for the FTS-first retrieval contract, payload normalization, facade exports, excerpt backfill, FTS cache invalidation, context-ref payloads, and source-bundle backfill behavior.

## Files Changed

Reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..77b174d10f981fae57850ba91335b933638adbd2`:

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

Current metadata-only fixer commit after `77b174d10f981fae57850ba91335b933638adbd2`:

- `THREAD_PACKET.md`

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; passes the high-risk task cap as a summarized cumulative handoff.
- Reviewed range file count: `7` files, within the high-risk 8-file size guideline.
- Reviewed range size: `438 insertions(+), 111 deletions(-)`, above the high-risk 300 net LOC guideline; this must be reviewed as an accumulated branch-tip handoff rather than a narrow metadata refresh.
- Post-`adfa8cd` implementation slice: `7` files, `410 insertions(+), 80 deletions(-)`, and is included in this handoff.
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

Fresh fixer pass on `2026-04-29` after regenerating the reviewed range through `77b174d10f981fae57850ba91335b933638adbd2`:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS.
- `./typecheck-test.sh` PASS.
- `make ci` PASS.

## Risks / Blockers

- No implementation blockers are known.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are tracked packet mirrors but are not writable in this sandbox (`Operation not permitted` on write-test and direct append). `THREAD_PACKET.md` is the corrected source-of-truth packet for this fixer pass.
- This metadata-only fixer commit intentionally changes only packet metadata after reviewed implementation head `77b174d10f981fae57850ba91335b933638adbd2`.
- Re-review should use reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..77b174d10f981fae57850ba91335b933638adbd2` for runtime/test scope and the final HEAD SHA reported by this fixer as the branch tip.
