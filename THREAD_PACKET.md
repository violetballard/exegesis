## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: authoritative branch-tip re-review packet for the actual merge candidate.
- Merge candidate: `HEAD` after the fixer commit that updates this packet; final HEAD SHA is reported by the fixer.
- Authoritative reviewed range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`.
- Scope rule: review the full range above. Do not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the endpoint, and do not treat later retrieval-code commits as metadata-only.
- Packet mirror note: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are stale packet mirrors in this worktree and still contain older narrowed-slice wording. This fixer attempted to update them again, but the sandbox rejected writes to those `.codex` paths with `Operation not permitted`. Treat this `THREAD_PACKET.md` as the source of truth for re-review.

## Required Reviewer Fixes Addressed

1. Regenerated one authoritative packet using the actual branch-tip range through `HEAD`.
2. Included all post-`adfa8cd` runtime retrieval changes: `fts_strategy.py`, `payload.py`, and `service.py`.
3. Recomputed files changed, task count, high-risk/shared budget accounting, risks, and blockers from the actual range.
4. Mapped every completed task to the canonical demo path.
5. Re-ran the required gates against the corrected merge candidate; outcomes are recorded below.
6. Recorded the stale `.codex` packet mirror write blocker so reviewers do not treat those locked mirrors as authoritative.

## Scope Completed

The branch keeps SQLite FTS as the MVP retrieval authority, removes PageIndex fallback from canonical excerpt lookup, and preserves deterministic retrieval payloads for downstream engine flows. The reviewed range also includes stable document/excerpt refs for basket promotion, normalized `retrieval_basket_promotion_refs` in source/context bundles and downstream reconstruction, and deep-copy isolation for FTS strategy hit snapshots.

Canonical demo path advanced:

1. Retrieve relevant material through the FTS-first retrieval path.
2. Promote or gather retrieved docs/excerpts into the basket using stable refs.
3. Carry retrieved context forward to later draft/revise/apply steps through deterministic payloads and auditable promotion fingerprints.

## Tasks Completed

1. FTS-first retrieval contract: made FTS-only excerpt retrieval authoritative and preserved deterministic query/result fingerprints, citation snapshots, and provenance on FTS hits. Demo path step: retrieve relevant material.
2. Deterministic payload reconstruction: normalized retrieval payloads, source bundles, provenance bundles, sparse backfills, missing-value handling, and basket-promotion refs. Demo path step: carry retrieved context forward.
3. Basket promotion refs: built stable doc/excerpt refs from FTS hits, exposed `retrieval_basket_promotion_refs`, preserved them through source-bundle/downstream reconstruction, and fingerprinted them. Demo path step: promote gathered docs/excerpts.
4. Regression coverage: maintained shared coverage for FTS-first retrieval, sparse payload reconstruction, citation/provenance helpers, FTS-only excerpt behavior, basket promotion refs, and FTS strategy snapshot isolation. Demo path step: all three retrieval-to-context handoff steps.

## Files Changed In Reviewed Range

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Runtime/test files in scope:

- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Budget / Size Accounting

- Risk: high/shared because the reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Task budget: `4/4` under the AGENTS high-risk/shared cap.
- File budget: `7/8` high-risk files changed in the actual branch-tip range.
- Size budget at handoff before this packet-only fixer edit: 7 files changed, 425 insertions, 130 deletions, net `+295`, within the `<=300` high-risk packet budget.
- Runtime/test subset at pre-final tip: 4 files changed, 175 insertions, 43 deletions, net `+132`.
- Shared-file edits: approved regression coverage in `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files: none.
- Scope remains tight to Milestone 3/4 retrieval: FTS-first retrieval, structured/auditable basket promotion refs, and no required PageIndex/embeddings path.

## Roadmap / Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 output/provenance contract readiness; Milestone 4 FTS-first retrieval orchestration, source attribution, deterministic auditable retrieval, and deferred PageIndex/embeddings.
- Vision capabilities affected: Product Vision capability 2, retrieval-first context handling; capability 3, auditable generation; capability 5, A2UI-compatible stable retrieval payloads.
- Routing/provider impact: none.
- Textual/UI impact: none.
- Alternate retrieval-mode impact: none. PageIndex and embeddings remain deferred/fallback-only.
- Proposed `README.md` patch text: none.

## Commands Run

Required final gates against the corrected merge candidate:

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS.

## Risks / Blockers

- Merge risk is high only because the handoff includes approved shared regression coverage; there are no integrator-locked file edits.
- The reviewed range intentionally includes post-`adfa8cd` retrieval code-bearing commits. They are part of the merge candidate and must be reviewed.
- The `.codex` packet mirror files are stale and write-blocked in this sandbox; this `THREAD_PACKET.md` packet is the authoritative branch-tip handoff source.
- The branch intentionally does not add embeddings, PageIndex requirements, UI rendering behavior, alternate retrieval modes, routing changes, or provider changes.
- Final HEAD SHA is reported by the fixer after commit creation.
