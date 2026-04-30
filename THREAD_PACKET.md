## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge target: actual branch tip after this fixer commit, not `adfa8cdadd43747ffbcb612e4151e262b13e52ca` only.
- Reviewer-cited stale stop point: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Pre-fixer branch-tip SHA: `8626703d3fa6929dd1923fecd41c804551eabef0`.
- Final HEAD SHA: reported in the fixer final response because a commit cannot contain its own SHA.
- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..FINAL_HEAD`, where `FINAL_HEAD` is the final fixer commit reported after the required gates pass.
- Actual merge-candidate comparison: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..FINAL_HEAD`, where `fd2ab6ca65ec2f93d1334c9b7df8512439725be4` is the `main...HEAD` merge base.
- Handoff classification: high-risk/shared because the corrected reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

## Required Fixes Addressed

1. Regenerated this handoff against the actual merge candidate. Review no longer stops at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`; the reviewed range covers the post-`adfa8cd` retrieval implementation, tests, packet files, and this fixer commit.
2. Updated `Files changed` to include every source, test, and packet file in the corrected reviewed range, including `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`.
3. Reclassified the packet as high-risk/shared because `tests/unit/test_unified_retrieval.py` remains touched in the corrected reviewed range, and reported task count, file count, and LOC for that range.
4. Rewrote completed tasks so each task names the canonical demo-path step it advances.
5. Re-ran and reported the required gates on the corrected merge candidate.

## Scope Completed

The corrected merge candidate advances the canonical demo-path step `retrieve relevant material`. SQLite FTS remains the authoritative MVP retrieval path, document updates invalidate cached FTS search state, excerpt lookup fails closed for PageIndex-only IDs, and sparse retrieval payload reconstruction preserves deterministic document IDs, citation refs, ranks, fingerprints, primary-source provenance, basket promotion items, and basket item IDs. Sparse context-reference preservation also advances `promote or gather context into the basket`.

PageIndex and embeddings remain compatibility-only fallback shims. They are not required paths for the branch-tip retrieval behavior.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: keep excerpt lookup on the canonical FTS-first path so PageIndex-only excerpt IDs fail closed under regression coverage.
2. Canonical demo-path step `retrieve relevant material`: invalidate FTS search cache after document updates so retrieval results do not reuse stale search state.
3. Canonical demo-path steps `retrieve relevant material` and `promote or gather context into the basket`: preserve deterministic sparse retrieval payload reconstruction, including primary-source provenance, basket promotion items, and basket item IDs.
4. Handoff traceability for canonical demo-path step `retrieve relevant material`: regenerate packet metadata so review covers the actual implementation that will merge, including all branch-tip code/test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Files Changed

Files changed in corrected reviewed range `adfa8cdadd43747ffbcb612e4151e262b13e52ca..FINAL_HEAD`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`: packet mirror is part of the corrected reviewed range, but this sandbox rejects edits under `.codex/kickoff_packets`; use `THREAD_PACKET.md` as the authoritative corrected handoff artifact for re-review.
- `.codex/lane_meta/feat-retrieval-fts.json`: lane metadata mirror is part of the corrected reviewed range, but this sandbox rejects edits under `.codex/lane_meta`; use `THREAD_PACKET.md` as the authoritative corrected handoff artifact for re-review.
- `THREAD_PACKET.md`: visible handoff packet regenerated for actual branch-tip review.
- `src/qual/engine/retrieval/fts_strategy.py`: adds explicit cache invalidation support for the FTS strategy.
- `src/qual/engine/retrieval/payload.py`: preserves sparse primary provenance, basket promotion items, basket item IDs, and basket/context reconstruction fields deterministically.
- `src/qual/retrieval/service.py`: invalidates the FTS cache after document updates.
- `tests/unit/test_unified_retrieval.py`: covers FTS cache invalidation and sparse primary provenance reconstruction.

Packet refresh commits in this range are reviewed as metadata changes. They are not used to hide or exclude retrieval source/test changes from the branch-tip review boundary.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; the branch-tip work is folded into four meaningful tasks under the high-risk cap.
- Changed files in corrected reviewed range: `7`.
- Net LOC in corrected reviewed range before commit: `441 insertions(+), 106 deletions(-)`, net `335`, across the 7 files above.
- Integrator-locked files touched: none.
- Shared-by-approval files touched: `tests/unit/test_unified_retrieval.py`.
- Lane-owned implementation files touched: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Routing/provider impact: none; no model routing or provider configuration is touched.

## Roadmap / Vision Mapping

- Roadmap items affected: `ROADMAP.md` Milestone 3 Real workflow loop, with Milestone 4 Retrieval Layer groundwork.
- Vision capabilities affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling, and capability 6, Auditable state and workflow.
- Canonical demo-path step advanced: `retrieve relevant material`. Sparse context-reference preservation also advances `promote or gather context into the basket`.
- FTS-first mapping: SQLite FTS remains the required retrieval path; PageIndex and embeddings remain fallback-only compatibility shims.
- Proposed `README.md` patch text: none.

## Commands Run

Required scope and integration gates for this corrected merge candidate:

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS.

## Risks / Blockers

- No implementation blocker is known.
- Protected `.codex` mirror files could not be updated in this lane worktree by this fixer pass: writes under `.codex/kickoff_packets` and `.codex/lane_meta` are rejected by the sandbox, so `THREAD_PACKET.md` remains the authoritative corrected handoff artifact.
- This packet treats `8626703d3fa6929dd1923fecd41c804551eabef0` plus this fixer commit as the actual merge candidate instead of preserving stale `adfa8cdadd43747ffbcb612e4151e262b13e52ca` review anchors.
- The corrected post-`adfa8cd` reviewed range exceeds the high-risk `<=300` net LOC guidance; this is explicitly surfaced for reviewer risk assessment.
