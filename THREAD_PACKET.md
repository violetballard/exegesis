## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge target: current branch tip after this fixer commit.
- Authoritative artifact: `THREAD_PACKET.md`. Attempts to update `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` from this worktree are blocked by sandbox approval settings, so those stale mirrors must not be used as source of truth for this re-review.
- Authoritative reviewed range: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`, where `fd2ab6ca65ec2f93d1334c9b7df8512439725be4` is the current `main...HEAD` merge base.
- Pre-fixer branch-tip SHA for this pass: `86401db3ae8284915540c9b7b43c2dfc0bf37253`.
- Final HEAD SHA: reported in the fixer final response because a commit cannot contain its own SHA.
- Handoff classification: high-risk/shared because the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

## Required Fixes Addressed

1. Regenerated this packet so the reviewed implementation range, cumulative range, file list, tasks, and command results all describe the same merge candidate: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`.
2. Removed/split the non-retrieval planner changes from this handoff scope by anchoring review to the current merge-base range. `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` are not changed in `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD` and are not part of this retrieval-lane merge candidate.
3. Updated every completed task below to name the canonical demo-path step it advances.
4. Re-ran and reported the required gates against this corrected merge candidate.

## Scope Completed

This corrected merge candidate advances the canonical demo-path step `retrieve relevant material`. SQLite FTS remains the authoritative MVP retrieval path, repeated retrieval calls use an immutable cache-key snapshot, document updates invalidate cached FTS search state, excerpt lookup fails closed for PageIndex-only IDs, and sparse retrieval payload reconstruction preserves deterministic document IDs, citation refs, ranks, fingerprints, primary-source provenance, basket promotion items, and basket item IDs.

Sparse context-reference preservation also advances `promote or gather context into the basket`: source-bundle-only context reconstruction now carries a canonical downstream retrieval payload while preserving the source bundle and basket references separately, including basket promotion refs that arrive under `retrieval_evidence` in sparse source snapshots. PageIndex and embeddings remain compatibility-only fallback shims and are not required paths for branch-tip retrieval behavior.

Final handoff statement: this work makes the `retrieve relevant material` step more real by ensuring retrieval excerpts are FTS-only, deterministic, provenance-bearing, and suitable for basket/workflow promotion.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: keep excerpt lookup on the canonical FTS-first path so PageIndex-only excerpt IDs fail closed under regression coverage.
2. Canonical demo-path step `retrieve relevant material`: keep the FTS search cache deterministic by freezing query-shaped cache keys and invalidating cached search state after document updates.
3. Canonical demo-path steps `retrieve relevant material` and `promote or gather context into the basket`: preserve deterministic sparse retrieval payload reconstruction, including primary-source provenance, canonical downstream payload reconstruction from source bundles, basket promotion items, basket item IDs, and basket refs carried under sparse `retrieval_evidence`.
4. Handoff traceability for canonical demo-path step `retrieve relevant material`: regenerate packet metadata so review covers the actual branch tip that will merge and excludes non-retrieval planner/test changes from this retrieval-lane handoff.

## Files Changed

Files changed in the reviewed merge-candidate range `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`:

- `THREAD_PACKET.md`: authoritative corrected handoff packet.
- `src/qual/engine/retrieval/fts_strategy.py`: adds explicit cache invalidation support and immutable cache-key snapshots for the FTS strategy.
- `src/qual/engine/retrieval/payload.py`: preserves sparse primary provenance, canonical source-bundle-derived downstream payloads, basket promotion items, basket item IDs, evidence-carried basket refs, and basket/context reconstruction fields deterministically.
- `src/qual/retrieval/service.py`: invalidates the FTS cache after document updates.
- `tests/unit/test_unified_retrieval.py`: approved shared retrieval regression coverage for FTS cache invalidation, sparse primary provenance reconstruction, and canonical downstream payload reconstruction from source-bundle-only context sources.

Non-retrieval planner/test files are explicitly out of scope for this merge candidate:

- `codex_packet_handoff/tools/planner.py`: unchanged in `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`.
- `tests/unit/test_packet_planner.py`: unchanged in `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; the branch-tip work is folded into four meaningful tasks under the high-risk cap.
- Changed files in reviewed merge-candidate range after this fixer correction: `5`.
- Pre-fixer merge-candidate diff before this packet edit: `5 files changed, 247 insertions(+), 89 deletions(-)`.
- Integrator-locked files touched: none.
- Shared-by-approval files touched: `tests/unit/test_unified_retrieval.py`.
- Lane-owned implementation files touched: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Routing/provider impact: none; no model routing or provider configuration is touched.

## Roadmap / Vision Mapping

- Roadmap items affected: `ROADMAP.md` Milestone 4 Retrieval Layer, especially FTS-first ingestion/index path, retrieval orchestration before drafting/diff generation, and auditable deterministic retrieval paths.
- Vision capabilities affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling, and capability 3, Auditable generation.
- Canonical demo-path step advanced: `retrieve relevant material`. Sparse context-reference preservation also advances `promote or gather context into the basket`.
- FTS-first mapping: SQLite FTS remains the required retrieval path; PageIndex and embeddings remain fallback-only compatibility shims.
- Proposed `README.md` patch text: none.

## Commands Run

Required scope and integration gates for this corrected merge candidate:

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS, 125 tests.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS, includes scope-check, format, lint, compileall/typecheck, and 125 tests.

Earlier retained verification from the retrieval fixer sequence:

- `python -m unittest tests.unit.test_unified_retrieval`: PASS, 56 tests.
- `python -m py_compile src/qual/engine/retrieval/fts_strategy.py && python -m unittest tests.unit.test_unified_retrieval`: PASS, 56 tests.
- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS, 125 tests.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS.

## Risks / Blockers

- No implementation blocker is known.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` remain stale because `apply_patch` to those mirrors failed with `patch rejected: writing outside of the project; rejected by user approval settings`.
- This packet uses `HEAD` for the reviewed merge candidate so the final fixer commit can be included without embedding a self-referential SHA. The final fixer response reports the exact final HEAD SHA.
- The approved shared regression file is limited to `tests/unit/test_unified_retrieval.py`; no integrator-locked files are touched.
