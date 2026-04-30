## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge target: actual branch tip after this fixer commit.
- Authoritative artifact: `THREAD_PACKET.md`. Attempts to update `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` from this worktree were rejected by the filesystem sandbox, so those mirrors must not be used as source of truth for this re-review.
- Reviewed merge-candidate range: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`, where `fd2ab6ca65ec2f93d1334c9b7df8512439725be4` is the current `main...HEAD` merge base.
- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..HEAD`; review must include all implementation, test, packet, and fixer changes through the final branch tip.
- Reviewer trace range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..HEAD`; this range includes the post-`adfa8cd` retrieval source/test changes that must be reviewed, including the reviewer-cited `0e86dfbb83606b30814de4cc2f30234867ebeda9` payload change and `b65733d6ffb0b78532478db3d4b4853f49248c4a` source/test change.
- Pre-fixer branch-tip SHA: `0c33dab0297afbe97a5ea03ca1c4c7f4bc49e22a`.
- Final HEAD SHA: reported in the fixer final response because a commit cannot contain its own SHA.
- Handoff classification: high-risk/shared because the corrected reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

## Required Fixes Addressed

1. Regenerated this handoff against the actual branch tip intended for merge.
2. Included post-`adfa8cd` source/test changes in the reviewed trace range and file list, including changes to `src/qual/engine/retrieval/payload.py` and `tests/unit/test_unified_retrieval.py`.
3. Removed the stale claim that branch-tip packet-refresh commits are metadata-only when they touch retrieval source or tests; `b65733d6ffb0b78532478db3d4b4853f49248c4a` is implementation/test scope, not metadata-only scope.
4. Made `Scope Completed`, `Tasks Completed`, `Files Changed`, and command results all refer to the same `HEAD` merge candidate.
5. Updated each completed task to name the canonical demo-path step it advances.
6. Re-ran and reported the required gates on the corrected merge candidate.

## Scope Completed

The corrected merge candidate advances the canonical demo-path step `retrieve relevant material`. SQLite FTS remains the authoritative MVP retrieval path, repeated retrieval calls use an immutable cache-key snapshot, document updates invalidate cached FTS search state, excerpt lookup fails closed for PageIndex-only IDs, and sparse retrieval payload reconstruction preserves deterministic document IDs, citation refs, ranks, fingerprints, primary-source provenance, basket promotion items, and basket item IDs.

Sparse context-reference preservation also advances `promote or gather context into the basket`: source-bundle-only context reconstruction now carries a canonical downstream retrieval payload while preserving the source bundle and basket references separately. PageIndex and embeddings remain compatibility-only fallback shims and are not required paths for branch-tip retrieval behavior.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: keep excerpt lookup on the canonical FTS-first path so PageIndex-only excerpt IDs fail closed under regression coverage.
2. Canonical demo-path step `retrieve relevant material`: keep the FTS search cache deterministic by freezing query-shaped cache keys and invalidating cached search state after document updates.
3. Canonical demo-path steps `retrieve relevant material` and `promote or gather context into the basket`: preserve deterministic sparse retrieval payload reconstruction, including primary-source provenance, canonical downstream payload reconstruction from source bundles, basket promotion items, and basket item IDs.
4. Handoff traceability for canonical demo-path step `retrieve relevant material`: regenerate packet metadata so review covers the actual branch tip that will merge, including all post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval source/test changes.

## Files Changed

Files changed in the reviewed merge-candidate range `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`:

- `THREAD_PACKET.md`: authoritative corrected handoff packet.
- `src/qual/engine/retrieval/fts_strategy.py`: adds explicit cache invalidation support and immutable cache-key snapshots for the FTS strategy.
- `src/qual/engine/retrieval/payload.py`: preserves sparse primary provenance, canonical source-bundle-derived downstream payloads, basket promotion items, basket item IDs, and basket/context reconstruction fields deterministically.
- `src/qual/retrieval/service.py`: invalidates the FTS cache after document updates.
- `tests/unit/test_unified_retrieval.py`: covers FTS cache invalidation, sparse primary provenance reconstruction, and canonical downstream payload reconstruction from source-bundle-only context sources.

Additional files present in the reviewer trace range `adfa8cdadd43747ffbcb612e4151e262b13e52ca..HEAD`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`: stale packet mirror from earlier packet-refresh commits; not authoritative for this fixer pass because the sandbox rejects edits under `.codex` from this worktree.
- `.codex/lane_meta/feat-retrieval-fts.json`: stale lane metadata mirror from earlier packet-refresh commits; not authoritative for this fixer pass because the sandbox rejects edits under `.codex` from this worktree.

The attempted regeneration of those `.codex` mirror files failed before any file content changed:

- `apply_patch` targeting `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json`: FAIL, `patch rejected: writing outside of the project; rejected by user approval settings`.

Packet refresh commits in the trace range are reviewed as packet changes only when they touch packet files only. Commits that touch retrieval source or tests, including `0e86dfbb83606b30814de4cc2f30234867ebeda9` and `b65733d6ffb0b78532478db3d4b4853f49248c4a`, are part of the reviewed source/test trace and are not classified as metadata-only.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; the branch-tip work is folded into four meaningful tasks under the high-risk cap.
- Changed files in reviewed merge-candidate range after this fixer commit: `5`.
- Net LOC in reviewed merge-candidate range after this fixer commit: `226 insertions(+), 87 deletions(-)`, net `139`.
- Changed files in reviewer trace range after this fixer commit: `7`.
- Net LOC in reviewer trace range after this fixer commit: `510 insertions(+), 120 deletions(-)`, net `390`.
- Integrator-locked files touched: none.
- Shared-by-approval files touched: `tests/unit/test_unified_retrieval.py`.
- Lane-owned implementation files touched: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Routing/provider impact: none; no model routing or provider configuration is touched.

## Roadmap / Vision Mapping

- Roadmap items affected: `ROADMAP.md` Milestone 3 Product Readiness output/provenance contracts, with Milestone 4 Retrieval Layer groundwork.
- Vision capabilities affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling, and capability 3, Auditable generation.
- Canonical demo-path step advanced: `retrieve relevant material`. Sparse context-reference preservation also advances `promote or gather context into the basket`.
- FTS-first mapping: SQLite FTS remains the required retrieval path; PageIndex and embeddings remain fallback-only compatibility shims.
- Proposed `README.md` patch text: none.

## Commands Run

Required scope and integration gates for this corrected merge candidate:

- `python -m unittest tests.unit.test_unified_retrieval`: PASS, 56 tests.
- `python -m py_compile src/qual/engine/retrieval/fts_strategy.py && python -m unittest tests.unit.test_unified_retrieval`: PASS, 56 tests.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS.
- `make scope-check`: PASS.

Additional focused check retained from the retrieval thread:

- `python3 -m unittest tests.unit.test_unified_retrieval -v`: PASS, 56 tests.
- `python -m pytest tests/unit/test_unified_retrieval.py -q`: FAIL, environment blocker `/opt/homebrew/opt/python@3.14/bin/python3.14: No module named pytest`; replaced with `python -m unittest tests.unit.test_unified_retrieval`.

## Risks / Blockers

- No implementation blocker is known.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` remain stale because the sandbox rejected edits under `.codex` from this worktree during this fixer pass. `THREAD_PACKET.md` is the corrected authoritative handoff artifact for this fixer pass.
- This packet uses `HEAD` for the reviewed merge candidate so the final fixer commit can be included without embedding a self-referential SHA. The final fixer response reports the exact final HEAD SHA.
- The corrected post-`adfa8cd` reviewer trace range exceeds the high-risk `<=300` net LOC guidance; this is explicitly surfaced for reviewer risk assessment.
