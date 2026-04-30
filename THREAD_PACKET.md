## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Pre-fixer branch-tip SHA: `25d4f4fdae66c3008a1b4c3d96ece7887dbd6103`
- Final HEAD SHA: reported in the fixer final response because a commit cannot contain its own SHA.
- Merge-candidate comparison: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`, where `fd2ab6ca65ec2f93d1334c9b7df8512439725be4` is the `main...HEAD` merge base.
- Reviewed implementation range: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..25d4f4fdae66c3008a1b4c3d96ece7887dbd6103`, plus this fixer commit's metadata-only packet refresh.
- Reviewed implementation head before this metadata-only fixer: `25d4f4fdae66c3008a1b4c3d96ece7887dbd6103`.
- Handoff classification: high-risk/shared because the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Shared-file approval provenance: reviewer packets for `feat-retrieval-fts` required the packet to cover every branch-tip source/test change, including the post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` and post-`c2f87101e` retrieval implementation commits.

## Required Fixes Addressed

1. Regenerated the packet against the actual branch tip instead of anchoring review to the narrowed `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice.
2. The reviewed range now includes all source/test changes through `25d4f4fdae66c3008a1b4c3d96ece7887dbd6103`, including post-`adfa8cd` changes in retrieval strategy, payload reconstruction, retrieval service, and shared regression tests.
3. `Files Changed` includes all metadata, source, and test files changed in the reviewed merge-candidate range.
4. Completed tasks are restated as four meaningful high-risk tasks under the AGENTS.md cap.
5. Final gates are re-run against the exact submitted branch tip after this packet refresh.

## Scope Completed

The current merge candidate advances the canonical demo-path step `retrieve relevant material`. SQLite FTS remains the authoritative retrieval path for MVP flows, document updates invalidate cached FTS search state, excerpt lookup fails closed for PageIndex-only IDs, and sparse retrieval payload reconstruction preserves deterministic document IDs, citation refs, ranks, fingerprints, primary sources, and basket promotion context references.

PageIndex and embeddings remain compatibility-only fallback shims. They are not required paths for the branch-tip retrieval behavior.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: keep excerpt lookup on the canonical FTS-first path so PageIndex-only excerpt IDs fail closed under regression coverage.
2. Canonical demo-path step `retrieve relevant material`: invalidate FTS search cache after document updates so retrieval results do not reuse stale search state.
3. Canonical demo-path step `retrieve relevant material`: preserve deterministic sparse retrieval payload reconstruction, including basket promotion context references and primary-source provenance.
4. Handoff traceability: regenerate packet metadata so review covers the implementation that will merge, including all branch-tip code/test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`: refreshes lane kickoff traceability for the actual branch-tip reviewed range.
- `.codex/lane_meta/feat-retrieval-fts.json`: refreshes lane metadata for the actual branch-tip reviewed range, high-risk budget, files, and gates.
- `THREAD_PACKET.md`: regenerates the authoritative handoff packet for actual branch-tip review.
- `src/qual/engine/retrieval/fts_strategy.py`: adds explicit cache invalidation support for the FTS strategy.
- `src/qual/engine/retrieval/payload.py`: preserves sparse primary provenance and basket/context reconstruction fields deterministically.
- `src/qual/retrieval/service.py`: routes excerpt lookup through the canonical FTS-first retrieval path and invalidates the FTS cache after document updates.
- `tests/unit/test_unified_retrieval.py`: covers FTS-only excerpt failure for PageIndex-only IDs, FTS cache invalidation, and sparse primary provenance reconstruction.

## Post-`adfa8cd` Implementation Accounting

The reviewed range explicitly includes implementation/test commits after the reviewer-cited `adfa8cdadd43747ffbcb612e4151e262b13e52ca` anchor:

- `02c1833d2`: FTS cache invalidation after document updates plus regression coverage.
- `d276ca07a`: sparse primary provenance backfill in retrieval payload reconstruction.

Packet refresh commits after those implementation commits are reviewed as metadata changes. They are not used to hide or exclude source/test changes from the branch-tip review boundary.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; branch-tip work is folded into four meaningful tasks under the high-risk cap.
- Changed files in reviewed merge-candidate range: `7`; within the high-risk `<=8` guideline.
- Net LOC in `main...HEAD` before this fixer: `103 insertions(+), 73 deletions(-)`; within the high-risk `<=300` guideline.
- Integrator-locked files touched: none.
- Shared-by-approval files touched: `tests/unit/test_unified_retrieval.py`.
- Lane-owned implementation files touched: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Routing/provider impact: none; no model routing or provider configuration is touched.

## Roadmap / Vision Mapping

- Roadmap items affected: `ROADMAP.md` Milestone 3 Real workflow loop, with Milestone 4 Retrieval Layer groundwork.
- Vision capabilities affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling, and capability 6, Auditable state and workflow.
- Canonical demo-path step advanced: `retrieve relevant material`.
- FTS-first mapping: SQLite FTS remains the required retrieval path; PageIndex and embeddings remain fallback-only compatibility shims.
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
- The packet now exposes the actual branch-tip implementation boundary and complete file list instead of preserving stale `adfa8cd` or `c2f87101` review anchors.
