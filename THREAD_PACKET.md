## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge target: actual branch tip after the new fixer commit from this pass.
- Authoritative artifact: `THREAD_PACKET.md`. Attempts to update `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` from this worktree are blocked by OS-level permissions on `.codex`, so those mirrors must not be used as source of truth for this re-review.
- Reviewed merge-candidate range: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`, where `fd2ab6ca65ec2f93d1334c9b7df8512439725be4` is the current `main...HEAD` merge base.
- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..HEAD`; review must include all implementation, test, packet, and fixer changes through the final branch tip.
- Reviewer trace range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..HEAD`; this range includes the post-`adfa8cd` retrieval source/test changes that must be reviewed, including `0e86dfbb83606b30814de4cc2f30234867ebeda9`, `b65733d6ffb0b78532478db3d4b4853f49248c4a`, the `6bd4f5c67b38cff4de9e19e2fcef4cea5c4d2296` FTS cache-key implementation commit, and the reviewer-cited `c620f6c716f7af17fb7d88c10dd93c6b58f9fe89` payload implementation commit.
- Pre-fixer branch-tip SHA for this pass: `3eb70a253ed127ff340b84a0882657b78fd5243c`.
- Reviewer-cited submitted packet tip: `c620f6c716086af10693500e4d7eb8da9245473e`; this is implementation scope because it changes `src/qual/engine/retrieval/payload.py`.
- Final HEAD SHA: reported in the fixer final response because a commit cannot contain its own SHA.
- Handoff classification: high-risk/shared because the corrected reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

## Required Fixes Addressed

1. Regenerated this handoff against the actual branch tip intended for merge.
2. Included post-`adfa8cd` source/test changes in the reviewed trace range and file list, including changes to `src/qual/engine/retrieval/payload.py` and `tests/unit/test_unified_retrieval.py`.
3. Removed the stale claim that branch-tip packet-refresh commits are metadata-only when they touch retrieval source or tests; `b65733d6ffb0b78532478db3d4b4853f49248c4a`, `6bd4f5c67b38cff4de9e19e2fcef4cea5c4d2296`, and `c620f6c716f7af17fb7d88c10dd93c6b58f9fe89` are implementation/test scope, not metadata-only scope.
4. Made `Scope Completed`, `Tasks Completed`, `Files Changed`, and command results all refer to the same `HEAD` merge candidate.
5. Updated each completed task to name the canonical demo-path step it advances.
6. Verified the current checkout is clean and `src/qual/engine/retrieval/payload.py` contains no conflict markers.
7. Re-ran and reported the required gates on the corrected merge candidate.
8. Preserved sparse source-bundle basket promotion references when those refs are carried under `retrieval_evidence`, so source-bundle-only reconstruction remains promotable into the context basket.

## Scope Completed

The corrected merge candidate advances the canonical demo-path step `retrieve relevant material`. SQLite FTS remains the authoritative MVP retrieval path, repeated retrieval calls use an immutable cache-key snapshot, document updates invalidate cached FTS search state, excerpt lookup fails closed for PageIndex-only IDs, and sparse retrieval payload reconstruction preserves deterministic document IDs, citation refs, ranks, fingerprints, primary-source provenance, basket promotion items, and basket item IDs.

Sparse context-reference preservation also advances `promote or gather context into the basket`: source-bundle-only context reconstruction now carries a canonical downstream retrieval payload while preserving the source bundle and basket references separately, including basket promotion refs that arrive under `retrieval_evidence` in sparse source snapshots. PageIndex and embeddings remain compatibility-only fallback shims and are not required paths for branch-tip retrieval behavior.

Final handoff statement: This work makes the `retrieve relevant material` step more real by ensuring retrieval excerpts are FTS-only, deterministic, provenance-bearing, and suitable for basket/workflow promotion.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: keep excerpt lookup on the canonical FTS-first path so PageIndex-only excerpt IDs fail closed under regression coverage.
2. Canonical demo-path step `retrieve relevant material`: keep the FTS search cache deterministic by freezing query-shaped cache keys and invalidating cached search state after document updates.
3. Canonical demo-path steps `retrieve relevant material` and `promote or gather context into the basket`: preserve deterministic sparse retrieval payload reconstruction, including primary-source provenance, canonical downstream payload reconstruction from source bundles, basket promotion items, basket item IDs, and basket refs carried under sparse `retrieval_evidence`.
4. Handoff traceability for canonical demo-path step `retrieve relevant material`: regenerate packet metadata so review covers the actual branch tip that will merge, including all post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval source/test changes.

## Files Changed

Files changed in the reviewed merge-candidate range `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`:

- `THREAD_PACKET.md`: authoritative corrected handoff packet.
- `src/qual/engine/retrieval/fts_strategy.py`: adds explicit cache invalidation support and immutable cache-key snapshots for the FTS strategy.
- `src/qual/engine/retrieval/payload.py`: preserves sparse primary provenance, canonical source-bundle-derived downstream payloads, basket promotion items, basket item IDs, evidence-carried basket refs, and basket/context reconstruction fields deterministically.
- `src/qual/retrieval/service.py`: invalidates the FTS cache after document updates.
- `tests/unit/test_unified_retrieval.py`: covers FTS cache invalidation, sparse primary provenance reconstruction, and canonical downstream payload reconstruction from source-bundle-only context sources.

Additional files present in the reviewer trace range `adfa8cdadd43747ffbcb612e4151e262b13e52ca..HEAD`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`: stale packet mirror from earlier packet-refresh commits; not authoritative for this fixer pass because writes under `.codex` are blocked in this worktree.
- `.codex/lane_meta/feat-retrieval-fts.json`: stale lane metadata mirror from earlier packet-refresh commits; not authoritative for this fixer pass because writes under `.codex` are blocked in this worktree.

The attempted regeneration of those `.codex` mirror files failed before any file content changed. This was rechecked in the current fixer pass:

- `apply_patch` targeting `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json`: FAIL, `patch rejected: writing outside of the project; rejected by user approval settings`.
- `apply_patch` targeting `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, and `THREAD_PACKET.md`: FAIL, `patch rejected: writing outside of the project; rejected by user approval settings`.
- `touch .codex/.write_test`: FAIL, `Operation not permitted`.

Packet refresh commits in the trace range are reviewed as packet changes only when they touch packet files only. Commits that touch retrieval source or tests, including `0e86dfbb83606b30814de4cc2f30234867ebeda9`, `b65733d6ffb0b78532478db3d4b4853f49248c4a`, `6bd4f5c67b38cff4de9e19e2fcef4cea5c4d2296`, and `c620f6c716f7af17fb7d88c10dd93c6b58f9fe89`, are part of the reviewed source/test trace and are not classified as metadata-only.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; the branch-tip work is folded into four meaningful tasks under the high-risk cap.
- Changed files in reviewed merge-candidate range after this fixer metadata correction: `5`.
- Net LOC in reviewed merge-candidate range after this fixer metadata correction: `232 insertions(+), 90 deletions(-)`, net `142`.
- Changed files in reviewer trace range after this fixer metadata correction: `7`.
- Net LOC in reviewer trace range after this fixer metadata correction: `513 insertions(+), 120 deletions(-)`, net `393`.
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

Required scope and integration gates for this corrected merge candidate, re-run after this fixer metadata correction:

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS, 125 tests.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS, includes scope-check, format, lint, compileall/typecheck, and 125 tests.
- `rg -n <conflict-marker-pattern> src/qual/engine/retrieval/payload.py`: PASS, no conflict markers found.
- `git status --porcelain=v1 -uall`: PASS, clean before this packet edit.

Earlier retained verification from this branch-tip fixer sequence:

- `python -m unittest tests.unit.test_unified_retrieval`: PASS, 56 tests.
- `python -m unittest tests.unit.test_unified_retrieval`: PASS, 56 tests after preserving evidence-carried basket refs in source-bundle normalization.
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
- The reviewer-reported unresolved conflict in `src/qual/engine/retrieval/payload.py` is not present in this checkout; conflict-marker scan is clean and the worktree was clean before this packet edit.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` remain stale because writes under `.codex` are OS-blocked in this worktree. `THREAD_PACKET.md` is the corrected authoritative handoff artifact for this fixer pass.
- This packet uses `HEAD` for the reviewed merge candidate so the final fixer commit can be included without embedding a self-referential SHA. The final fixer response reports the exact final HEAD SHA.
- The corrected post-`adfa8cd` reviewer trace range exceeds the high-risk `<=300` net LOC guidance; this is explicitly surfaced for reviewer risk assessment.
