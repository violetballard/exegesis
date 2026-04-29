## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip `HEAD` after this metadata-only fixer commit.
- Branch-tip SHA: reported in the final fixer response after commit creation.
- Reviewed implementation head: `980e2814c058f76d75739808757b0013da84b440`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..980e2814c058f76d75739808757b0013da84b440`
- Packet refresh note: this fixer commit only regenerates handoff metadata. The reviewed material code/test range now includes every branch-tip material change through `980e2814c058f76d75739808757b0013da84b440`.
- Handoff classification: high-risk/shared because the reviewed implementation includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Shared-file approval provenance: reviewer packet `fixer__feat-retrieval-fts__20260429T202122Z.prompt.txt`, finding 2, identifies `tests/unit/test_unified_retrieval.py` as the approved shared surface for `feat-retrieval-fts`.

## Required Fixes Addressed

1. Regenerated the review packet so the reviewed implementation range includes the material code/test changes currently present at `980e2814c058f76d75739808757b0013da84b440`.
2. Updated scope, task, file, and command accounting to describe the full reviewed range `d7fd5d200358287fa42a18d39e2b277463b9b69f..980e2814c058f76d75739808757b0013da84b440`.
3. Added explicit canonical demo-path mapping: this work advances `retrieve relevant material`, and the context-ref additions make retrieved material promotion/gathering into the basket more concrete.
4. Re-ran the required gates after regenerating the reviewed range; results are reported below.

## Scope Completed

The reviewed implementation range ships the cumulative FTS-first retrieval handoff through `980e2814c058f76d75739808757b0013da84b440`: SQLite FTS remains authoritative for excerpt lookup and retrieval ranking, canonical query and payload snapshots are normalized, retrieval provenance and fingerprints are deterministic, sparse source/context bundles rehydrate into stable payloads, and retrieval context refs/citation refs are exposed for basket promotion handoff. PageIndex and embeddings remain compatibility/fallback surfaces, not required retrieval paths.

## Canonical Demo-Path Mapping

- Demo-path step advanced: `retrieve relevant material`.
- Basket/context step advanced: retrieved source, citation, and context refs are now preserved in payload/provenance snapshots so relevant material can be gathered or promoted into the basket without losing traceability.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: keep SQLite FTS authoritative for excerpt lookup, candidate ranking, cache scope normalization, and fail-closed unsupported lookup paths.
2. Canonical demo-path step `retrieve relevant material`: normalize canonical query snapshots, constraints, date ranges, hit payloads, source bundles, and provenance fingerprints across the retrieval and engine retrieval facades.
3. Canonical demo-path step `retrieve relevant material`: preserve sparse source/context/citation refs and basket promotion metadata so retrieved evidence can be gathered into downstream context with stable traceability.
4. Handoff/review support: update packet planner metadata support and shared regression coverage for the FTS-first retrieval contract, payload normalization, facade exports, excerpt backfill, and context-ref payloads.

## Files Changed

Reviewed implementation range `d7fd5d200358287fa42a18d39e2b277463b9b69f..980e2814c058f76d75739808757b0013da84b440`:

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

Metadata-only fixer commit after `980e2814c058f76d75739808757b0013da84b440`:

- `THREAD_PACKET.md`

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`.
- Reviewed range file count: `13` files, above the high-risk 8-file guideline because this packet covers the full accumulated branch-tip material range requested by review.
- Reviewed range size: `1978 insertions(+), 268 deletions(-)`.
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

Fresh fixer pass on `2026-04-29` after regenerating the reviewed range:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS.
- `./typecheck-test.sh` PASS.
- `make ci` PASS.

## Risks / Blockers

- No implementation blockers are known.
- Auxiliary packet mirrors under `.codex/` are not writable in this sandbox, so `THREAD_PACKET.md` is the regenerated source-of-truth handoff packet for re-review.
- This metadata-only fixer commit intentionally does not change retrieval code or tests after reviewed implementation head `980e2814c058f76d75739808757b0013da84b440`.
- Re-review should use reviewed implementation range `d7fd5d200358287fa42a18d39e2b277463b9b69f..980e2814c058f76d75739808757b0013da84b440` and the final HEAD SHA reported by this fixer as the branch tip.
