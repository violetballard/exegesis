## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Pre-fixer branch-tip SHA: `b039675ac64fd3358c5b232256dac13e05c61a1c`
- Final HEAD SHA: reported in the fixer final response because a commit cannot contain its own SHA.
- Merge-candidate comparison: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`, where `fd2ab6ca65ec2f93d1334c9b7df8512439725be4` is the `main...HEAD` merge base.
- Reviewed implementation range: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..b039675ac64fd3358c5b232256dac13e05c61a1c`, plus this fixer commit's metadata-only packet correction.
- Reviewed implementation head before this metadata-only fixer: `b039675ac64fd3358c5b232256dac13e05c61a1c`.
- Handoff classification: high-risk/shared because the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Shared-file approval provenance: reviewer packets for `feat-retrieval-fts` required the packet to cover every branch-tip source/test change, including the post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval implementation commits.

## Required Fixes Addressed

1. Regenerated the packet against the actual branch tip instead of anchoring review to the narrowed `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice.
2. The reviewed range now includes all source/test changes through `b039675ac64fd3358c5b232256dac13e05c61a1c`, including post-`adfa8cd` changes in retrieval strategy, payload reconstruction, retrieval service, and shared regression tests.
3. `Files Changed` exactly matches the merge-candidate range before this metadata-only fixer: implementation/test files are separated from the handoff packet file, and executable packet-planner code/test files are explicitly accounted for as non-metadata surfaces in the cumulative lane range.
4. Completed tasks are restated as four meaningful high-risk tasks under the AGENTS.md cap.
5. Each completed task is mapped to the canonical demo path: `retrieve relevant material` and, where applicable, `promote or gather context into the basket`.

## Scope Completed

The current merge candidate advances the canonical demo-path step `retrieve relevant material`. SQLite FTS remains the authoritative retrieval path for MVP flows, document updates invalidate cached FTS search state, excerpt lookup fails closed for PageIndex-only IDs, and sparse retrieval payload reconstruction preserves deterministic document IDs, citation refs, ranks, fingerprints, primary sources, and basket promotion context references. The sparse provenance and context-reference work also advances `promote or gather context into the basket`.

PageIndex and embeddings remain compatibility-only fallback shims. They are not required paths for the branch-tip retrieval behavior.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: keep excerpt lookup on the canonical FTS-first path so PageIndex-only excerpt IDs fail closed under regression coverage.
2. Canonical demo-path step `retrieve relevant material`: invalidate FTS search cache after document updates so retrieval results do not reuse stale search state.
3. Canonical demo-path steps `retrieve relevant material` and `promote or gather context into the basket`: preserve deterministic sparse retrieval payload reconstruction, including basket promotion context references and primary-source provenance.
4. Handoff traceability for canonical demo-path step `retrieve relevant material`: regenerate packet metadata so review covers the implementation that will merge, including all branch-tip code/test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and executable packet-planner code/test surfaces from the cumulative lane range.

## Files Changed

Implementation and shared regression files in the reviewed merge-candidate range:

- `src/qual/engine/retrieval/fts_strategy.py`: adds explicit cache invalidation support for the FTS strategy.
- `src/qual/engine/retrieval/payload.py`: preserves sparse primary provenance and basket/context reconstruction fields deterministically.
- `src/qual/retrieval/service.py`: routes excerpt lookup through the canonical FTS-first retrieval path and invalidates the FTS cache after document updates.
- `tests/unit/test_unified_retrieval.py`: covers FTS-only excerpt failure for PageIndex-only IDs, FTS cache invalidation, and sparse primary provenance reconstruction.

Metadata-only handoff file in the reviewed merge-candidate range:

- `THREAD_PACKET.md`: regenerates the authoritative handoff packet for actual branch-tip review.

No `.codex/kickoff_packets` or `.codex/lane_meta` files are changed in the `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..b039675ac64fd3358c5b232256dac13e05c61a1c` merge-candidate range.

Non-metadata executable code/test files in the cumulative lane range, not classified as handoff metadata:

- `codex_packet_handoff/tools/planner.py`: packet-planner tool behavior; owned by packet-handoff tooling, included for review/risk accounting rather than listed as metadata-only.
- `tests/unit/test_packet_planner.py`: packet-planner regression coverage; included for review/risk accounting rather than listed as metadata-only.

## Post-`adfa8cd` Implementation Accounting

The reviewed range explicitly includes implementation/test commits after the reviewer-cited `adfa8cdadd43747ffbcb612e4151e262b13e52ca` anchor:

- `02c1833d2`: FTS cache invalidation after document updates plus regression coverage.
- `d276ca07a`: sparse primary provenance backfill in retrieval payload reconstruction.
- `b039675ac`: final demo-path packet alignment while preserving the same branch-tip source/test scope.
- `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` are executable tool/test changes in the cumulative lane range and are not metadata-only handoff files.

Packet refresh commits after those implementation commits are reviewed as metadata changes. They are not used to hide or exclude source/test changes from the branch-tip review boundary.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; branch-tip work is folded into four meaningful tasks under the high-risk cap.
- Changed files in reviewed merge-candidate range before this metadata-only fixer: `5`; within the high-risk `<=8` guideline.
- Net LOC in reviewed merge-candidate range before this metadata-only fixer: `107 insertions(+), 73 deletions(-)`; within the high-risk `<=300` guideline.
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

Required gates for this corrected merge candidate:

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS.

## Risks / Blockers

- No implementation blocker is known.
- Protected `.codex` mirror files could not be updated in this lane worktree: writes under `.codex/kickoff_packets` and `.codex/lane_meta` return `EPERM`, so `THREAD_PACKET.md` remains the authoritative corrected handoff artifact.
- The packet now exposes the actual branch-tip implementation boundary and complete file list instead of preserving stale `adfa8cd` or `c2f87101` review anchors.
