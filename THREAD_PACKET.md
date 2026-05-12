## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval handoff for the FTS-first retrieval lane.
- Canonical demo-path step advanced before handoff: `retrieve relevant material`; deterministic payload/provenance output also strengthens `promote or gather context into the basket`.
- Risk reason: approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.
- Authoritative reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`.
- Reviewed source-bearing implementation head: this source-bearing fixer commit; final branch tip SHA is reported in the fixer final response.
- Reviewed source-bearing implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` on branch `codex/feat-retrieval-fts`.
- Packet update note: this commit updates retrieval basket-promotion item snapshots, sparse excerpt-hit rehydration, the approved shared regression surface, and `THREAD_PACKET.md` so context-basket promotion items carry the same deterministic `query_constraints_fingerprint` already present on promotion bundle items; the final branch tip SHA is reported in the fixer final response.
- Current pass role: source-bearing FTS-first basket-promotion query-constraint fingerprint finalization for canonical context-basket promotion availability.

## Traceability Correction

This packet supersedes earlier handoffs that described `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the final reviewed implementation head or described later source/test-changing commits as metadata-only.

The actual source-bearing merge candidate for this branch is:

`378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` on branch `codex/feat-retrieval-fts`

That range includes every intended retrieval source/test change through this final source-bearing fixer commit, including the reviewer-cited post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` changes in `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`.

`beed411ecb15821f0cf145bd3ad68d59c996801c` is source-bearing. It modifies `src/qual/engine/retrieval/__init__.py`, `src/qual/retrieval/service.py`, and `THREAD_PACKET.md`. It must not be treated as metadata-only.

`51ee03de162297cce0dfafb2435fb33a7189807d` is also source-bearing. It modifies `src/qual/engine/retrieval/payload.py` so basket-promotion item rehydration normalizes item-level `query_date_range` and `matched_terms` values before promotion-item fingerprinting.

`60ec82aad820530cd1011b36a92404dfc07e37d7` is also source-bearing. It modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `tests/unit/test_unified_retrieval.py` so FTS basket-promotion items expose and rehydrate deterministic `basket_item_id` values of the form `retrieval:fts:<excerpt_id>`.

`5c87b08a9f7ca5a4dabc23fc1a80214276a882e9` is also source-bearing. It modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `tests/unit/test_unified_retrieval.py` so basket-promotion item ID generation remains FTS-only; PageIndex/embedding-shaped sparse promotion snapshots fail closed instead of receiving promotable `retrieval:<strategy>:<excerpt_id>` IDs.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/__init__.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so the engine retrieval facade exports `retrieve_auto` through `__all__`. The callable already routed to the canonical FTS-first implementation; this makes export-list consumers see the default retrieval entrypoint alongside the explicit FTS entrypoint.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so direct scalar `doc_types` constraints normalize as one FTS filter and the shared regression surface covers that service path.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so document ingestion canonicalizes stored `doc_type` metadata before FTS indexing. This keeps canonical query filters such as scalar `"memo"` aligned with documents ingested using whitespace or case variants such as `" Memo "`.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py` and `THREAD_PACKET.md` so sparse downstream payloads that contain empty primary summary fields can still rehydrate primary document and excerpt provenance from citation snapshots. This keeps retrieval source/context bundles deterministic for basket promotion and later revise/apply consumers without reintroducing deferred retrieval strategies.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse downstream payloads that omit explicit doc/excerpt bundle snapshots and provenance citation arrays still rehydrate bundle citations from the canonical retrieval citation bundle. This keeps citation-backed source/context bundles deterministic for basket promotion and later revise/apply consumers.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py` and `THREAD_PACKET.md` so sparse citation bundle normalization strips stale or non-FTS `basket_item_id` values from excerpt citations. Existing FTS basket IDs that match `retrieval:fts:<excerpt_id>` are preserved, while PageIndex/embedding-shaped or mismatched IDs fail closed before source/context bundle rehydration.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so direct FTS excerpt lookup trims padded excerpt IDs, fails blank excerpt IDs before FTS lookup, and returns the same deterministic `retrieval:fts:<excerpt_id>` basket item identity used by retrieval basket-promotion bundles.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `THREAD_PACKET.md` so accepted mixed-case or padded FTS strategy labels still emit canonical lower-case `retrieval:fts:<excerpt_id>` basket item IDs while non-FTS strategies continue to fail closed.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so excerpt hit snapshots and excerpt citation snapshots expose the same deterministic FTS-only `basket_item_id` used by context-basket promotion bundles. Sparse citation normalization now mints missing FTS citation basket IDs and still strips stale or non-FTS IDs.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so downstream payload/source/context/provenance/diagnostics/basket snapshots normalize `citation_status` booleans and counts before copy-safe rehydration and fingerprinting, including numeric 0/1 flags from sparse engine payloads. This keeps sparse retrieval evidence deterministic for basket promotion and later revise/apply consumers without widening retrieval strategy scope.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse retrieval `caches_used` snapshots normalize string-shaped booleans before downstream source/citation/basket bundle rehydration and fingerprinting. This keeps cache-use provenance deterministic for basket promotion and later revise/apply consumers without widening retrieval strategy scope.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` to resolve the integrator replay conflict for basket-promotion normalization. Sparse basket-promotion rehydration now preserves fail-closed behavior for missing `basket_item_id` values while still normalizing query constraints, citation status, cache-use snapshots, and diagnostics deterministically.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse basket-promotion bundle `active_strategy_ids` and `deferred_strategy_ids` use the canonical FTS-first MVP policy validators. Non-FTS active strategies now fail closed before basket-promotion rehydration can make deferred retrieval evidence look promotable.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse basket-promotion bundle items also run through the canonical FTS-only item validator. Non-FTS promotion item strategies now fail closed, while padded or mixed-case FTS labels canonicalize to `fts` before downstream payload rehydration.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so context-basket promotion items carry the canonical FTS-first retrieval policy, sparse basket-promotion bundle rehydration backfills item policy/backend/mode identity from the bundle policy, and bundle-level backend/mode drift fails closed before promotion evidence reaches engine consumers.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py` and `THREAD_PACKET.md` so raw excerpt-hit rehydration falls back from `source_strategy` to canonical `retrieval_source_strategy` when rebuilding basket-promotion bundles from sparse engine payloads. This keeps FTS-only promotion identity deterministic without widening retrieval strategy scope or touching the approved shared regression surface.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `THREAD_PACKET.md` so retrieval basket-promotion bundles carry the same canonical basket item snapshots, IDs, fingerprints, counts, and readiness fields exposed by the other retrieval bundles. Sparse basket-promotion bundle normalization now preserves or rehydrates those fields without changing the FTS-only strategy contract.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse basket-promotion item rehydration prefers explicit FTS `basket_item_id` values over stale generic `item_id` values, then rewrites both identity fields to the canonical basket item id before downstream source/context bundle promotion.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so direct retrieval result bundles and sparse excerpt-hit basket rehydration both expose canonical `retrieval:fts:<excerpt_id>` item identities for context-basket promotion while preserving the raw `excerpt_id` separately for audit.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so basket-promotion bundle `promotion_items` now carry the same canonical FTS basket item identity used by `basket_promotion_items`, including when sparse payloads rebuild the bundle from excerpt hits.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so basket-promotion item snapshots carry deterministic `query_constraints_fingerprint` values in both direct retrieval results and sparse excerpt-hit rehydration. This keeps context-basket promotion items auditable against the query constraints that produced them without widening retrieval strategy scope.

Packet-only commits after `5c87b08a9f7ca5a4dabc23fc1a80214276a882e9` refresh traceability and gate evidence only through `f9bdab5ded16e44476d773a24249c64442df2f3a`. The source-bearing passes after that packet-only refresh change `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `tests/unit/test_unified_retrieval.py`; reviewers should include those source-bearing commits, including this final basket-promotion query-constraint fingerprint pass, when re-reviewing the merge candidate.

Tracked packet note for this fixer pass: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are ignored local automation metadata in this branch worktree and are not tracked at `HEAD`. Treat this tracked `THREAD_PACKET.md` file as the authoritative corrected handoff packet for re-review.

Re-review should not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the implementation head. It is an intermediate implementation commit only.

## Files Changed

Source and shared regression implementation surface in the corrected source-bearing range:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Packet/artifact surface in the corrected source-bearing range:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

Packet-only refresh surface after the reviewed implementation head:

- `THREAD_PACKET.md`

Previous source-bearing fixer surface at `1439aa3eff4d420fb4fcad83c0556c2608813c77`:

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/payload.py`
- `tests/unit/test_unified_retrieval.py`

Current source-bearing basket-promotion query-constraint fingerprint finalization surface in this pass:

- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Scope Completed

SQLite FTS remains the required MVP retrieval path. PageIndex and embeddings remain deferred or compatibility-only fallback surfaces and are not reintroduced as required paths.

The branch makes FTS retrieval deterministic and auditable across query construction, cache keys, fresh-run cache snapshots, query snapshots, result payloads, excerpt lookup, citation/provenance bundles, sparse source/context bundle rehydration, date-range propagation, shortlist query fingerprints, matched-term provenance, result fingerprints, doc identity, doc rank, doc type, strategy aliases, query constraints, retrieval manifest fingerprints, and basket-promotion evidence. The final source-bearing passes additionally normalize rehydrated basket-promotion item date ranges and matched-term lists before item fingerprinting, add deterministic basket item IDs for direct context-basket promotion, keep those IDs FTS-only so compatibility/deferred retrieval shapes fail closed, and carry query-constraint fingerprints on basket-ready item snapshots.

The corrected branch-tip implementation also tightens the canonical engine and service query normalization paths so malformed, unordered, or scalar-shaped `date_range` inputs fail closed before FTS execution.

This finalization pass keeps direct service-layer `RetrievalConstraints(doc_types=...)` normalization aligned with the canonical facade path. Scalar text doc-type filters now normalize as a single doc type instead of being split into characters, so direct engine/service callers preserve deterministic FTS document filters before retrieval execution.

This finalization pass also canonicalizes stored document `doc_type` values before writing metadata and FTS rows. Canonical query filters now continue to match when callers ingest documents with whitespace or case variants, and provenance returns the canonical doc type that was actually filtered.

This finalization pass also backfills sparse retrieval provenance primary document and excerpt fields from citation snapshots when earlier sparse summary fields are empty. That preserves deterministic primary-source provenance for context-basket promotion and downstream revise/apply steps that rehydrate from source/context bundles.

This finalization pass also backfills sparse doc and excerpt bundle citation arrays from the canonical retrieval citation bundle when a downstream payload omits explicit bundle snapshots and provenance citation arrays. That keeps citation evidence available to context-basket promotion and revise/apply consumers that rehydrate from sparse engine payloads.

This finalization pass also validates sparse excerpt-citation basket item IDs during citation bundle normalization. FTS-shaped citation IDs remain rehydratable, while stale, mismatched, PageIndex-shaped, or embedding-shaped citation IDs are removed so deferred retrieval strategies cannot appear promotable through sparse source/context bundles.

This finalization pass also makes direct FTS excerpt lookup payloads promotion-ready by exposing the deterministic `retrieval:fts:<excerpt_id>` basket item ID at top level and in provenance. Padded excerpt IDs are canonicalized before lookup, and blank excerpt IDs fail closed before FTS execution.

This finalization pass also lower-cases the strategy segment when minting FTS basket item IDs from accepted mixed-case or padded FTS strategy values. That keeps service and sparse-payload rehydration paths on the same canonical `retrieval:fts:<excerpt_id>` identity without making PageIndex or embedding-shaped snapshots promotable.

This finalization pass also carries deterministic FTS-only basket item IDs through excerpt hit snapshots and excerpt citation snapshots. That gives basket promotion, citation evidence, and later revise/apply consumers the same auditable `retrieval:fts:<excerpt_id>` identity while preserving fail-closed behavior for deferred retrieval strategies.

This finalization pass also carries canonical `retrieval_source_strategy` through doc and excerpt citation snapshots and backfills it during sparse citation normalization. FTS excerpt evidence snapshots now retain the same deterministic `retrieval:fts:<excerpt_id>` basket identity across citation bundles, evidence snapshots, source bundles, and context-basket promotion paths.

This finalization pass also normalizes downstream `citation_status` snapshots across citation, doc, excerpt, source, context, diagnostics, provenance, and basket-promotion bundle rehydration. String-shaped booleans, numeric 0/1 flags, and string-shaped counts now canonicalize before promotion item fingerprints and source/context fingerprints are minted, keeping sparse engine payloads deterministic for basket promotion and later revise/apply steps.

This finalization pass also validates sparse basket-promotion strategy lists with the canonical MVP retrieval policy. A sparse downstream payload cannot carry `embeddings`, `pageindex`, or other non-FTS active strategies into promotion-ready evidence.

This finalization pass also carries the canonical retrieval policy on each basket-promotion item and validates sparse basket-promotion bundle backend/mode identity. Sparse promotion evidence now backfills item policy/backend/mode from the FTS-first bundle policy, while PageIndex-shaped bundle identity fails closed before context-basket promotion.

This finalization pass also makes the retrieval basket-promotion bundle self-contained for context-basket promotion by including canonical basket promotion item snapshots, basket item IDs, basket item fingerprints, promotion counts, and readiness flags directly in the bundle. Sparse bundle normalization now preserves or rehydrates those fields before downstream source/context payloads consume the evidence.

This finalization pass also aligns direct retrieval result basket-promotion snapshots and sparse excerpt-hit rehydration around the same canonical `retrieval:fts:<excerpt_id>` item identity. Raw excerpt IDs remain available as `excerpt_id`, while `item_id`, `basket_item_id`, and `basket_item_ids` now carry the context-basket-safe FTS identity across citation, source, context, evidence, and downstream payload surfaces.

This finalization pass also exposes the canonical `retrieve_auto` default retrieval entrypoint through the engine retrieval facade export list. The engine surface now exports both explicit `retrieve_fts` and default `retrieve_auto` entrypoints while both continue to resolve to the FTS-first retrieval path.

This finalization pass also carries deterministic `query_constraints_fingerprint` values on direct and sparse-rehydrated basket-promotion item snapshots. Context-basket promotion consumers can now audit each basket item against the exact normalized constraints that produced it, matching the bundle-level promotion-item fingerprint evidence.

Canonical demo path advanced: `vault/context material -> FTS retrieval -> retrieval evidence -> context basket promotion -> engine revise/apply`.

Before-handoff canonical demo-path statement: this work advances `retrieve relevant material` by keeping retrieval FTS-first, deterministic, and auditable; it also supports `promote or gather context into the basket` by preserving provenance and query evidence on promotion bundles/items.

## Tasks Completed

1. Canonical demo-path step advanced: `retrieve relevant material`. Made SQLite FTS the authoritative MVP retrieval path while keeping PageIndex and embeddings fallback-only/deferred.
2. Canonical demo-path step advanced: `retrieve relevant material`. Stabilized FTS query, cache, constraint, date-range, shortlist, doc-type, scope, and fresh-run behavior for deterministic retrieval.
3. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Normalized retrieval payloads, provenance, citation/source/context bundles, evidence snapshots, sparse bundle rehydration, retrieval manifest fingerprints, and basket-promotion evidence, including item-level date-range and matched-term normalization before basket-promotion fingerprinting, deterministic FTS-only `basket_item_id` values for promotion, and query-constraint fingerprints on basket-ready item snapshots. The engine facade now exports the default `retrieve_auto` entrypoint that reaches this FTS-first retrieval path.
4. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Added fail-closed and audit-focused regression coverage for malformed/reversed date ranges, empty inputs, unresolved scopes, FTS-only excerpt lookup and payload normalization, excerpt lookup fingerprints, cache/query snapshots, facade/export availability, basket-promotion fingerprint propagation, sparse basket item ID rehydration, basket item query-constraint fingerprints, and non-FTS basket item ID rejection.
Task accounting: this high-risk handoff is summarized as the 4 meaningful task groups above, matching the kickoff budget. The later source-bearing finalization commits are folded into those groups rather than counted as separate inflated tasks.

## Kickoff Budget/Limits Compliance

- Task budget: `4` high-risk task groups; this handoff folds the cumulative retrieval work into 4 meaningful and testable task groups.
- File count: the corrected source-bearing range before this pass changes `6` source/test files plus `3` packet/artifact files; this pass changes `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md`.
- Size accounting before this packet refresh: the corrected source-bearing range `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` already exceeds the high-risk `<=300 net LOC` limit; this pass adds a small retrieval service/payload/test/packet update for basket item query-constraint fingerprint propagation, keeping the range above the limit.
- Size limit status: exceeds the high-risk `<=8 files` and `<=300 net LOC` limits.
- Explicit exception status: no integrator-approved size or task-budget exception is recorded in this worktree. Because the full source-bearing range remains together, this is a known blocker for approval until the integrator grants an exception or requests a branch split.
- Shared-file exception status: `tests/unit/test_unified_retrieval.py` is the sole approved shared regression surface; no integrator-locked files changed.
- Routing/provider impact: none.

## Required Fixes Applied

1. Regenerated this review packet with the real source-bearing implementation head identified as the final branch tip reported in the fixer final response.
2. Removed the stale metadata-only framing for `beed411ecb15821f0cf145bd3ad68d59c996801c`; it is explicitly identified as source-bearing.
3. Updated the reviewed implementation range to include all intended source/test changes in the branch-tip source-bearing candidate.
4. Updated files changed, task accounting, command outcomes, risks, and roadmap/vision mapping to match the corrected range.
5. Documented that no explicit integrator-approved size exception is present for the high-risk size overage, so approval remains blocked unless the integrator grants an exception or requests a branch split/reduced handoff.
6. Stated the corrected canonical demo-path step explicitly: `retrieve relevant material`, with additional support for `promote or gather context into the basket`.
7. Reproduced the integrator replay blocker locally as a failing `./quality-test.sh` run in `test_basket_promotion_bundle_normalizes_query_constraints_snapshot`, then confirmed the resolved source/test state with focused retrieval regressions and the full required gate suite.
8. Added FTS-first basket-promotion strategy validation so sparse downstream payloads fail closed when a promotion bundle advertises non-FTS active strategies.
9. Added FTS-only basket-promotion item validation so sparse downstream payloads fail closed when individual promotion items advertise PageIndex/embedding strategies, while canonicalizing accepted padded or mixed-case FTS labels to `fts`.
10. Added basket-promotion policy propagation and sparse bundle backend/mode backfill/validation so context-basket promotion evidence carries the canonical FTS-first identity and rejects non-FTS bundle identity drift.
11. Added sparse excerpt-hit `retrieval_source_strategy` fallback during basket-promotion bundle rebuilds so FTS-only promotion evidence keeps canonical strategy identity when `source_strategy` is absent.
12. Added self-contained basket item snapshots, IDs, fingerprints, counts, and readiness fields to retrieval basket-promotion bundles and their sparse normalization path.
13. Added canonical sparse basket-promotion item identity normalization so an explicit FTS `basket_item_id` wins over stale generic `item_id` values before downstream source/context bundle promotion.
14. Aligned direct retrieval bundle basket IDs and sparse excerpt-hit basket rehydration on canonical `retrieval:fts:<excerpt_id>` item identity while preserving raw excerpt IDs separately for audit.
15. Added canonical FTS basket item identity fields to basket-promotion bundle `promotion_items` so direct and sparse promotion evidence can be promoted without depending on plain excerpt IDs.
16. Exported the canonical engine facade `retrieve_auto` default entrypoint through `src.qual.engine.retrieval.__all__`, with regression coverage keeping the facade export list aligned to the FTS-first engine surface.
17. Added deterministic `query_constraints_fingerprint` values to direct and sparse-rehydrated basket-promotion item snapshots so context-basket promotion evidence remains auditable against normalized query constraints.

## Commands Run

Required gates for this corrected merge candidate were re-run on 2026-05-12 against branch `codex/feat-retrieval-fts` after this source-bearing basket-promotion query-constraint fingerprint fix.

- `python -m pytest tests/unit/test_unified_retrieval.py -k basket_promotion -q` - passed 3 focused basket-promotion regressions after adding basket item `query_constraints_fingerprint` propagation.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `./quality-test.sh` - passed smoke tests and 475 unit tests, including all 92 unified retrieval tests.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when tests attempted to write `.codex/packet_router/logs`, `.codex/feature_runner/state.json`, `.codex/packet_planner/state.json`, move recovery artifacts under `.codex/worktree_recovery`, or invoke `ps`.
- `python -m pytest tests/unit/test_unified_retrieval.py -q` - passed 92 unified retrieval tests and 8 subtests after the packet refresh.

Earlier gate history for this corrected merge candidate:

- `pytest tests/unit/test_unified_retrieval.py -q` - blocked during collection because the shell environment did not include the repository on `PYTHONPATH` (`ModuleNotFoundError: No module named 'src'`).
- `PYTHONPATH=. pytest tests/unit/test_unified_retrieval.py -q` - passed 92 unified retrieval tests and 8 subtests after exporting `retrieve_auto` through the engine facade `__all__`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 475 unit tests, including all 92 unified retrieval tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when tests attempted to write `.codex/packet_router/logs`, `.codex/feature_runner/state.json`, `.codex/packet_planner/state.json`, move recovery artifacts under `.codex/worktree_recovery`, or invoke `ps`.

- `python -m pytest tests/unit/test_unified_retrieval.py -k 'basket_promotion_items_backfill_query_context_from_bundle or basket_promotion_bundle_normalizes_query_constraints_snapshot or retrieval_downstream_payload_helper_normalizes_citation_status_and_cache_snapshots'` - passed 2 focused basket-promotion identity regressions.
- `python -m pytest tests/unit/test_unified_retrieval.py` - passed 92 unified retrieval tests.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 475 unit tests, including all 92 unified retrieval tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when tests attempted to write `.codex/packet_router/logs`, `.codex/feature_runner/state.json`, `.codex/packet_planner/state.json`, move recovery artifacts under `.codex/worktree_recovery`, or invoke `ps`.

- `python3 -m unittest tests.unit.test_unified_retrieval -k basket_item -q` - passed 3 focused basket item identity regressions after canonicalizing direct and sparse FTS basket IDs.
- `python3 -m unittest tests.unit.test_unified_retrieval -k basket_promotion -q` - passed 3 focused basket-promotion regressions.
- `python3 -m unittest tests.unit.test_unified_retrieval -q` - passed 92 unified retrieval tests after canonical basket ID alignment.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 475 unit tests, including the unified retrieval regression surface.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when tests attempted to write `.codex/packet_router/logs`, `.codex/feature_runner/state.json`, `.codex/packet_planner/state.json`, move recovery artifacts under `.codex/worktree_recovery`, or invoke `ps`.
- `SCOPE_ALLOW_SHARED=1 ./scripts/scope-check.sh && ./scripts/format-check.sh && ./scripts/lint.sh && ./scripts/build.sh && ./typecheck-test.sh && ./scripts/test.sh` - passed scope-check, format, lint, compile/typecheck, smoke tests, and retrieval tests, then failed with the same 6 unrelated sandbox/control-plane `PermissionError` errors during control-plane tests.
- `python -m pytest tests/unit/test_unified_retrieval.py -k "prefers_explicit_basket_item_id or deduplicates_sparse_basket_items"` - passed 2 focused sparse basket-promotion identity regressions.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 475 unit tests, including the unified retrieval regression surface.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and 475 unit tests.
- `python -m pytest tests/unit/test_unified_retrieval.py -k "basket_promotion_bundle or basket_promotion_items"` - passed 3 focused basket-promotion regressions after the bundle self-containment fix.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 474 unit tests, including the unified retrieval regression surface.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and 474 unit tests.

- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_basket_promotion_bundle_backfills_item_policy_and_rejects_non_fts_identity tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_basket_promotion_bundle_normalizes_query_constraints_snapshot tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_basket_promotion_items_backfill_query_context_from_bundle -q` - passed 3 focused retrieval regressions for basket-promotion item policy/backend/mode backfill, bundle identity validation, and neighboring promotion normalization.

- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_downstream_payload_helper_rejects_non_fts_promotion_items tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_downstream_payload_helper_canonicalizes_fts_promotion_items -q` - passed 2 focused retrieval regression tests for item-level basket-promotion strategy validation.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - initially failed after broad item normalization added basket identity fields to sparse bundle snapshots; fixed by narrowing item-level normalization to strategy-label validation/canonicalization only.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_downstream_payload_helper_rejects_non_fts_promotion_items tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_downstream_payload_helper_canonicalizes_fts_promotion_items tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_basket_promotion_bundle_normalizes_query_constraints_snapshot tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_downstream_payload_helper_normalizes_numeric_citation_status -q` - passed 4 focused retrieval regressions after the narrow fix.
- `./quality-test.sh` - passed smoke tests and 474 unit tests, including the unified retrieval regression surface.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and retrieval tests, then failed with 6 unrelated control-plane `PermissionError` errors when tests attempted to write `.codex/packet_router/logs`, `.codex/feature_runner/state.json`, `.codex/packet_planner/state.json`, move recovery artifacts under `.codex/worktree_recovery`, or invoke `ps`.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_downstream_payload_helper_rejects_non_fts_promotion_strategies tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_downstream_payload_helper_normalizes_numeric_citation_status -q` - passed 2 focused retrieval regression tests.

Additional focused retrieval checks run earlier in this lane:

- `python3 -m compileall -q src/qual/retrieval/service.py src/qual/engine/retrieval/payload.py tests/unit/test_unified_retrieval.py` - passed after citation provenance strategy normalization.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_engine_retrieval_tool_returns_canonical_downstream_payload -q` - passed after adding canonical `retrieval_source_strategy` to citation snapshots.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_sparse_payload_doc_and_excerpt_bundles_use_citation_fallbacks -q` - passed after sparse citation normalization started backfilling `retrieval_source_strategy`.
- `python3 -m unittest tests.unit.test_unified_retrieval -q` - passed 68 unified retrieval tests after evidence snapshots were aligned with normalized citation snapshots.
- `python3 -m compileall -q src/qual/retrieval/service.py src/qual/engine/retrieval/payload.py tests/unit/test_unified_retrieval.py` - passed after propagating FTS basket item IDs into excerpt hit and citation snapshots.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_engine_retrieval_tool_returns_canonical_downstream_payload -q` - passed after aligning excerpt citation expectations with top-level excerpt hit basket item IDs.
- `python3 -m unittest tests.unit.test_unified_retrieval -q` - passed 68 unified retrieval tests after propagating FTS basket item IDs into excerpt hit and citation snapshots.
- `python3 - <<'PY' ... _basket_item_id_for_excerpt(...) ... PY` - passed after canonicalizing accepted mixed-case FTS strategy labels to lower-case `retrieval:fts:<excerpt_id>` basket item IDs while keeping deferred strategies fail-closed.
- `python3 -m compileall -q src/qual/retrieval/service.py src/qual/engine/retrieval/payload.py` - passed after the FTS strategy-label basket ID canonicalization fix.
- `python3 -m unittest tests.unit.test_unified_retrieval -q` - passed 68 unified retrieval tests after the FTS strategy-label basket ID canonicalization fix.
- `python -m unittest tests.unit.test_unified_retrieval -v` - passed 68 unified retrieval tests after making direct FTS excerpt lookup payloads expose FTS-only basket item IDs and canonicalize padded excerpt IDs.
- `python3 -m unittest tests.unit.test_unified_retrieval -q` - passed 67 unified retrieval tests after the sparse citation basket ID validation fix.
- `python3 - <<'PY' ... build_retrieval_citation_bundle_from_result(...) ... PY` - passed; FTS-shaped citation `basket_item_id` values are preserved while PageIndex-shaped and mismatched IDs are removed.
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

- The corrected cumulative source-bearing range exceeds the high-risk task, size, and file limits. No explicit integrator-approved exception is present in the worktree, so this remains a required integration decision: grant an exception or request a branch split/reduced handoff.
- Required retrieval and local format/lint/typecheck/test gates are green for this pass. `make ci` is blocked after two attempts by unrelated sandbox/control-plane `PermissionError` failures after scope, format, lint, compile/typecheck, smoke, and retrieval tests pass; details are recorded above.
- All source-bearing work is now included in the reviewed implementation range; there is no longer a metadata-only branch-tip claim hiding source/test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 Real workflow loop, especially `feat-retrieval-fts` retrieval/search and the exit criterion that retrieval returns structured results suitable for basket promotion.
- Product Vision capabilities affected: `2. Retrieval-first context handling` and `3. Canonical engine contract`.
- Architecture alignment: retrieval stays in `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`; no provider/routing/core app entrypoints are touched.
- Routing/provider impact: none.
- Proposed `README.md` patch text: none.
