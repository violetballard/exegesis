## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip `HEAD` after this fixer commit.
- Branch-tip SHA: reported in the final fixer response after commit creation.
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Post-`adfa8cd` policy: only packet metadata and this cleanup/revert commit are part of the merge candidate after the reviewed implementation head. Non-metadata retrieval drift after `adfa8cd` has been removed from the branch-tip file state.
- Handoff classification: high-risk/shared because the reviewed implementation includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Shared-file approval provenance: reviewer packet `fixer__feat-retrieval-fts__20260429T202122Z.prompt.txt`, finding 2, identifies `tests/unit/test_unified_retrieval.py` as the approved shared surface for `feat-retrieval-fts`.

## Required Fixes Addressed

1. Chose the narrow merge target: the current branch tip contains the reviewed `adfa8cd` implementation state plus packet metadata and this cleanup/revert commit.
2. Removed the non-metadata retrieval/test drift after `adfa8cd` from the merge-candidate file state by restoring `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py` to the reviewed `adfa8cd` content.
3. Re-ran all required gates against the corrected merge target after this cleanup commit; results are reported below and in the final fixer response.
4. Restated the branch, reviewed implementation range, and files changed to match the corrected merge candidate.

## Scope Completed

The reviewed implementation slice keeps `fetch_excerpt` on the canonical SQLite FTS lookup path and adds shared regression coverage proving PageIndex-only excerpt IDs fail closed. PageIndex and embeddings remain compatibility/fallback surfaces, not required retrieval paths.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: keep SQLite FTS authoritative for excerpt lookup.
2. Canonical demo-path step `retrieve relevant material`: fail closed for PageIndex-only excerpt identifiers.
3. Canonical demo-path step `retrieve relevant material`: add approved shared regression coverage for the FTS-only excerpt contract.
4. Handoff traceability: remove post-review retrieval drift from the branch-tip file state and refresh packet metadata for re-review.

## Files Changed

Reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Post-`adfa8cd` merge-candidate maintenance:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/payload.py` restored to `adfa8cd` state
- `src/qual/retrieval/service.py` restored to `adfa8cd` state
- `tests/unit/test_unified_retrieval.py` restored to `adfa8cd` state

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`.
- File budget for corrected branch-tip file state vs `378cf9a74a3658058079a32f186fcd254c4a4034`: `5/8` files.
- Size budget for corrected branch-tip file state vs `378cf9a74a3658058079a32f186fcd254c4a4034`: `256 insertions(+), 118 deletions(-)`, net `138` LOC.
- Integrator-locked files: none.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py`, used only for canonical retrieval regression coverage.
- Routing/provider impact: none.

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 3 real workflow loop: retrieval supplies workflow-ready source context before drafting or diff generation.
- Roadmap item affected: `ROADMAP.md` Milestone 4 retrieval layer: FTS-first retrieval and source attribution for retrieved chunks, with PageIndex/embeddings deferred until after the demo push.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling.
- Vision capability affected: `PRODUCT_VISION.md` capability 3, Auditable generation.
- Proposed `README.md` patch text: none.

## Commands Run

Fresh fixer pass on `2026-04-29` for the corrected merge candidate:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS.
- `./typecheck-test.sh` PASS.
- `make ci` PASS.

## Risks / Blockers

- No implementation blockers are known.
- Auxiliary packet files under `.codex/` were read-only in this sandbox (`Operation not permitted`), so `THREAD_PACKET.md` is the corrected handoff packet for re-review.
- Re-review should use the reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and the final HEAD SHA reported by this fixer as the branch tip.
