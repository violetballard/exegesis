## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip after this reviewer-fix packet refresh; final SHA is reported in the fixer handoff.
- Reviewed range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD`
- Review choice: this packet supersedes earlier narrowed-slice packets. Re-review must use the branch-tip range above, or a later split branch explicitly identified as the merge candidate.
- Canonical demo-path step advanced: retrieve relevant material through the FTS-first retrieval service, then expose stable context/promotion refs for downstream basket and workflow use.

## Required Fixes Addressed

1. The reviewable branch-tip merge candidate is regenerated against `d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD`.
2. The packet no longer asks reviewers to approve an older narrowed implementation slice. The branch-tip range is the only current merge-candidate range named for review.
3. Budget accounting is explicit for the actual branch tip. The current full branch is high-risk/shared work and exceeds the AGENTS high-risk size and file caps; integration requires either a split into budget-compliant high-risk handoffs or explicit integrator approval for the exception before approval.
4. Roadmap mapping is corrected to the reviewer-required current roadmap target: `ROADMAP.md` Milestone 3 Real workflow loop, specifically FTS-first structured retrieval suitable for basket promotion.
5. Required gates are re-run and reported below for the final branch-tip range.

## Scope Completed

The branch delivers the cumulative FTS-first retrieval slice for the MVP engine workflow loop. SQLite FTS is the canonical retrieval path; PageIndex and embeddings remain compatibility/fallback shims rather than required paths. Retrieval query construction, payload normalization, provenance bundles, source/context bundles, cache snapshots, excerpt lookup, and downstream context refs are deterministic enough for engine orchestration and auditable handoff into basket/workflow flows. The current branch-tip code hardening preserves `retrieval_context_refs` when downstream consumers reconstruct source, doc, excerpt, or context bundles from nested sparse snapshots, keeping basket-promotion refs available without requiring broader retrieval strategies.

Canonical demo path advanced by the full branch tip:

1. Retrieve relevant material through SQLite FTS-backed retrieval.
2. Preserve document/excerpt provenance and citations in deterministic payload snapshots.
3. Expose and preserve `retrieval_context_refs` and promotion-ready bundle data for downstream basket/context use, including sparse nested bundle reconstruction.

## Tasks Completed

1. FTS-first retrieval contract: canonical SQLite FTS retrieval, FTS-only excerpt lookup, guarded scope handling, compatibility exports, and fallback-only PageIndex/embedding shims.
2. Deterministic payloads: normalized queries, constraints, date ranges, cache keys, ranked IDs, hit snapshots, policy metadata, citation fields, and provenance/source/context bundles.
3. Basket/workflow promotion readiness: stable context refs, fingerprints, source bundle aliases, sparse bundle rehydration, nested context-ref extraction, and downstream helper backfills.
4. Regression and packet coverage: shared canonical retrieval tests plus packet planner coverage and branch-tip handoff metadata corrected for the actual merge candidate.

## Branch-Tip Files Changed

Matches `git diff --name-status d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD` for the true merge candidate:

- `M .codex/kickoff_packets/feat-retrieval-fts.md`
- `M .codex/lane_meta/feat-retrieval-fts.json`
- `M THREAD_PACKET.md`
- `M codex_packet_handoff/tools/planner.py`
- `M src/qual/engine/retrieval/__init__.py`
- `A src/qual/engine/retrieval/embeddings_strategy.py`
- `M src/qual/engine/retrieval/fts_strategy.py`
- `A src/qual/engine/retrieval/pageindex_strategy.py`
- `M src/qual/engine/retrieval/payload.py`
- `M src/qual/retrieval/__init__.py`
- `M src/qual/retrieval/service.py`
- `A tests/unit/test_packet_planner.py`
- `M tests/unit/test_unified_retrieval.py`

## Focused Regression Coverage

- `tests/unit/test_unified_retrieval.py` covers FTS-first retrieval behavior, FTS-only excerpt lookup, payload normalization, sparse bundle backfills, provenance/citation fields, fingerprint stability, and promotion-ready `retrieval_context_refs`.
- `tests/unit/test_packet_planner.py` covers packet-planner metadata emitted for handoff traceability.

## Budget / Risk

Risk/budget: high/shared because shared regression coverage and runtime retrieval payload/service behavior are included in the reviewed range. Recomputed from `d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD` including this packet refresh: task budget `4/4`; file budget `13/8`; size budget `13 files changed, 1973 insertions(+), 264 deletions(-)`, which is `1709` net LOC and exceeds the high-risk `<=300` net LOC cap. Integrator-locked files: none. Shared-by-approval files: `tests/unit/test_unified_retrieval.py` and `tests/unit/test_packet_planner.py` as regression/packet coverage for this lane. Routing/provider/core entrypoint impact: none.

Required budget disposition: do not approve the full branch tip under normal AGENTS high-risk enforcement unless the integrator grants an explicit budget exception. Without that exception, split the work into budget-compliant high-risk handoffs, each capped at `4` meaningful tasks, `<=8` files, and `<=300` net LOC, and regenerate each split packet against its intended merge-candidate range.

## FTS-First Alignment Proof

`src/qual/retrieval/service.py` and `src/qual/engine/retrieval/fts_strategy.py` keep SQLite FTS canonical for retrieval and excerpt lookup. PageIndex and embeddings are compatibility/fallback surfaces only; they are not required for the MVP retrieval path. Context refs are built from canonical retrieval hits and carry FTS provenance so downstream basket/workflow consumers can audit source material. `src/qual/engine/retrieval/payload.py` now preserves those refs from nested source/doc/excerpt snapshots during sparse bundle reconstruction.

## Roadmap / Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 3 Real workflow loop: FTS-first structured retrieval suitable for basket promotion.
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

## Risks / Blockers

- The branch-tip merge candidate now has truthful traceability, but it exceeds the high-risk AGENTS size/file budget for a single handoff. This remains an integration blocker unless the integrator approves the exception or the branch is split into compliant handoffs.
- Reviewers should evaluate `d7fd5d200358287fa42a18d39e2b277463b9b69f..HEAD` as the current branch-tip merge candidate. Earlier narrowed-slice packet ranges are superseded and are not approval candidates.
