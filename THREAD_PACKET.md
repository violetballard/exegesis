## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Pre-fixer branch-tip SHA: `d276ca07ae3ed8ab51c66f8f07fb62b5bd00ca02`
- Final HEAD SHA: reported in the fixer final response because a commit cannot contain its own SHA.
- Reviewed implementation range: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..d276ca07ae3ed8ab51c66f8f07fb62b5bd00ca02`
- Reviewed implementation head: `d276ca07ae3ed8ab51c66f8f07fb62b5bd00ca02`
- Merge-candidate comparison used for this packet: `main...HEAD` from merge base `fd2ab6ca65ec2f93d1334c9b7df8512439725be4`.
- Handoff classification: high-risk/shared because the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Shared-file approval provenance: reviewer packet `fixer__feat-retrieval-fts__20260430T004922Z.prompt.txt` required the packet to cover every branch-tip code/test change, including post-`adfa8cd` and post-`c2f87101` retrieval implementation commits.

## Required Fixes Addressed

1. Regenerated this packet against the actual merge candidate instead of anchoring review to `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. Updated the reviewed implementation range so it includes all branch-tip code/test changes through `d276ca07ae3ed8ab51c66f8f07fb62b5bd00ca02`.
3. Updated `Files Changed` to include every non-metadata implementation/test file in the true `main...HEAD` merge-candidate diff.
4. Re-ran the required gates on the final branch-tip worktree after this packet refresh; outcomes are recorded below.
5. Restated the canonical demo-path step advanced by the full branch-tip implementation.

## Scope Completed

The current merge candidate advances the canonical demo-path step `retrieve relevant material`. It preserves SQLite FTS as the active retrieval path, invalidates cached FTS search state after document updates, and backfills sparse primary provenance so downstream payload/source/context reconstruction retains deterministic document IDs, citation refs, ranks, fingerprints, primary sources, and basket promotion context references.

The branch-tip packet now treats post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` and post-`c2f87101e` retrieval commits as implementation changes when they modify retrieval code or tests. Metadata-only packet refresh commits remain metadata-only, but they no longer hide later retrieval implementation changes from review.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: expose the branch-tip FTS cache invalidation path after document upserts so retrieval results do not reuse stale search state.
2. Canonical demo-path step `retrieve relevant material`: preserve deterministic sparse retrieval payload reconstruction, including basket promotion context references and primary-source provenance.
3. Canonical demo-path step `retrieve relevant material`: add regression coverage for cache invalidation and sparse primary provenance behavior in the approved shared retrieval test surface.
4. Handoff traceability: regenerate the branch-tip packet so review covers the implementation that will merge, including all code/test changes through `d276ca07ae3ed8ab51c66f8f07fb62b5bd00ca02`.

## Files Changed

- `THREAD_PACKET.md`: regenerates the authoritative handoff packet for actual branch-tip review.
- `src/qual/engine/retrieval/fts_strategy.py`: adds explicit cache invalidation support for the FTS strategy.
- `src/qual/engine/retrieval/payload.py`: preserves sparse primary provenance and basket/context reconstruction fields deterministically.
- `src/qual/retrieval/service.py`: invalidates the FTS cache after document updates.
- `tests/unit/test_unified_retrieval.py`: covers FTS cache invalidation and sparse primary provenance reconstruction.

## Post-`adfa8cd` / Post-`c2f87101` Implementation Accounting

The current reviewed range includes branch-tip implementation/test changes after both reviewer-cited anchors:

- `02c1833d2`: FTS cache invalidation after document updates plus regression coverage.
- `d276ca07a`: sparse primary provenance backfill in retrieval payload reconstruction.

The packet refresh commits between those implementation commits update handoff wording only. They are included in branch history but are not used to exclude implementation commits from the reviewed range.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; branch-tip work is folded into four meaningful tasks under the high-risk cap.
- Changed files in `main...HEAD`: `5`; within the high-risk `<=8` guideline.
- Net LOC in `main...HEAD`: `117 insertions(+), 76 deletions(-)`; within the high-risk `<=300` guideline.
- Integrator-locked files touched: none.
- Shared-by-approval files touched: `tests/unit/test_unified_retrieval.py`.
- Lane-owned implementation files touched: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Routing/provider impact: none; no model routing or provider configuration is touched.

## Roadmap / Vision Mapping

- Roadmap items affected: `ROADMAP.md` Milestone 3 Real workflow loop, with Milestone 4 Retrieval Layer groundwork.
- Vision capabilities affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling, and capability 6, Auditable state and workflow.
- Canonical demo-path step advanced: `retrieve relevant material`.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS.

## Risks / Blockers

- No implementation blocker is known.
- The branch-tip packet now exposes the actual reviewed implementation head and file list instead of preserving stale `adfa8cd` or `c2f87101` review anchors.
