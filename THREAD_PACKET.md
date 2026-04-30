## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge target: current branch tip, not `adfa8cdadd43747ffbcb612e4151e262b13e52ca` only.
- Pre-fixer branch-tip SHA: `faba2c65c1c6d231bda95cfd64a12169b9a41a1a`.
- Final HEAD SHA: reported in the fixer final response because a commit cannot contain its own SHA.
- Actual merge-candidate comparison: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`, where `fd2ab6ca65ec2f93d1334c9b7df8512439725be4` is the `main...HEAD` merge base.
- Reviewed branch-tip packet range for this reviewer-required correction: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..faba2c65c1c6d231bda95cfd64a12169b9a41a1a`, plus this metadata-only fixer commit.
- Handoff classification: high-risk/shared because the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Shared-file approval provenance: reviewer packets for `feat-retrieval-fts` required the packet to cover every branch-tip source/test change, including the retrieval implementation commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Current fixer note: this metadata-only pass preserves the corrected `adfa8cd..faba2c65` branch-tip packet boundary and re-runs the required gates before creating a new fixer commit.

## Required Fixes Addressed

1. Regenerated the packet against the actual merge candidate tip, keeping `faba2c65c1c6d231bda95cfd64a12169b9a41a1a` as the candidate instead of narrowing the submission to `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. Updated the reviewed implementation range to include `adfa8cdadd43747ffbcb612e4151e262b13e52ca..faba2c65c1c6d231bda95cfd64a12169b9a41a1a` and listed every code/test/packet file changed in that range.
3. Recast the task list as four high-risk tasks that describe only the branch-tip code and packet changes under review.
4. Added explicit canonical demo-path mapping: the branch-tip changes primarily advance `retrieve relevant material`, with sparse context-reference preservation also advancing `promote or gather context into the basket`.
5. Re-ran and reported `make scope-check` plus all required integration gates on the corrected review target.

## Scope Completed

The current branch-tip merge candidate advances the canonical demo-path step `retrieve relevant material`. SQLite FTS remains the authoritative retrieval path for MVP flows, document updates now invalidate cached FTS search state, excerpt lookup fails closed for PageIndex-only IDs, and sparse retrieval payload reconstruction preserves deterministic document IDs, citation refs, ranks, fingerprints, primary sources, and basket promotion context references. The sparse provenance and context-reference work also advances `promote or gather context into the basket`.

PageIndex and embeddings remain compatibility-only fallback shims. They are not required paths for the branch-tip retrieval behavior.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: keep excerpt lookup on the canonical FTS-first path so PageIndex-only excerpt IDs fail closed under regression coverage.
2. Canonical demo-path step `retrieve relevant material`: invalidate FTS search cache after document updates so retrieval results do not reuse stale search state.
3. Canonical demo-path steps `retrieve relevant material` and `promote or gather context into the basket`: preserve deterministic sparse retrieval payload reconstruction, including basket promotion context references and primary-source provenance.
4. Handoff traceability for canonical demo-path step `retrieve relevant material`: regenerate packet metadata so review covers the implementation that will merge, including all branch-tip code/test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Files Changed

Files changed in reviewed branch-tip range `adfa8cdadd43747ffbcb612e4151e262b13e52ca..faba2c65c1c6d231bda95cfd64a12169b9a41a1a`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`: packet mirror updated during prior packet refresh commits, but still preserves stale reviewed-head language in this sandboxed worktree.
- `.codex/lane_meta/feat-retrieval-fts.json`: lane metadata mirror updated during prior packet refresh commits, but still preserves stale reviewed-head language in this sandboxed worktree.
- `THREAD_PACKET.md`: visible handoff packet regenerated for actual branch-tip review.
- `src/qual/engine/retrieval/fts_strategy.py`: adds explicit cache invalidation support for the FTS strategy.
- `src/qual/engine/retrieval/payload.py`: preserves sparse primary provenance and basket/context reconstruction fields deterministically.
- `src/qual/retrieval/service.py`: invalidates the FTS cache after document updates.
- `tests/unit/test_unified_retrieval.py`: covers FTS cache invalidation and sparse primary provenance reconstruction.

Actual post-`adfa8cd` range stat before this metadata-only fixer: `398 insertions(+), 93 deletions(-)` across the 7 files above.

Actual merge-base candidate range before this metadata-only fixer, `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..faba2c65c1c6d231bda95cfd64a12169b9a41a1a`, changes these 5 files:

- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Post-`adfa8cd` Implementation Accounting

The reviewed branch-tip range explicitly includes implementation/test commits after the reviewer-cited `adfa8cdadd43747ffbcb612e4151e262b13e52ca` anchor:

- `02c1833d2`: FTS cache invalidation after document updates plus regression coverage.
- `d276ca07a`: sparse primary provenance backfill in retrieval payload reconstruction.
- `faba2c65c`: regenerated packet metadata for the actual branch-tip review target.

Packet refresh commits in this range are reviewed as metadata changes. They are not used to hide or exclude retrieval source/test changes from the branch-tip review boundary.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; branch-tip work is folded into four meaningful tasks under the high-risk cap.
- Changed files in post-`adfa8cd` branch-tip range before this metadata-only fixer: `7`.
- Net LOC in post-`adfa8cd` branch-tip range before this metadata-only fixer: `398 insertions(+), 93 deletions(-)`, which exceeds the high-risk `<=300` guidance and is therefore explicitly surfaced for reviewer risk assessment.
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
- Protected `.codex` mirror files could not be updated in this lane worktree by this fixer pass: writes under `.codex/kickoff_packets` and `.codex/lane_meta` are rejected by the sandbox as outside the writable project, so `THREAD_PACKET.md` remains the authoritative corrected handoff artifact.
- This packet now treats `faba2c65c1c6d231bda95cfd64a12169b9a41a1a`, plus this metadata-only fixer commit, as the actual merge candidate instead of preserving stale `adfa8cdadd43747ffbcb612e4151e262b13e52ca` review anchors.
- The post-`adfa8cd` packet-refresh range exceeds the high-risk net LOC guidance; this is packet traceability risk, not an unresolved implementation failure.
