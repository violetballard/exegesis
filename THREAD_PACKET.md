## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Handoff type: high-risk retrieval handoff for the FTS-first retrieval lane.
- Canonical demo-path step advanced before handoff: `retrieve relevant material`; deterministic payload/provenance output also strengthens `promote or gather context into the basket`.
- Risk reason: approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Lane-owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Approved shared regression path: `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files changed: none.
- Authoritative reviewed implementation base: `378cf9a74a3658058079a32f186fcd254c4a4034`.
- Reviewed source-bearing implementation head: this source-bearing fixer commit; final branch tip SHA is reported in the fixer final response.
- Reviewed source-bearing implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` on branch `codex/feat-retrieval-fts`.
- Packet update note: this commit updates retrieval payload source, the approved shared regression surface, and `THREAD_PACKET.md`; the final branch tip SHA is reported in the fixer final response.
- Current pass role: source-bearing caches-used normalization for the reviewed source-bearing range.

## Traceability Correction

This packet supersedes earlier handoffs that described `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the final reviewed implementation head or described later source/test-changing commits as metadata-only.

The actual source-bearing merge candidate for this branch is:

`378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` on branch `codex/feat-retrieval-fts`

That range includes every intended retrieval source/test change through this final source-bearing fixer commit, including the reviewer-cited post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` changes in `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`, and `tests/unit/test_unified_retrieval.py`.

`beed411ecb15821f0cf145bd3ad68d59c996801c` is source-bearing. It modifies `src/qual/engine/retrieval/__init__.py`, `src/qual/retrieval/service.py`, and `THREAD_PACKET.md`. It must not be treated as metadata-only.

`51ee03de162297cce0dfafb2435fb33a7189807d` is also source-bearing. It modifies `src/qual/engine/retrieval/payload.py` so basket-promotion item rehydration normalizes item-level `query_date_range` and `matched_terms` values before promotion-item fingerprinting.

`60ec82aad820530cd1011b36a92404dfc07e37d7` is also source-bearing. It modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `tests/unit/test_unified_retrieval.py` so FTS basket-promotion items expose and rehydrate deterministic `basket_item_id` values of the form `retrieval:fts:<excerpt_id>`.

`5c87b08a9f7ca5a4dabc23fc1a80214276a882e9` is also source-bearing. It modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `tests/unit/test_unified_retrieval.py` so basket-promotion item ID generation remains FTS-only; PageIndex/embedding-shaped sparse promotion snapshots fail closed instead of receiving promotable `retrieval:<strategy>:<excerpt_id>` IDs.

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

Packet-only commits after `5c87b08a9f7ca5a4dabc23fc1a80214276a882e9` refresh traceability and gate evidence only through `f9bdab5ded16e44476d773a24249c64442df2f3a`. The source-bearing passes after that packet-only refresh change `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `tests/unit/test_unified_retrieval.py`; reviewers should include those source-bearing commits, including this final caches-used normalization pass, when re-reviewing the merge candidate.

Tracked packet note for this fixer pass: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are ignored local automation metadata in this branch worktree and are not tracked at `HEAD`. Treat this tracked `THREAD_PACKET.md` file as the authoritative corrected handoff packet for re-review.

Re-review should not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the implementation head. It is an intermediate implementation commit only.

## Files Changed

Source and shared regression implementation surface in the corrected source-bearing range:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
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

Final source-bearing citation-status normalization surface in this pass:

- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/payload.py`
- `tests/unit/test_unified_retrieval.py`

## Scope Completed

SQLite FTS remains the required MVP retrieval path. PageIndex and embeddings remain deferred or compatibility-only fallback surfaces and are not reintroduced as required paths.

The branch makes FTS retrieval deterministic and auditable across query construction, cache keys, fresh-run cache snapshots, query snapshots, result payloads, excerpt lookup, citation/provenance bundles, sparse source/context bundle rehydration, date-range propagation, shortlist query fingerprints, matched-term provenance, result fingerprints, doc identity, doc rank, doc type, strategy aliases, query constraints, retrieval manifest fingerprints, and basket-promotion evidence. The final source-bearing passes additionally normalize rehydrated basket-promotion item date ranges and matched-term lists before item fingerprinting, add deterministic basket item IDs for direct context-basket promotion, and keep those IDs FTS-only so compatibility/deferred retrieval shapes fail closed.

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

Canonical demo path advanced: `vault/context material -> FTS retrieval -> retrieval evidence -> context basket promotion -> engine revise/apply`.

Before-handoff canonical demo-path statement: this work advances `retrieve relevant material` by keeping retrieval FTS-first, deterministic, and auditable; it also supports `promote or gather context into the basket` by preserving provenance and query evidence on promotion bundles/items.

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
10. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Validated sparse excerpt-citation `basket_item_id` values as FTS-only during citation bundle normalization so stale or deferred-strategy IDs fail closed before rehydration.
11. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Made direct FTS excerpt lookup payloads expose deterministic FTS-only basket item IDs, canonicalize padded excerpt IDs, and fail blank IDs closed before lookup.
12. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Canonicalized accepted FTS strategy labels before minting basket item IDs so service and sparse payload helpers always emit lower-case `retrieval:fts:<excerpt_id>` identities while deferred strategies fail closed.
13. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Propagated deterministic FTS-only basket item IDs into excerpt hit and citation snapshots so citation-backed context can be promoted and audited with the same item identity as promotion bundles.
14. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Propagated canonical `retrieval_source_strategy` and FTS basket item identity through doc/excerpt citation and evidence snapshots, and backfilled sparse citation snapshots so source/context bundle rehydration preserves the canonical FTS strategy key.
15. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Normalized sparse `citation_status` snapshots before downstream source/context/diagnostics/provenance/basket rehydration and fingerprinting so string-shaped status values cannot destabilize promotion evidence.
16. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Canonicalized numeric sparse `citation_status` flags before downstream payload and basket-promotion rehydration so integer 0/1 flags cannot destabilize promotion evidence fingerprints.
17. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Canonicalized sparse `caches_used` boolean maps before downstream source/citation/basket bundle rehydration so string-shaped cache flags cannot destabilize retrieval evidence fingerprints.
18. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Resolved the integrator replay conflict by keeping sparse basket-promotion item identity fail-closed when `basket_item_id` is absent, while preserving deterministic query constraint and diagnostics normalization.

Task accounting: `18` high-risk task groups are present in the cumulative branch after this source-bearing finalization pass, exceeding the high-risk task cap and requiring the same integration decision already noted for the size overage.

## Kickoff Budget/Limits Compliance

- Task budget: `4` high-risk task groups; this cumulative branch now has `18` source-bearing task groups after the integrator replay conflict fix.
- File count: the corrected source-bearing range before this pass changes `6` source/test files plus `3` packet/artifact files; this pass changes `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md`.
- Size accounting before this packet refresh: the corrected source-bearing range `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` already exceeds the high-risk `<=300 net LOC` limit; this pass adds a small retrieval payload/test/packet update for caches-used normalization, keeping the range above the limit.
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

## Commands Run

Required gates for this corrected merge candidate were re-run on 2026-05-12 against branch `codex/feat-retrieval-fts` after this source-bearing integrator replay conflict fix.

- `make scope-check` - passed for branch `codex/feat-retrieval-fts` after reporting no branch policy to enforce.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - initially reproduced the integration blocker with a basket-promotion normalization failure, then passed smoke tests and 138 unit tests after the focused fix pass.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - passed setup, scope-check, format, lint, compile/typecheck, smoke tests, and 138 unit tests.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_basket_promotion_bundle_normalizes_query_constraints_snapshot tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_downstream_payload_helper_normalizes_numeric_citation_status -q` - passed 2 focused retrieval regression tests.
- `python3 -m compileall -q src/qual/engine/retrieval/payload.py tests/unit/test_unified_retrieval.py` - passed after caches-used normalization.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_downstream_payload_helper_normalizes_numeric_citation_status -q` - passed after extending the focused sparse payload normalization regression to cover string-shaped `caches_used` values.
- `python3 -m unittest tests.unit.test_unified_retrieval -q` - passed 69 unified retrieval tests.

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
- All source-bearing work is now included in the reviewed implementation range; there is no longer a metadata-only branch-tip claim hiding source/test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 Product Readiness generation provenance and Milestone 4 Retrieval Layer FTS-first retrieval orchestration/source attribution.
- Product Vision capabilities affected: `2. Retrieval-first context handling` and `3. Auditable generation`.
- Architecture alignment: retrieval stays in `src/qual/retrieval/**` and `src/qual/engine/retrieval/**`; no provider/routing/core app entrypoints are touched.
- Routing/provider impact: none.
- Proposed `README.md` patch text: none.
