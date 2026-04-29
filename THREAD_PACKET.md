## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip `HEAD` after this fixer metadata commit.
- Branch-tip SHA before this metadata fix: `c6302e9e4c74bb24ba45752424ec6bea12cd4c0b`
- Reviewed implementation head: `c6302e9e4c74bb24ba45752424ec6bea12cd4c0b`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..c6302e9e4c74bb24ba45752424ec6bea12cd4c0b`
- Packet refresh note: this fixer commit only regenerates handoff metadata. The reviewed material code/test range now includes every runtime and test change through branch tip `c6302e9e4c74bb24ba45752424ec6bea12cd4c0b`.
- Handoff classification: high-risk/shared because the reviewed implementation includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Shared-file approval provenance: reviewer packet `fixer__feat-retrieval-fts__20260429T202122Z.prompt.txt`, finding 2, identifies `tests/unit/test_unified_retrieval.py` as the approved shared surface for `feat-retrieval-fts`.

## Required Fixes Addressed

1. Regenerated the review packet so the reviewed implementation range includes all runtime/test changes through actual branch tip `c6302e9e4c74bb24ba45752424ec6bea12cd4c0b`.
2. Added the post-`adfa8cd` branch-tip work to the handoff: FTS cache invalidation after document upserts, retrieval context refs, citation/context payload helpers, and the related shared regression tests.
3. Recomputed budget and size accounting against the full implementation range `d7fd5d200358287fa42a18d39e2b277463b9b69f..c6302e9e4c74bb24ba45752424ec6bea12cd4c0b`.
4. Updated `Files Changed`, `Tasks Completed`, and `Scope Completed` so they match the actual full branch-tip diff.
5. Reran the required gates for the corrected final range; results are reported below.
6. Added explicit canonical demo-path mapping for `retrieve relevant material` and basket/context promotion.

## Scope Completed

The reviewed implementation range ships the cumulative FTS-first retrieval handoff through `c6302e9e4c74bb24ba45752424ec6bea12cd4c0b`: SQLite FTS remains authoritative for excerpt lookup and retrieval ranking, document upserts invalidate the FTS retrieval cache, canonical query and payload snapshots are normalized, retrieval provenance and fingerprints are deterministic, sparse source/context/citation refs rehydrate into stable payloads, and retrieval context refs are exposed for basket promotion handoff. PageIndex and embeddings remain compatibility/fallback surfaces, not required retrieval paths.

## Canonical Demo-Path Mapping

- Demo-path step advanced: `retrieve relevant material`.
- Basket/context step advanced: retrieved source, citation, and context refs are preserved in payload/provenance snapshots so relevant material can be gathered or promoted into the basket without losing traceability.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: keep SQLite FTS authoritative for excerpt lookup, candidate ranking, cache scope normalization, FTS cache invalidation after document upserts, and fail-closed unsupported lookup paths.
2. Canonical demo-path step `retrieve relevant material`: normalize canonical query snapshots, constraints, date ranges, hit payloads, source bundles, and provenance fingerprints across the retrieval and engine retrieval facades.
3. Canonical demo-path step `retrieve relevant material` plus basket handoff: preserve sparse source/context/citation refs and basket promotion metadata so retrieved evidence can be gathered into downstream context with stable traceability.
4. Handoff/review support: update packet planner metadata support and shared regression coverage for the FTS-first retrieval contract, payload normalization, facade exports, excerpt backfill, FTS cache invalidation, and context-ref payloads.

## Files Changed

Reviewed implementation range `d7fd5d200358287fa42a18d39e2b277463b9b69f..c6302e9e4c74bb24ba45752424ec6bea12cd4c0b`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_packet_planner.py`
- `tests/unit/test_unified_retrieval.py`

Post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` branch-tip implementation slice included in this handoff:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Metadata-only fixer commit after `c6302e9e4c74bb24ba45752424ec6bea12cd4c0b`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; passes the high-risk task cap.
- Reviewed range file count: `13` files, above the high-risk 8-file size guideline because this packet now covers the full accumulated branch-tip implementation range requested by review.
- Reviewed range size: `1994 insertions(+), 265 deletions(-)`, above the high-risk 300 net LOC guideline and above the default 500 net LOC guideline; this must be reviewed as an oversized accumulated branch-tip handoff rather than a narrow metadata refresh.
- Post-`adfa8cd` implementation slice: `7` files, `393 insertions(+), 83 deletions(-)`, and is included in this handoff.
- Integrator-locked files: none identified in `THREAD_OWNERSHIP.md`.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py`, used for canonical retrieval regression coverage.
- Routing/provider impact: none.

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 3 real workflow loop: retrieval supplies workflow-ready source context before drafting or diff generation.
- Roadmap item affected: `ROADMAP.md` Milestone 4 retrieval layer: FTS-first retrieval and source attribution for retrieved chunks, with PageIndex/embeddings deferred until after the demo push.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling.
- Vision capability affected: `PRODUCT_VISION.md` capability 3, Auditable generation.
- Proposed `README.md` patch text: none.

## Commands Run

Fresh fixer pass on `2026-04-29` after regenerating the reviewed range through `c6302e9e4c74bb24ba45752424ec6bea12cd4c0b`:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS.
- `./typecheck-test.sh` PASS.
- `make ci` PASS.

## Risks / Blockers

- No implementation blockers are known.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are tracked packet mirrors but are not writable in this sandbox (`EPERM` on direct write, temp-file creation, and xattr removal), so `THREAD_PACKET.md` is the corrected source-of-truth packet for this fixer pass.
- This metadata-only fixer commit intentionally changes only packet metadata after reviewed implementation head `c6302e9e4c74bb24ba45752424ec6bea12cd4c0b`.
- Re-review should use reviewed implementation range `d7fd5d200358287fa42a18d39e2b277463b9b69f..c6302e9e4c74bb24ba45752424ec6bea12cd4c0b` and the final HEAD SHA reported by this fixer as the branch tip.
