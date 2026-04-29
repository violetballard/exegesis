## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet refresh commit before this fixer: `3bef51f327ec4d37780b518790840cf3bf9563b7`
- Merge candidate before this metadata-only fixer: `3bef51f327ec4d37780b518790840cf3bf9563b7`
- Merge candidate after this reviewer-fix packet refresh: final SHA reported in the fixer handoff.
- Reviewed range: `378cf9a..HEAD`
- Reviewed implementation range before this metadata-only fixer: `378cf9a74a3658058079a32f186fcd254c4a4034..3bef51f327ec4d37780b518790840cf3bf9563b7`
- Review choice: this packet supersedes earlier narrowed-slice packets. Re-review must use the actual branch-tip range above, or a later split branch explicitly identified as the merge candidate.
- Canonical demo-path step advanced: `retrieve relevant material` and `promote or gather context into the basket`.

## Required Fixes Addressed

1. The reviewable branch-tip merge candidate is regenerated against `378cf9a..HEAD`, with pre-fix branch tip `3bef51f327ec4d37780b518790840cf3bf9563b7` and the final metadata-only fixer SHA reported in the handoff.
2. The packet no longer asks reviewers to approve the older `adfa8cdadd43747ffbcb612e4151e262b13e52ca` narrowed implementation slice. The actual branch-tip range is the only current merge-candidate range named for review.
3. Budget accounting is explicit for the actual branch tip. The reviewed `378cf9a74a3658058079a32f186fcd254c4a4034..3bef51f327ec4d37780b518790840cf3bf9563b7` range is high-risk/shared work and fits the AGENTS high-risk task, file, and net-LOC caps before this metadata-only packet refresh.
4. Roadmap mapping is corrected to the reviewer-required current roadmap target: `ROADMAP.md` Milestone 3 Real workflow loop, specifically FTS-first structured retrieval suitable for basket promotion.
5. The canonical demo-path step is explicit: `retrieve relevant material` and `promote or gather context into the basket`.
6. Required gates are re-run and reported below for the final branch-tip range.

## Scope Completed

The branch delivers the cumulative FTS-first retrieval slice for the MVP engine workflow loop. SQLite FTS is the canonical retrieval path; PageIndex and embeddings remain compatibility/fallback shims rather than required paths. Retrieval query construction, payload normalization, provenance bundles, source/context bundles, cache snapshots, excerpt lookup, and downstream context refs are deterministic enough for engine orchestration and auditable handoff into basket/workflow flows. The current branch-tip code hardening in `src/qual/engine/retrieval/payload.py` preserves `retrieval_context_refs` when downstream consumers reconstruct source, doc, excerpt, or context bundles from nested sparse snapshots, keeping basket-promotion refs available without requiring broader retrieval strategies. That keeps the actual branch tip aligned with `feat-retrieval-fts`: the extra implementation is retrieval payload normalization and context-ref preservation, not provider routing, model selection, or console work.

Canonical demo path advanced by the full branch tip:

1. Retrieve relevant material through SQLite FTS-backed retrieval.
2. Promote or gather context into the basket by preserving document/excerpt provenance, citations, and `retrieval_context_refs` in deterministic payload snapshots.
3. Expose promotion-ready bundle data for downstream basket/context use, including sparse nested bundle reconstruction.

## Tasks Completed

1. FTS-first retrieval contract: canonical SQLite FTS retrieval, FTS-only excerpt lookup, guarded scope handling, compatibility exports, and fallback-only PageIndex/embedding shims.
2. Deterministic payloads: normalized queries, constraints, date ranges, cache keys, ranked IDs, hit snapshots, policy metadata, citation fields, and provenance/source/context bundles.
3. Basket/workflow promotion readiness: stable context refs, fingerprints, source bundle aliases, sparse bundle rehydration, nested context-ref extraction, and downstream helper backfills.
4. Regression and packet coverage: shared canonical retrieval tests plus branch-tip handoff metadata corrected for the actual merge candidate.

## Branch-Tip Files Changed

Matches `git diff --name-status 378cf9a74a3658058079a32f186fcd254c4a4034..3bef51f327ec4d37780b518790840cf3bf9563b7` for the true merge candidate before this metadata-only fixer commit; this packet refresh itself changes `THREAD_PACKET.md` only:

- `M .codex/kickoff_packets/feat-retrieval-fts.md`
- `M .codex/lane_meta/feat-retrieval-fts.json`
- `M THREAD_PACKET.md`
- `M src/qual/engine/retrieval/payload.py`
- `M src/qual/retrieval/service.py`
- `M tests/unit/test_unified_retrieval.py`

## Focused Regression Coverage

- `tests/unit/test_unified_retrieval.py` covers FTS-first retrieval behavior, FTS-only excerpt lookup, payload normalization, sparse bundle backfills, provenance/citation fields, fingerprint stability, and promotion-ready `retrieval_context_refs`.

## Budget / Risk

Risk/budget: high/shared because shared regression coverage and runtime retrieval payload/service behavior are included in the reviewed range. Recomputed from `378cf9a74a3658058079a32f186fcd254c4a4034..3bef51f327ec4d37780b518790840cf3bf9563b7`: task budget `4/4`; file budget `6/8`; size budget `6 files changed, 422 insertions(+), 131 deletions(-)`, which is `291` net LOC and stays within the high-risk `<=300` net LOC cap before this metadata-only packet refresh. Integrator-locked files: none. Shared-by-approval files: `tests/unit/test_unified_retrieval.py` as regression coverage for this lane. Routing/provider/core entrypoint impact: none.

Required budget disposition: the regenerated actual branch-tip range fits the high-risk task, file, and net-LOC caps before this metadata-only packet refresh. Re-review should use the final fixer SHA as the branch tip and confirm the only additional change after `3bef51f327ec4d37780b518790840cf3bf9563b7` is this packet metadata update.

Packet mirror blocker: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are present in the worktree but reject writes with `Operation not permitted`; this `THREAD_PACKET.md` is the writable corrected handoff source for this fixer pass. Those protected mirrors still contain older `adfa8cd` wording and should not be used as the re-review source of truth.

## FTS-First Alignment Proof

`src/qual/retrieval/service.py` and `src/qual/engine/retrieval/fts_strategy.py` keep SQLite FTS canonical for retrieval and excerpt lookup. PageIndex and embeddings are compatibility/fallback surfaces only; they are not required for the MVP retrieval path. Context refs are built from canonical retrieval hits and carry FTS provenance so downstream basket/workflow consumers can audit source material. `src/qual/engine/retrieval/payload.py` is explicitly in scope for this branch-tip review because it preserves those refs from nested source/doc/excerpt snapshots during sparse bundle reconstruction.

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 3 Real workflow loop: FTS-first structured retrieval suitable to `retrieve relevant material` and `promote or gather context into the basket`.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling: source documents are retrieved as chunks and SQLite FTS remains the current MVP retrieval path.
- Vision capability affected: `PRODUCT_VISION.md` capability 3, Auditable generation: retrieved sources carry deterministic provenance, citation, fingerprint, and promotion references.
- Routing/provider impact: none. This branch does not change model routing, provider configuration, or provider compatibility behavior.
- Proposed `README.md` patch text: none.

## Commands Run

Fresh branch-tip fixer pass:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS (`124` tests).
- `./typecheck-test.sh` PASS.
- `make ci` PASS (`124` tests).

Validation fixer pass on `2026-04-29` against the branch-tip working tree before this fixer commit, based on `1917cde3660bddb87a93a265de15197f07fff03b`:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS (`124` tests).
- `./typecheck-test.sh` PASS.
- `make ci` PASS (`124` tests).

## Risks / Blockers

- The branch-tip merge candidate now has truthful traceability for the actual `378cf9a..HEAD` range. The only expected delta after `3bef51f327ec4d37780b518790840cf3bf9563b7` is this metadata-only packet refresh.
- Reviewers should evaluate `378cf9a..HEAD` as the current branch-tip merge candidate. Earlier narrowed-slice packet ranges, including `378cf9a..adfa8cdadd43747ffbcb612e4151e262b13e52ca`, are superseded and are not approval candidates.
