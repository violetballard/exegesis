## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval handoff for the FTS-first retrieval lane.
- Risk reason: approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.
- Authoritative reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`.
- Authoritative reviewed implementation head: `b0b046271168b6d058e60b7a97080bebf5220781`.
- Authoritative reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..b0b046271168b6d058e60b7a97080bebf5220781`.
- Reviewer-cited unreviewed implementation range now included: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..b0b046271168b6d058e60b7a97080bebf5220781`.

## Traceability Correction

This packet supersedes all earlier handoffs that described `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the reviewed implementation head or described later branch-tip commits as metadata-only. The actual merge candidate range is:

`378cf9a74a3658058079a32f186fcd254c4a4034..b0b046271168b6d058e60b7a97080bebf5220781`

That range includes every non-metadata retrieval change through `b0b046271168b6d058e60b7a97080bebf5220781`, including the reviewer-cited implementation changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` in `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `tests/unit/test_unified_retrieval.py`.

This fixer creates a metadata-only packet refresh commit after `b0b046271168b6d058e60b7a97080bebf5220781`; the final HEAD SHA for that packet refresh is reported with the fixer response. The refreshed packet does not classify `b0b046271168b6d058e60b7a97080bebf5220781` as metadata-only.

Re-review should not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the implementation head. It is an intermediate commit only.

## Files Changed

Source and shared regression implementation surface in the corrected range:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Packet/artifact surface in the corrected range:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

## Scope Completed

SQLite FTS remains the required MVP retrieval path. PageIndex and embeddings remain deferred or compatibility-only fallback surfaces and are not reintroduced as required paths.

The branch makes FTS retrieval deterministic and auditable across query construction, cache keys, fresh-run cache snapshots, query snapshots, result payloads, excerpt lookup, citation/provenance bundles, sparse source/context bundle rehydration, date-range propagation, shortlist query fingerprints, matched-term provenance, result fingerprints, doc identity, doc rank, doc type, strategy aliases, query constraints, and basket-promotion evidence.

The branch also carries deterministic retrieval evidence fingerprints into diagnostics, provenance, source bundles, promotion bundles, and promotion items so downstream basket/revise/apply flows can audit the exact FTS evidence snapshot attached to promoted excerpts without rehydrating the whole retrieval result.

The prior implementation delta tightened the canonical excerpt payload normalizer so PageIndex-sourced excerpt payloads fail closed before they can be normalized into engine-facing retrieval context. The guard keeps excerpt lookup and basket-promotion inputs FTS-only while preserving the existing canonical FTS lookup payload shape.

The latest implementation delta preserves normalized query constraints and their fingerprint when rehydrating basket-promotion bundles from downstream payload snapshots. This keeps payload-derived promotion evidence aligned with service-produced bundles for downstream basket promotion and later revise/apply audit trails.

Canonical demo path advanced: `vault/context material -> FTS retrieval -> retrieval evidence -> context basket promotion -> engine revise/apply`.

## Tasks Completed

1. Made SQLite FTS the authoritative MVP retrieval path while keeping PageIndex and embeddings fallback-only/deferred.
2. Stabilized FTS query, cache, constraint, date-range, shortlist, doc-type, scope, and fresh-run behavior for deterministic retrieval.
3. Normalized retrieval payloads, provenance, citation/source/context bundles, evidence snapshots, sparse bundle rehydration, and basket-promotion evidence so downstream helpers preserve ranks, identities, policies, fingerprints, matched terms, and confidentiality profile metadata.
4. Added fail-closed and audit-focused shared regression coverage for malformed/reversed date ranges, empty inputs, unresolved `doc:` and `collection:` scopes, FTS-only excerpt lookup and payload normalization, excerpt lookup fingerprints, cache/query snapshots, facade/export availability, basket-promotion fingerprint propagation, and payload-derived basket-promotion query-constraint rehydration.

Task accounting: `4` high-risk task groups completed, matching the high-risk task cap.

## Kickoff Budget/Limits Compliance

- Task budget: `4` high-risk task groups; completed as the four groups above.
- File count: the corrected implementation submission uses `6` source/test files plus `3` packet/artifact files.
- Size limit: exceeds the high-risk `<=300 net LOC` limit. The corrected implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..b0b046271168b6d058e60b7a97080bebf5220781` is `9 files changed, 1062 insertions(+), 199 deletions(-)`. This packet refresh keeps that overage explicit for reviewer/integrator disposition.
- Explicit exception status: no integrator-approved size exception is recorded in the worktree. Re-review should treat the size overage as a known blocker unless the integrator grants an exception or requests a split.
- Shared-file exception status: `tests/unit/test_unified_retrieval.py` is the sole approved shared regression surface; no integrator-locked files changed.
- Routing/provider impact: none.

## Required Fixes Applied

1. Regenerated the review packet so the reviewed implementation range includes all non-metadata commits through the actual branch tip instead of stopping at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. Updated files changed, tasks completed, scope completed, and kickoff budget/limits compliance to match the actual implementation being submitted.
3. Re-ran the required gates on the exact branch tip intended for re-review; current outcomes are listed below.
4. Documented that the branch still exceeds the high-risk size limit and that no explicit integrator-approved size exception is present.
5. Added a final fail-closed guard so excerpt payload normalization cannot accept PageIndex resolution as a compatibility path.
6. Preserved query constraints and query-constraint fingerprints in payload-derived basket-promotion bundles so sparse promotion evidence remains auditable.

## Commands Run

Required gates for this final fixer state were re-run on 2026-05-07 after the
latest retrieval implementation delta. The final packet refresh commit is
metadata-only, so these results apply to the corrected branch tip without
changing the implementation review range above.

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`; no branch-specific policy was configured.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 131 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 131 unit tests.

Additional focused retrieval checks run earlier in this lane:

- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_basket_promotion_items_backfill_query_context_from_bundle` - passed after preserving payload-derived basket-promotion query constraints.
- `python -m pytest tests/unit/test_unified_retrieval.py` - blocked because the active Python interpreter has no `pytest` module installed.
- `python3 -m unittest tests.unit.test_unified_retrieval` - passed 62 retrieval tests after the final FTS-only excerpt payload normalization guard.
- `python -m unittest tests.unit.test_unified_retrieval` - passed 61 retrieval tests after retrieval evidence fingerprint hardening.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_downstream_payload_exposes_policy_and_diagnostics_snapshot tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_basket_promotion_items_backfill_query_context_from_bundle` - passed.

## Remaining Risks Or Blockers

- The corrected cumulative range exceeds the high-risk size limit. No explicit integrator-approved size exception is present in the worktree.
- All source-bearing work is now included in the reviewed implementation range; there is no longer a metadata-only branch-tip claim hiding source/test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 Product Readiness generation provenance and Milestone 4 Retrieval Layer FTS-first retrieval orchestration/source attribution.
- Product Vision capabilities affected: `2. Retrieval-first context handling` and `3. Auditable generation`.
- Architecture alignment: retrieval stays in `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`; no provider/routing/core app entrypoints are touched.
- Proposed `README.md` patch text: none.
