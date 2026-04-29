## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: reviewer-fix re-review packet after correcting the merge candidate scope.
- Merge candidate: current branch tip after this fixer commit.
- Reviewer base/range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Final proposed merge HEAD after this fixer commit: reported in the fixer response.

## Scope Completed

This handoff intentionally narrows the merge candidate back to the previously reviewed implementation slice: FTS excerpt lookup now uses the canonical SQLite FTS path only, and PageIndex-only excerpt IDs fail closed. PageIndex and embeddings remain compatibility-only fallback shims and are not reintroduced as excerpt lookup fallbacks.

The post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` runtime/test changes previously present at `5e3df62f6` have been removed from the final branch-tip content. The remaining post-`adfa8cd` changes are packet metadata only.

No Textual/UI work, provider routing change, command surface expansion, hidden alternate retrieval mode, payload expansion, basket-promotion behavior, or context-bundle rehydration change is included in this corrected merge candidate.

## Tasks Completed

1. Changed `RetrievalService.fetch_excerpt` to use `_lookup_fts_excerpt` directly and fail closed for unknown or non-FTS excerpt IDs.
2. Added shared regression coverage proving PageIndex-only excerpt IDs are rejected by the canonical `fetch_excerpt` path.
3. Updated the existing excerpt payload regression from PageIndex normalization to PageIndex rejection.
4. Corrected packet traceability so branch-tip scope, files changed, task accounting, and budget status match the narrowed merge candidate.

## Files Changed

Corrected final branch-tip content versus reviewer base `378cf9a74a3658058079a32f186fcd254c4a4034`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Implementation/test content in the reviewed slice:

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

The corrected final branch-tip diff removes `src/qual/engine/retrieval/payload.py` from the merge candidate content. That file was part of the unreviewed post-`adfa8cd` expansion and is deferred.

## Budget

- Risk: high, because the implementation slice touches shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Task budget: `4/4` under AGENTS high-risk rules.
- File budget for corrected final branch-tip content: `5/8`.
- Net LOC budget for corrected final branch-tip content: within `<=300` net LOC.
- Implementation/test slice size: `2 files changed, 28 insertions(+), 31 deletions(-)`.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is the only shared-by-approval regression surface in the implementation slice; no integrator-locked files are edited.

## Roadmap / Vision

- Roadmap item: `ROADMAP.md` Milestone 3 Product Readiness, specifically retrieval evidence attached to workflow outputs.
- Vision capabilities: retrieval-first context handling and auditable workflow behavior.
- Exact mapping: canonical FTS-backed excerpt lookup is now the only supported `fetch_excerpt` path, so excerpt provenance remains tied to SQLite FTS rather than PageIndex fallback behavior.
- Routing/provider impact: none.
- Textual/UI impact: none.
- Alternate retrieval-mode impact: none.
- Proposed `README.md` patch text: none.

## Reviewer Required Fixes Addressed

1. The actual merge candidate is the current branch tip after this fixer commit, whose implementation content is narrowed back to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` plus packet metadata only.
2. The `5e3df62f6` branch-tip expansion is no longer the merge-candidate content; its post-`adfa8cd` source/test changes were removed from the final branch-tip tree.
3. The unreviewed `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py` post-`adfa8cd` additions were split out/deferred by reverting their final content.
4. Required gates are rerun against the corrected branch tip and reported below.

## Commands Run

Required gates rerun after correcting the branch-tip content:

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS, including smoke plus 124 unit tests
- `./typecheck-test.sh`: PASS
- `make ci`: PASS, including scope-check, format, lint, compileall, and smoke plus 124 unit tests

## Risks / Blockers

- The branch history still contains earlier commits that temporarily expanded runtime/test scope, but the final merge-candidate tree no longer contains those post-`adfa8cd` source/test changes.
- Review should be based on the corrected final branch-tip diff against `378cf9a74a3658058079a32f186fcd254c4a4034`, not the superseded `5e3df62f6` content snapshot.
