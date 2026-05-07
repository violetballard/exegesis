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
- Reviewed implementation head: final branch tip reported in the fixer handoff after this packet edit.
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..final branch tip reported in the fixer handoff`.
- Current branch head before this packet edit: `fc52e1621d7321321e8aa5ec6811a3fd447dcc6d`.
- Current pass role: source-bearing retrieval finalization that keeps sparse doc/excerpt bundle citations rehydratable from citation snapshots.

## Traceability Correction

This packet supersedes all earlier handoffs that described `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the reviewed implementation head or described later source-bearing branch-tip commits as metadata-only. The actual source-bearing merge candidate range before this packet refresh is:

`378cf9a74a3658058079a32f186fcd254c4a4034..83e52f7642a21516a3a996d099c9a50b6527c379`

That range includes every retrieval implementation change through `83e52f7642a21516a3a996d099c9a50b6527c379`, including the reviewer-cited implementation changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` in `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`.

This fixer creates a packet refresh commit after `83e52f7642a21516a3a996d099c9a50b6527c379`; the final HEAD SHA for that packet refresh is reported with the fixer response. The refreshed packet does not classify `9e3df053f8cb56536a1908dfbce8acbd2cdadf86`, `83e52f7642a21516a3a996d099c9a50b6527c379`, or any other source/test-changing commit as metadata-only.

Re-review should not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the implementation head. It is an intermediate commit only.

`51ee03de162297cce0dfafb2435fb33a7189807d` is also source-bearing. It modifies `src/qual/engine/retrieval/payload.py` so basket-promotion item rehydration normalizes item-level `query_date_range` and `matched_terms` values before promotion-item fingerprinting.

`60ec82aad820530cd1011b36a92404dfc07e37d7` is also source-bearing. It modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `tests/unit/test_unified_retrieval.py` so FTS basket-promotion items expose and rehydrate deterministic `basket_item_id` values of the form `retrieval:fts:<excerpt_id>`.

`5c87b08a9f7ca5a4dabc23fc1a80214276a882e9` is also source-bearing. It modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `tests/unit/test_unified_retrieval.py` so basket-promotion item ID generation remains FTS-only; PageIndex/embedding-shaped sparse promotion snapshots fail closed instead of receiving promotable `retrieval:<strategy>:<excerpt_id>` IDs.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so direct scalar `doc_types` constraints normalize as one FTS filter and the shared regression surface covers that service path.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so document ingestion canonicalizes stored `doc_type` metadata before FTS indexing. This keeps canonical query filters such as scalar `"memo"` aligned with documents ingested using whitespace or case variants such as `" Memo "`.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py` and `THREAD_PACKET.md` so sparse downstream payloads that contain empty primary summary fields can still rehydrate primary document and excerpt provenance from citation snapshots. This keeps retrieval source/context bundles deterministic for basket promotion and later revise/apply consumers without reintroducing deferred retrieval strategies.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse downstream payloads that omit explicit doc/excerpt bundle snapshots and provenance citation arrays still rehydrate bundle citations from the canonical retrieval citation bundle. This keeps citation-backed source/context bundles deterministic for basket promotion and later revise/apply consumers.

Packet-only commits after `5c87b08a9f7ca5a4dabc23fc1a80214276a882e9` refresh traceability and gate evidence only through `f9bdab5ded16e44476d773a24249c64442df2f3a`. The source-bearing passes after that packet-only refresh change `src/qual/retrieval/service.py` and `tests/unit/test_unified_retrieval.py`; reviewers should include the final branch tip reported in the fixer handoff when re-reviewing the merge candidate.

Tracked packet note for this fixer pass: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are ignored local automation metadata in this branch worktree and are not tracked at `HEAD`. Treat this tracked `THREAD_PACKET.md` file as the authoritative corrected handoff packet for re-review.

Re-review should not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the implementation head. It is an intermediate implementation commit only.

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

This finalization pass also backfills sparse doc and excerpt bundle citation arrays from the canonical retrieval citation bundle when a downstream payload omits explicit bundle snapshots and provenance citation arrays. That keeps citation evidence available to context-basket promotion and revise/apply consumers that rehydrate from sparse engine payloads.

Canonical demo path advanced: `vault/context material -> FTS retrieval -> retrieval evidence -> context basket promotion -> engine revise/apply`.

Before-handoff canonical demo-path statement: this work makes `retrieve relevant material` more real by making FTS-only excerpt lookup deterministic and fail-closed for PageIndex-only excerpt IDs, and it supports `promote or gather context into the basket` through stable excerpt/provenance payloads.

## Tasks Completed

1. Canonical demo-path step advanced: `retrieve relevant material`. Made SQLite FTS the authoritative MVP retrieval path while keeping PageIndex and embeddings fallback-only/deferred.
2. Canonical demo-path step advanced: `retrieve relevant material`. Stabilized FTS query, cache, constraint, date-range, shortlist, doc-type, scope, and fresh-run behavior for deterministic retrieval.
3. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Normalized retrieval payloads, provenance, citation/source/context bundles, evidence snapshots, sparse bundle rehydration, retrieval manifest fingerprints, and basket-promotion evidence, including item-level date-range and matched-term normalization before basket-promotion fingerprinting and deterministic FTS-only `basket_item_id` values for promotion.
4. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Added fail-closed and audit-focused regression coverage for malformed/reversed date ranges, empty inputs, unresolved scopes, FTS-only excerpt lookup and payload normalization, excerpt lookup fingerprints, cache/query snapshots, facade/export availability, basket-promotion fingerprint propagation, sparse basket item ID rehydration, and non-FTS basket item ID rejection.
5. Canonical demo-path step advanced: `promote or gather context into the basket`. Recomputed basket-promotion fingerprints after snapshot normalization so stale sparse bundle fingerprints cannot survive rehydration.
6. Canonical demo-path step advanced: `retrieve relevant material`. Aligned direct service scalar `doc_types` constraints with facade normalization so a scalar text filter is treated as one deterministic FTS filter, not character-split filter noise.
7. Canonical demo-path step advanced: `retrieve relevant material`. Canonicalized stored document `doc_type` values before metadata/FTS writes so normalized FTS filters match ingested documents deterministically and provenance emits the canonical filtered type.
8. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Backfilled sparse primary document/excerpt provenance from citation snapshots when summary fields are empty, keeping rehydrated retrieval context auditable for basket promotion and later revise/apply consumers.
9. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Backfilled sparse doc/excerpt bundle citation arrays from the canonical citation bundle when explicit bundle snapshots and provenance citation arrays are absent.

Task accounting: `9` high-risk task groups are present in the cumulative branch after this source-bearing finalization pass, exceeding the high-risk task cap and requiring the same integration decision already noted for the size overage.

## Kickoff Budget/Limits Compliance

- Task budget: `4` high-risk task groups; this cumulative branch now has `9` source-bearing task groups after the sparse doc/excerpt bundle citation fallback fix.
- File count: the corrected source-bearing range before this pass changes `6` source/test files plus `3` packet/artifact files; this pass changes `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md`.
- Size accounting: the corrected source-bearing range `378cf9a74a3658058079a32f186fcd254c4a4034..final branch tip reported in the fixer handoff` is `9 files changed, 1621 insertions(+), 221 deletions(-)` including this source-bearing fix and packet refresh.
- Size limit status: exceeds the high-risk `<=8 files` and `<=300 net LOC` limits.
- Explicit exception status: no integrator-approved size or task-budget exception is recorded in this worktree. Because the full source-bearing range remains together, this is a known blocker for approval until the integrator grants an exception or requests a branch split.
- Shared-file exception status: `tests/unit/test_unified_retrieval.py` is the sole approved shared regression surface; no integrator-locked files changed.
- Routing/provider impact: none.

## Required Fixes Applied

1. Regenerated the review packet so the reviewed implementation range includes all source/test-changing commits through the actual branch tip `83e52f7642a21516a3a996d099c9a50b6527c379` instead of stopping at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
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

## Commands Run

Required gates for this corrected merge candidate were re-run on 2026-05-07 after the packet updates. This fixer changes packet metadata only; the reviewed implementation range remains `378cf9a74a3658058079a32f186fcd254c4a4034..83e52f7642a21516a3a996d099c9a50b6527c379`. The final packet refresh commit SHA is reported with the handoff response after commit creation.

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 136 unit tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 136 unit tests.

Additional focused retrieval checks run earlier in this lane:

- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_constraints_accept_scalar_doc_type_as_one_filter -q` - passed after aligning direct service scalar doc-type constraint normalization with the canonical facade path.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_add_document_canonicalizes_doc_type_before_fts_filtering -q` - passed after canonicalizing stored document doc types before FTS indexing.
- `python3 - <<'PY' ... _build_retrieval_provenance_from_payload(...) ... PY` - passed; sparse primary document/excerpt provenance fields are backfilled from citation snapshots when summary fields are empty.
- `python3 -m compileall -q src/qual/engine/retrieval/payload.py` - passed after the sparse provenance citation fallback fix.
- `python3 -m unittest tests.unit.test_unified_retrieval -q` - passed 66 unified retrieval tests after the sparse provenance citation fallback fix.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_sparse_payload_doc_and_excerpt_bundles_use_citation_fallbacks -q` - passed after adding sparse doc/excerpt bundle citation fallback coverage.
- `python3 -m unittest tests.unit.test_unified_retrieval -q` - passed 67 unified retrieval tests after the sparse doc/excerpt bundle citation fallback fix.
- `python3 -m unittest tests.unit.test_unified_retrieval -q` - passed 66 unified retrieval tests after the stored doc-type canonicalization fix.
- `python3 -m unittest tests.unit.test_unified_retrieval -q` - passed 65 unified retrieval tests after the direct scalar doc-type normalization fix.
- `python3 -m unittest tests.unit.test_unified_retrieval -k basket_promotion -q` - passed 3 focused basket-promotion tests after recomputing normalized basket-promotion fingerprints.
- `python3 - <<'PY' ... _build_retrieval_basket_promotion_bundle_from_payload(...) ... PY` - passed; stale query constraint, promotion item, and promotion bundle fingerprints are recomputed after sparse basket-promotion snapshot normalization.
- `python3 -m unittest tests.unit.test_unified_retrieval -q` - passed 64 unified retrieval tests after adding deterministic FTS-only `basket_item_id` output and rehydration.
- `python3 -m compileall -q src/qual/retrieval src/qual/engine/retrieval tests/unit/test_unified_retrieval.py` - passed after the final source-bearing basket item ID fix.
- `python3 -m unittest tests.unit.test_unified_retrieval -k basket_promotion -q` - passed 3 focused basket-promotion tests after the FTS-only basket item ID guard.
- `python3 -m unittest tests.unit.test_unified_retrieval` - passed after unordered date-range containers were rejected in facade/service normalization.
- `python3 - <<'PY' ... build_retrieval_query(...) ... RetrievalConstraints(...) ... PY` - passed; unordered set-shaped date ranges fail closed in both the engine facade and service constraints, scalar string date ranges remain rejected, and ordered list-shaped date ranges still normalize to the canonical tuple.
- `python -m pytest tests/unit/test_unified_retrieval.py` - blocked because the active Python interpreter had no `pytest` module installed.

## Remaining Risks Or Blockers

- The corrected cumulative range exceeds the high-risk size limit. No explicit integrator-approved size exception is present in the worktree.
- All source-bearing work is now included in the reviewed implementation range; there is no longer a metadata-only branch-tip claim hiding source/test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 Product Readiness generation provenance and Milestone 4 Retrieval Layer FTS-first retrieval orchestration/source attribution.
- Product Vision capabilities affected: `2. Retrieval-first context handling` and `3. Auditable generation`.
- Architecture alignment: retrieval stays in `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`; no provider/routing/core app entrypoints are touched.
- Proposed `README.md` patch text: none.
