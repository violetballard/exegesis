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
- Reviewed implementation head: final source-bearing fixer commit SHA, reported in the final handoff response after commit creation.
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..final source-bearing fixer commit SHA reported in the final handoff response`.
- Current packet refresh commit: not applicable; this pass is source-bearing and the final commit SHA is reported in the final handoff response after commit creation.
- Gate re-run anchor before this fixer commit: `bed7e94c77bfbe78b48972b164bfebdb6ad96f57`.
- Reviewer-cited unreviewed implementation range now included: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..ea11c328588f77aec44cc0cb163f7266364cb87b`, plus the source-bearing manifest provenance commit `05dbd5e46c57d7bbfa7679bb171ad3cfe2223975`.

## Traceability Correction

This packet supersedes all earlier handoffs that described `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the reviewed implementation head or described later source-bearing branch-tip commits as metadata-only. The actual source-bearing merge candidate range before this packet refresh is:

`378cf9a74a3658058079a32f186fcd254c4a4034..05dbd5e46c57d7bbfa7679bb171ad3cfe2223975`

That range includes every retrieval implementation change through `05dbd5e46c57d7bbfa7679bb171ad3cfe2223975`, including the reviewer-cited implementation changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` in `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`.

This fixer creates a source-bearing retrieval facade correction after `bed7e94c77bfbe78b48972b164bfebdb6ad96f57`; the final HEAD SHA for that source-bearing fixer is reported with the fixer response. The refreshed packet does not classify `9e3df053f8cb56536a1908dfbce8acbd2cdadf86`, `83e52f7642a21516a3a996d099c9a50b6527c379`, `05dbd5e46c57d7bbfa7679bb171ad3cfe2223975`, this current fixer, or any other source/test-changing commit as metadata-only.

Re-review should not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the implementation head. It is an intermediate commit only.

The source-bearing manifest fingerprint refresh is commit `05dbd5e46c57d7bbfa7679bb171ad3cfe2223975`; this source-bearing fixer extends the handoff to include stricter canonical engine query normalization for loose date-range facade inputs.

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

The final source-bearing fixer also preserves `retrieval_evidence_fingerprint` on payload-derived basket-promotion items when the full promotion bundle is absent. This keeps sparse downstream payload snapshots auditable at the individual promotion-item level without requiring the original `RetrievalResult`.

This latest source-bearing delta normalizes and fingerprints `query_constraints` when a downstream payload already carries a `retrieval_basket_promotion_bundle`. That keeps service-produced and payload-derived basket-promotion bundles aligned even when tuple/list constraint shapes or blank section hints are rehydrated from sparse engine snapshots.

This final source-bearing delta also canonicalizes string-shaped scalar query constraints when sparse engine payload snapshots are rehydrated. `max_results`, `require_citations`, and `prefer_exact_matches` now normalize to stable int/bool values before query-constraint fingerprints are generated, keeping basket-promotion evidence aligned with service-produced retrieval contracts.

This latest source-bearing delta carries normalized query constraints and their fingerprint onto each basket-promotion item from both service-produced bundles and sparse downstream payload rehydration. Promoted excerpts are now self-contained enough for context-basket storage and later revise/apply audit trails without relying only on bundle-level query metadata.

This final source-bearing delta also normalizes item-level query constraints when rehydrating an existing downstream `retrieval_basket_promotion_bundle`. If a promotion item carries tuple/string-shaped constraints or a stale query-constraint fingerprint, the payload helper now canonicalizes the item constraints and regenerates the item query-constraint fingerprint before computing the promotion item fingerprint.

This current source-bearing delta adds a deterministic `retrieval_manifest_fingerprint` to the FTS manifest, diagnostics, provenance, source/context bundles, and basket-promotion evidence. That gives basket promotion and later revise/apply flows a compact audit key for the exact doc/excerpt manifest attached to promoted FTS excerpts, including when sparse downstream payloads are rehydrated.

This final source-bearing delta makes the canonical engine retrieval query builder fail closed on malformed loose `date_range` inputs before FTS execution. Mapping-shaped facade calls now accept only exactly two non-empty date-range values, keeping engine-facing retrieval constraints deterministic and aligned with the service-layer FTS contract.

Canonical demo path advanced: `vault/context material -> FTS retrieval -> retrieval evidence -> context basket promotion -> engine revise/apply`.

Before-handoff canonical demo-path statement: this work makes `retrieve relevant material` more real by making FTS-only excerpt lookup deterministic and fail-closed for PageIndex-only excerpt IDs, and it supports `promote or gather context into the basket` through stable excerpt/provenance payloads.

## Tasks Completed

1. Canonical demo-path step advanced: `retrieve relevant material`. Made SQLite FTS the authoritative MVP retrieval path while keeping PageIndex and embeddings fallback-only/deferred.
2. Canonical demo-path step advanced: `retrieve relevant material`. Stabilized FTS query, cache, constraint, date-range, shortlist, doc-type, scope, and fresh-run behavior for deterministic retrieval.
3. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Normalized retrieval payloads, provenance, citation/source/context bundles, evidence snapshots, sparse bundle rehydration, and basket-promotion evidence so downstream helpers preserve ranks, identities, policies, fingerprints, matched terms, and confidentiality profile metadata.
4. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Added fail-closed and audit-focused shared regression coverage for malformed/reversed date ranges, empty inputs, unresolved `doc:` and `collection:` scopes, FTS-only excerpt lookup and payload normalization, excerpt lookup fingerprints, cache/query snapshots, facade/export availability, basket-promotion fingerprint propagation, and payload-derived basket-promotion query-constraint rehydration.

Task accounting: `4` high-risk task groups completed, matching the high-risk task cap.

## Kickoff Budget/Limits Compliance

- Task budget: `4` high-risk task groups; completed as the four groups above.
- File count: the corrected implementation submission uses `6` source/test files plus `3` packet/artifact files.
- Size limit: exceeds the high-risk `<=300 net LOC` limit. The corrected implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..05dbd5e46c57d7bbfa7679bb171ad3cfe2223975` is `9 files changed, 1346 insertions(+), 201 deletions(-)` including packet metadata (`7 files changed, 1346 insertions(+), 137 deletions(-)` excluding `.codex` packet metadata). This packet refresh keeps that overage explicit for reviewer/integrator disposition.
- Explicit exception status: no integrator-approved size exception is recorded in the worktree. Re-review should treat the size overage as a known blocker unless the integrator grants an exception or requests a split.
- Shared-file exception status: `tests/unit/test_unified_retrieval.py` is the sole approved shared regression surface; no integrator-locked files changed.
- Routing/provider impact: none.

## Required Fixes Applied

1. Regenerated the review packet so the reviewed implementation range includes all source/test-changing commits through the actual source head `05dbd5e46c57d7bbfa7679bb171ad3cfe2223975` instead of stopping at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. Updated files changed, tasks completed, scope completed, and kickoff budget/limits compliance to match the actual implementation being submitted.
3. Re-ran the required gates on the exact branch tip intended for re-review; current outcomes are listed below.
4. Documented that the branch still exceeds the high-risk size limit and that no explicit integrator-approved size exception is present.
5. Added a final fail-closed guard so excerpt payload normalization cannot accept PageIndex resolution as a compatibility path.
6. Preserved query constraints and query-constraint fingerprints in payload-derived basket-promotion bundles so sparse promotion evidence remains auditable.
7. Preserved retrieval evidence fingerprints in payload-derived basket-promotion items so sparse promotion evidence stays aligned with service-produced promotion bundles.
8. Normalized basket-promotion bundle query constraints and regenerated missing query-constraint fingerprints when rehydrating an existing promotion bundle from downstream payload snapshots.
9. Canonicalized string-shaped scalar query constraints during sparse payload rehydration so downstream basket-promotion fingerprints do not drift from service-produced FTS retrieval contracts.
10. Added explicit per-task canonical demo-path step mappings to the completed task list.
11. Added the required before-handoff canonical demo-path statement naming how this work makes `retrieve relevant material` more real and supports `promote or gather context into the basket`.
12. Added item-level query constraints and query-constraint fingerprints to basket-promotion evidence for both direct FTS retrieval results and sparse payload-derived bundles.
13. Normalized item-level query constraints and regenerated item query-constraint fingerprints when existing downstream basket-promotion bundles are rehydrated.
14. Added deterministic retrieval manifest fingerprints to service-produced and payload-derived retrieval contracts so basket-promotion evidence can audit the exact FTS doc/excerpt manifest without rehydrating the full result.
15. Tightened canonical engine query construction so loose mapping-shaped `date_range` constraints must contain exactly two non-empty values before FTS retrieval can run.

## Commands Run

Required gates for this corrected merge candidate were re-run on 2026-05-07 against source-bearing fixer tip reported with the handoff response after commit creation.

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 132 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 132 unit tests.

Additional focused retrieval checks run earlier in this lane:

- `python3 - <<'PY' ... build_retrieval_query(...) ... PY` - passed; list-shaped date ranges normalize to the canonical tuple and scalar string date ranges fail closed with `date_range must contain exactly two non-empty values`.
- `python3 -m unittest tests.unit.test_unified_retrieval` - passed 63 retrieval tests after tightening canonical engine query date-range normalization.
- `python3 -m unittest tests.unit.test_unified_retrieval` - passed 63 retrieval tests after adding retrieval manifest fingerprints to service and payload-derived retrieval contracts.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_basket_promotion_items_backfill_query_context_from_bundle` - passed after adding item-level query constraints and query-constraint fingerprints to basket-promotion evidence.
- `python3 -m unittest tests.unit.test_unified_retrieval` - passed 63 retrieval tests after adding item-level basket-promotion query audit fields.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_basket_promotion_bundle_normalizes_query_constraints_snapshot` - passed after adding item-level query-constraint normalization for existing basket-promotion bundles.
- `python3 -m unittest tests.unit.test_unified_retrieval` - passed 63 retrieval tests after adding item-level query-constraint normalization for existing basket-promotion bundles.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_basket_promotion_bundle_normalizes_query_constraints_snapshot` - passed after scalar query-constraint canonicalization.
- `python3 - <<'PY' ... _build_retrieval_basket_promotion_bundle_from_payload(...) ... PY` - passed; sparse string-shaped `max_results`, `require_citations`, and `prefer_exact_matches` normalized to int/bool values.
- `python3 -m unittest tests.unit.test_unified_retrieval` - passed 63 retrieval tests after scalar query-constraint canonicalization.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_basket_promotion_bundle_normalizes_query_constraints_snapshot` - passed after adding basket-promotion bundle query-constraint normalization.
- `python3 -m unittest tests.unit.test_unified_retrieval` - passed 63 retrieval tests after adding basket-promotion bundle query-constraint normalization.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_basket_promotion_items_backfill_query_context_from_bundle` - passed after preserving payload-derived promotion-item retrieval evidence fingerprints.
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
