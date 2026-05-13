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
- Packet update note: this commit adds stable promotion item fingerprints to standalone FTS excerpt lookup payloads, provenance, basket-promotion item snapshots, and audit metadata, then refreshes `THREAD_PACKET.md`; the final branch tip SHA is reported in the fixer final response.
- Current pass role: source-bearing FTS excerpt lookup promotion-item fingerprint finalization for context-basket evidence.

## Traceability Correction

This packet supersedes earlier handoffs that described `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the final reviewed implementation head or described later source/test-changing commits as metadata-only.

The actual source-bearing merge candidate for this branch is:

`378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` on branch `codex/feat-retrieval-fts`

That range includes every intended retrieval source/test change through this final source-bearing fixer commit, including the reviewer-cited post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` changes in `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`, `engine/src/exegesis_engine/retrieval/search_service.py`, and `tests/unit/test_unified_retrieval.py`.

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

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse basket-promotion items rebuilt from excerpt hits preserve canonical `matched_terms` and `match_count` evidence. This keeps compact basket-promotion bundles auditable against the FTS match evidence that produced the excerpt without enabling deferred retrieval strategies.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and `THREAD_PACKET.md` so retrieval basket-promotion bundles carry the same canonical basket item snapshots, IDs, fingerprints, counts, and readiness fields exposed by the other retrieval bundles. Sparse basket-promotion bundle normalization now preserves or rehydrates those fields without changing the FTS-only strategy contract.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse basket-promotion item rehydration prefers explicit FTS `basket_item_id` values over stale generic `item_id` values, then rewrites both identity fields to the canonical basket item id before downstream source/context bundle promotion.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so direct retrieval result bundles and sparse excerpt-hit basket rehydration both expose canonical `retrieval:fts:<excerpt_id>` item identities for context-basket promotion while preserving the raw `excerpt_id` separately for audit.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so basket-promotion bundle `promotion_items` now carry the same canonical FTS basket item identity used by `basket_promotion_items`, including when sparse payloads rebuild the bundle from excerpt hits.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so basket-promotion item snapshots carry deterministic `query_constraints_fingerprint` values in both direct retrieval results and sparse excerpt-hit rehydration. This keeps context-basket promotion items auditable against the query constraints that produced them without widening retrieval strategy scope.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse basket-promotion bundle snapshots recompute stale bundle-level `query_constraints_fingerprint` values from normalized query constraints. This keeps bundle-level promotion evidence auditable against the same canonical constraints as its promotion items.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py` and `THREAD_PACKET.md` so sparse basket-promotion bundle snapshots that retain canonical `promotion_items` but omit `basket_promotion_items` still rehydrate context-basket-ready FTS promotion refs from those promotion items. This keeps self-contained promotion bundles promotable without falling through to empty evidence or alternate retrieval strategies.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so direct and sparse-rehydrated basket-promotion bundle `promotion_items` carry the canonical basket item fingerprint from the matching context-basket item. This lets engine consumers audit the exact FTS basket identity promoted from either bundle surface without deriving identity from plain excerpt IDs.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so basket-promotion bundle `promotion_items` carry the same deterministic `excerpt_lookup_fingerprint` already exposed by canonical basket promotion item snapshots. Sparse excerpt-hit rehydration now preserves that lookup identity when rebuilding promotion items, and sparse bundle normalization backfills older promotion items from matching basket item snapshots by `item_id` or canonical FTS `basket_item_id` before downstream context-basket consumers see the bundle.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py` and `THREAD_PACKET.md` so the retrieval manifest records canonical FTS basket item IDs and the result fingerprint binds those IDs alongside excerpt lookup identity. Context-basket promotion consumers can now audit the promoted `retrieval:fts:<excerpt_id>` item identities back to the exact FTS result fingerprint without introducing PageIndex, embeddings, or multi-strategy retrieval as required paths.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so doc-hit payloads, doc citation snapshots, retrieval summaries, retrieval provenance, and the retrieval manifest expose `top_basket_item_id` values derived from the canonical FTS top excerpt. Context-basket promotion consumers can now move from a doc-level result or sparse source/context bundle to the exact promotable `retrieval:fts:<excerpt_id>` item without reconstructing identity from raw excerpt IDs.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse basket-promotion snapshots that omit both `item_id` and `basket_item_id` rehydrate the canonical FTS basket item identity from `source_strategy` plus `excerpt_id` before promotion fingerprints are rebuilt. Compatibility snapshots that intentionally retain only `item_id` still keep the missing `basket_item_id` missing.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so direct FTS excerpt lookup provenance carries the same deterministic `basket_item_ids` and `basket_item_fingerprints` lists already exposed on the lookup payload and audit event. Context-basket promotion consumers can now audit the complete basket-ready identity set from the canonical provenance snapshot without reconstructing it from top-level fields.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so downstream payload and excerpt-bundle `excerpt_hits` carry the deterministic FTS `basket_item_fingerprint` from the matching canonical basket-promotion item. Context-basket promotion consumers can now audit raw excerpt-hit snapshots directly against promotable basket evidence without reconstructing the fingerprint from plain excerpt IDs.

This source-bearing fixer pass modifies `engine/src/exegesis_engine/retrieval/__init__.py`, `src/qual/engine/retrieval/__init__.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so the canonical engine retrieval package exports the same FTS-first facade entrypoints and policy helpers already exposed through `src.qual.engine.retrieval`. Engine-package consumers can now reach `build_retrieval_query`, `retrieve_fts`, `retrieve_auto`, direct FTS citation bundles, and the bundle/payload helpers from the canonical package without falling back to PageIndex, embeddings, or alternate strategy imports. The canonical package now binds each source facade export from `src.qual.engine.retrieval.__all__` and inserts only the legacy service dataclass exports after the explicit `DEFERRED_STRATEGY_IDS` anchor, so future FTS-first facade additions do not silently drift between packages and export ordering no longer depends on a positional slice.

This source-bearing fixer pass also modifies `src/qual/engine/retrieval/__init__.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so canonical retrieval query construction uses one strict boolean constraint normalizer. Text-shaped booleans such as `"yes"` and `"off"` remain accepted by both facades, while non-canonical integer values such as `2` fail closed before a query fingerprint can be derived.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse source/context bundle rehydration can recover canonical FTS basket item IDs, counts, and fingerprints from `retrieval_manifest` when top-level and summary basket fields have been stripped. This keeps compact engine snapshots basket-promotion-ready without reintroducing PageIndex, embeddings, or alternate retrieval strategies.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse source/context bundle basket item ID snapshots are accepted only when they are canonical FTS IDs of the form `retrieval:fts:<excerpt_id>`. Stale PageIndex, embedding-shaped, or raw excerpt IDs now fail closed instead of keeping sparse promotion evidence ready through summary or manifest fallback fields.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse source/context bundle basket item fingerprint snapshots are trusted only from the same fallback surfaces that retain canonical FTS basket item IDs. Stale fingerprint-only PageIndex, embedding-shaped, or raw excerpt snapshots now fail closed with the invalid IDs instead of leaking provenance into basket-promotion evidence.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse retrieval manifest and summary `top_basket_item_ids`, summary and manifest `basket_item_ids`, document-citation `top_basket_item_id` fallbacks, and fingerprint-only stale snapshots normalize through the canonical FTS-only basket ID validator. Stale PageIndex, embedding-shaped, raw excerpt, or padded non-canonical IDs now fail closed before source/context/provenance rehydration can treat them as promotable basket identity or preserve a stale promotion-ready count.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse `primary_basket_item_id` summary/provenance fields use the same canonical FTS-only validation as list-shaped basket IDs. Stale PageIndex or embedding-shaped primary IDs now fail closed, while sparse excerpt citation fallback can rehydrate the first canonical `retrieval:fts:<excerpt_id>` primary ID for basket-promotion evidence.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse source/context bundle basket item fingerprint snapshots are trusted only when their normalized fingerprint set pairs one-for-one with the surviving canonical FTS basket item IDs. Unpaired fingerprint-only evidence now fails closed while canonical basket item IDs can still preserve basket-promotion readiness for downstream engine consumers.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse basket item fingerprint fallback handles both explicit positional ID/fingerprint pairs and compact fingerprint lists aligned to the surviving canonical FTS basket IDs. Mixed stale PageIndex refs no longer attach their fingerprints to FTS basket IDs, while compact valid FTS fallback snapshots keep their auditable fingerprint.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse source/context bundle basket item ID fallback canonicalizes case-varied `Retrieval:FTS:<excerpt_id>` refs to `retrieval:fts:<excerpt_id>` before pairing fingerprints. PageIndex, embedding-shaped, and raw excerpt refs still fail closed, but compact snapshots with FTS-only case drift can remain auditable for context-basket promotion.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so retrieval summaries and manifests carry and rehydrate the canonical demo-path markers for `retrieve_relevant_material` and `promote_context_to_basket`. This keeps compact summary-backed or manifest-backed engine snapshots self-describing for basket promotion and later revise/apply consumers without widening retrieval strategy scope.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so direct and sparse-rehydrated FTS retrieval payloads, source/context bundles, basket-promotion bundles, and promotion items carry explicit `canonical_demo_path_steps` markers for `retrieve_relevant_material` and `promote_context_to_basket`, with shared regression coverage locking the markers onto the engine-facing payload surfaces. This makes the Milestone 3 retrieval output self-describing for basket promotion and later revise/apply consumers without reintroducing PageIndex, embeddings, or multi-strategy retrieval as required paths.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse source-bundle context rehydration backfills `canonical_demo_path_steps` when compact source snapshots strip that marker from the top level and nested retrieval bundles. This keeps source-bundle-only engine context reconstruction aligned with the canonical demo path and basket-promotion evidence without deriving workflow role from raw excerpt IDs or widening beyond FTS-first retrieval.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse source/context/basket-promotion rehydration rewrites stale `canonical_demo_path_steps` values to the canonical FTS MVP markers. Compact or older engine snapshots can no longer preserve misleading workflow-role markers on retrieval evidence, source bundles, downstream payloads, basket-promotion bundles, or promotion items before context-basket promotion.

This source-bearing fixer pass modifies `engine/src/exegesis_engine/retrieval/search_service.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so direct imports from `exegesis_engine.retrieval.search_service` expose the same FTS-first facade as `exegesis_engine.retrieval`. The canonical compat shim now preserves direct access to `build_retrieval_query`, explicit FTS entrypoints, default `retrieve_auto` helpers, and payload bundle builders while still excluding PageIndex and embeddings strategy classes.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so compact basket item fingerprint fallback is accepted only when all candidate basket IDs are already canonical FTS IDs. Sparse snapshots with mixed stale PageIndex/embedding IDs can still preserve the surviving `retrieval:fts:<excerpt_id>` basket ID, but their compact fingerprint evidence now fails closed instead of becoming positionally ambiguous promotion provenance.

This source-bearing fixer pass modifies `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so sparse basket-promotion items must expose canonical `retrieval:fts:<excerpt_id>` item identity before surviving source/context bundle rehydration. Raw excerpt-only sparse items now fail closed with their orphaned fingerprints instead of becoming unaudited context-basket evidence.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so standalone FTS excerpt lookup payloads, provenance snapshots, basket-promotion items, and audit metadata carry the canonical demo-path markers for `retrieve_relevant_material` and `promote_context_to_basket`. Direct lookup provenance and audit metadata now also include canonical basket-promotion item snapshots with their own readiness/count fields and singleton basket item ID/fingerprint lists, so fetched excerpts remain self-describing basket-ready evidence even when consumers inspect nested provenance or the audit trail rather than the returned payload.

This source-bearing fixer pass modifies `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md` so standalone FTS excerpt lookup payloads, provenance snapshots, basket-promotion items, and audit metadata carry a stable `promotion_item_fingerprint` alongside the existing canonical basket item ID/fingerprint evidence. Direct lookup evidence now has the same item-level promotion fingerprint expected by context-basket consumers without adding PageIndex, embeddings, or multi-strategy behavior.

Packet-only commits after `5c87b08a9f7ca5a4dabc23fc1a80214276a882e9` refresh traceability and gate evidence only through `f9bdab5ded16e44476d773a24249c64442df2f3a`. The source-bearing passes after that packet-only refresh change `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/engine/retrieval/__init__.py`, `engine/src/exegesis_engine/retrieval/__init__.py`, `engine/src/exegesis_engine/retrieval/search_service.py`, and `tests/unit/test_unified_retrieval.py`; reviewers should include those source-bearing commits, including this final FTS excerpt lookup provenance/audit basket-item pass, when re-reviewing the merge candidate.

Tracked packet note for this fixer pass: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are ignored local automation metadata in this branch worktree and are not tracked at `HEAD`. Treat this tracked `THREAD_PACKET.md` file as the authoritative corrected handoff packet for re-review.

Re-review should not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the implementation head. It is an intermediate implementation commit only.

## Files Changed

Source and shared regression implementation surface in the corrected source-bearing range:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `tests/unit/test_unified_retrieval.py`
- `engine/src/exegesis_engine/retrieval/__init__.py`
- `engine/src/exegesis_engine/retrieval/search_service.py`

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

Current source-bearing FTS excerpt lookup provenance/audit basket-item finalization surface in this pass:

- `THREAD_PACKET.md`
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

This finalization pass also recomputes stale basket-promotion bundle-level `query_constraints_fingerprint` values from normalized query constraints during sparse bundle rehydration. Context-basket promotion consumers now receive bundle and item fingerprints derived from the same canonical constraint shape even when upstream sparse payloads carry stale fingerprint text.

This finalization pass also rehydrates `basket_promotion_items` directly from normalized `promotion_items` when a sparse basket-promotion bundle has lost the duplicate basket item list. Context-basket promotion consumers now keep canonical FTS basket refs from self-contained promotion bundles instead of seeing an empty promotion set.

This finalization pass also carries deterministic `excerpt_lookup_fingerprint` values on direct and sparse-rehydrated basket-promotion `promotion_items`, and backfills that field from matching canonical basket item snapshots by `item_id` or `basket_item_id` when normalizing older sparse bundle payloads. Context-basket promotion consumers can now audit promotion evidence back to the canonical FTS excerpt lookup identity without depending on the duplicate `basket_promotion_items` list.

This finalization pass also records canonical FTS basket item IDs in the retrieval manifest and includes those IDs in the result fingerprint. The result identity now binds both excerpt lookup fingerprints and the `retrieval:fts:<excerpt_id>` basket-promotion identities that downstream basket/context flows consume.

This finalization pass also carries the top excerpt's canonical FTS basket item ID through doc hits, doc citations, retrieval summaries, retrieval provenance, and the manifest. Sparse source/context bundle normalization now backfills `top_basket_item_ids` and `primary_basket_item_id` from surviving doc/excerpt snapshots, and provenance snapshots retain the full doc-level `top_basket_item_ids` list for manifest/audit comparison. The result fingerprint now binds those doc-level `top_basket_item_ids`, so document-level retrieval consumers can promote or inspect the exact basket-ready FTS item without deriving unaudited identity from `top_excerpt_id`.

This finalization pass also rehydrates canonical FTS basket item identity for sparse basket-promotion snapshots that have lost both `item_id` and `basket_item_id`. The normalizer derives `retrieval:fts:<excerpt_id>` from FTS strategy provenance before recomputing promotion item fingerprints, while preserving older sparse compatibility behavior when a snapshot intentionally keeps only `item_id`.

This finalization pass also stores the canonical basket-promotion identity lists in direct FTS excerpt lookup provenance. The lookup payload, provenance snapshot, and audit event now agree on `basket_item_ids` and `basket_item_fingerprints`, so basket/context consumers can prove which FTS item identities are promotable from any of those surfaces.

This finalization pass also mirrors the canonical basket item fingerprint onto basket-promotion bundle `promotion_items`, including sparse bundle rehydration from surviving basket item snapshots. That keeps direct promotion evidence and canonical basket refs aligned on the same auditable FTS item fingerprint.

This finalization pass also lets sparse source/context bundle rehydration fall back to `retrieval_manifest` for canonical FTS basket item IDs, counts, and fingerprints when compact snapshots have lost top-level and summary basket fields. Context-basket promotion consumers can still recover manifest-backed FTS basket identity without treating PageIndex or embeddings as promotable paths.

This finalization pass also validates basket item ID snapshots used by sparse source/context fallback. Only canonical `retrieval:fts:<excerpt_id>` IDs can preserve basket-promotion readiness; PageIndex-shaped, embedding-shaped, or raw excerpt IDs now fail closed before context-basket consumers receive promoted refs.

This finalization pass also pairs sparse basket item fingerprint fallback with canonical FTS basket item ID fallback. Fingerprint-only stale snapshots from PageIndex, embeddings, or raw excerpt refs now clear alongside invalid basket IDs so context-basket consumers cannot receive unaudited promotion provenance, while case-varied FTS basket refs canonicalize before pairing.

This finalization pass also canonicalizes sparse basket-promotion item identity before downstream bundle rehydration. Explicit canonical `retrieval:fts:<excerpt_id>` values now win over stale `item_id` values, derived FTS identities are restored when both item identity fields are missing, and explicit deferred-strategy retrieval identities fail closed case-insensitively when no canonical FTS basket identity or excerpt can recover them.

This finalization pass also adds a stable `fts_match_query_fingerprint` to FTS retrieval diagnostics, excerpt/doc hit snapshots, hit/doc provenance, retrieval manifests, retrieval summaries, citation/evidence snapshots, basket-promotion items, audit metadata, and source/context bundle rehydration. The fingerprint is derived from the canonical SQLite FTS match expression and normalized query terms, but only the hash is exposed, so downstream basket/context consumers can audit which FTS query shape produced the evidence without storing plaintext query terms. The manifest copy and result fingerprint payload bind the retrieval result fingerprint to the canonical FTS match-query shape.

This finalization pass also carries canonical demo-path markers directly on retrieval summaries and manifests, and rehydrates those markers during sparse summary/manifest normalization. Compact engine snapshots that retain only the summary or manifest now remain self-describing for `retrieve_relevant_material` and `promote_context_to_basket` without inferring workflow role from raw excerpt or basket IDs.

This finalization pass also exposes the canonical FTS-first facade through direct `exegesis_engine.retrieval.search_service` compat imports. Direct compat consumers now see the same `build_retrieval_query`, `retrieve_fts`, `retrieve_auto`, payload, provenance, source/context, and basket-promotion helpers as `exegesis_engine.retrieval`, while PageIndex and embeddings strategy classes remain absent from the export surface.

This finalization pass also prevents raw excerpt-only sparse basket-promotion items from surviving source/context bundle rehydration. Context-basket consumers now require canonical FTS basket item identity before accepting sparse promotion evidence, so compact snapshots cannot promote unaudited raw excerpt IDs or orphaned fingerprints.

This finalization pass also records canonical basket item fingerprints on the retrieval manifest and the nested manifest copy inside retrieval evidence. Context-basket consumers that retain manifest-backed retrieval evidence can now audit both the canonical `retrieval:fts:<excerpt_id>` IDs and their matching basket item fingerprints without reconstructing them from raw excerpt IDs or enabling deferred retrieval strategies.

This finalization pass also adds canonical demo-path markers to standalone FTS excerpt lookup payloads, provenance snapshots, lookup basket-promotion items, and audit metadata. Direct excerpt lookup provenance and audit metadata now include canonical basket-promotion item snapshots with item-level readiness/count fields and singleton basket item ID/fingerprint lists as well, so fetched excerpts remain self-describing basket-ready evidence in the returned payload, nested provenance, and audit trail.

This finalization pass also adds stable `promotion_item_fingerprint` values to standalone FTS excerpt lookup payloads, nested provenance, lookup basket-promotion items, and audit metadata. Context-basket consumers can now audit direct excerpt lookup promotion evidence using the same item-level fingerprint surface as normal retrieval promotion bundles.

Canonical demo path advanced: `vault/context material -> FTS retrieval -> retrieval evidence -> context basket promotion -> engine revise/apply`.

Before-handoff canonical demo-path statement: this work advances `retrieve relevant material` by keeping retrieval FTS-first, deterministic, and auditable; it also supports `promote or gather context into the basket` by preserving provenance and query evidence on promotion bundles/items.

## Tasks Completed

1. Canonical demo-path step advanced: `retrieve relevant material`. Made SQLite FTS the authoritative MVP retrieval path while keeping PageIndex and embeddings fallback-only/deferred.
2. Canonical demo-path step advanced: `retrieve relevant material`. Stabilized FTS query, cache, constraint, date-range, shortlist, doc-type, scope, and fresh-run behavior for deterministic retrieval.
3. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Normalized retrieval payloads, provenance, citation/source/context bundles, evidence snapshots, sparse bundle rehydration, retrieval summary/manifest fingerprints, query constraint values, and basket-promotion evidence, including item-level date-range and matched-term normalization before basket-promotion fingerprinting, sparse excerpt-hit rehydration of `matched_terms` and `match_count`, deterministic FTS-only `basket_item_id` values for promotion, query-constraint fingerprints on basket-ready item and bundle snapshots, promotion-item fallback rehydration when sparse bundles omit duplicate basket item lists, excerpt lookup fingerprints on promotion items with sparse bundle backfill from canonical basket items by `item_id` or `basket_item_id`, promotion-item basket fingerprint propagation from canonical basket refs, retrieval manifest/result fingerprint binding for canonical FTS basket item IDs and hashed FTS match-query identity, manifest-backed canonical basket item fingerprints in direct retrieval diagnostics/evidence, doc-hit `top_basket_item_id` snapshots/backfill bound into result identity for document-level promotion, direct excerpt lookup provenance lists for basket-ready item IDs/fingerprints, direct lookup promotion item fingerprints, and basket-promotion item snapshots, standalone FTS excerpt lookup demo-path markers on payload/provenance/basket item/audit surfaces, standalone lookup audit basket-promotion item snapshots with singleton basket item ID/fingerprint lists, sparse manifest fallback for basket item IDs/counts/fingerprints when compact source/context snapshots lose top-level basket fields, FTS-only normalization for sparse manifest/summary basket item ID fallback fields, FTS-only normalization for sparse primary basket item identity, FTS-first sparse promotion item identity canonicalization when stale `item_id` values conflict with canonical FTS basket refs, paired sparse fingerprint fallback for both positional and compact FTS basket ref snapshots, raw excerpt-only sparse promotion item rejection before basket evidence rehydration, case-varied FTS basket ref canonicalization before sparse fingerprint pairing, explicit `canonical_demo_path_steps` markers on payload/source/context/basket-promotion evidence and retrieval summaries/manifests, and hashed FTS match-query fingerprints for audit without plaintext query-term exposure. The `src.qual.engine.retrieval`, canonical `exegesis_engine.retrieval`, and direct `exegesis_engine.retrieval.search_service` facades now export the FTS-first retrieval entrypoints, including direct FTS citation-bundle access, that reach this path.
4. Canonical demo-path steps advanced: `retrieve relevant material` and `promote or gather context into the basket`. Added fail-closed and audit-focused regression coverage for malformed/reversed date ranges, empty inputs, unresolved scopes, FTS-only excerpt lookup and payload normalization, excerpt lookup fingerprints, cache/query snapshots, facade/export availability across both engine retrieval packages and the direct canonical search-service compat shim, basket-promotion fingerprint propagation, sparse basket item ID and fingerprint rehydration, basket item and bundle query-constraint fingerprints, promotion-item lookup fingerprint propagation and sparse bundle lookup backfill through canonical basket item IDs, non-FTS basket item ID rejection, doc-level top basket item identity/result fingerprint binding, sparse source/context bundle backfill for doc-level basket identity, direct excerpt lookup provenance basket item ID/fingerprint lists, direct lookup promotion item fingerprints, demo-path markers, provenance basket-promotion snapshots, audit basket-promotion snapshots, and item-level singleton basket ID/fingerprint lists, manifest-backed sparse source-bundle basket refs, sparse manifest/summary fallback filtering for stale PageIndex, embedding-shaped, or raw excerpt basket IDs, sparse primary basket item ID fallback filtering for stale deferred-strategy IDs, sparse fingerprint pairing for mixed stale and canonical FTS basket refs including case-varied FTS IDs, raw excerpt-only sparse basket item rejection before context-basket promotion, case-varied stale non-FTS promotion `item_id` replacement or rejection before context-basket promotion, canonical demo-path marker propagation across direct and sparse-rehydrated basket-promotion surfaces and retrieval summaries/manifests, and hashed FTS match-query audit identity on retrieval outputs.
Task accounting: this high-risk handoff is summarized as the 4 meaningful task groups above, matching the kickoff budget. The later source-bearing finalization commits, including stale demo-path marker normalization for sparse rehydration, are folded into those groups rather than counted as separate inflated tasks.

## Kickoff Budget/Limits Compliance

- Task budget: `4` high-risk task groups; this handoff folds the cumulative retrieval work into 4 meaningful and testable task groups.
- File count: the corrected source-bearing range before this pass changes `7` source/test files plus `3` packet/artifact files; this pass changes `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`, and `THREAD_PACKET.md`.
- Size accounting before this packet refresh: the corrected source-bearing range `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` already exceeds the high-risk `<=300 net LOC` limit; this pass adds a small FTS excerpt lookup promotion-item fingerprint finalization, keeping the range above the limit.
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
12. Added retrieval-manifest fallback for sparse source/context bundle basket item IDs, counts, and fingerprints so compact snapshots remain promotion-ready when top-level basket fields are missing.
13. Added self-contained basket item snapshots, IDs, fingerprints, counts, and readiness fields to retrieval basket-promotion bundles and their sparse normalization path.
14. Added canonical sparse basket-promotion item identity normalization so an explicit FTS `basket_item_id` wins over stale generic `item_id` values before downstream source/context bundle promotion.
15. Aligned direct retrieval bundle basket IDs and sparse excerpt-hit basket rehydration on canonical `retrieval:fts:<excerpt_id>` item identity while preserving raw excerpt IDs separately for audit.
16. Added canonical FTS basket item identity fields to basket-promotion bundle `promotion_items` so direct and sparse promotion evidence can be promoted without depending on plain excerpt IDs.
17. Exported the canonical engine facade `retrieve_auto` default entrypoint through `src.qual.engine.retrieval.__all__`, with regression coverage keeping the facade export list aligned to the FTS-first engine surface.
18. Added deterministic `query_constraints_fingerprint` values to direct and sparse-rehydrated basket-promotion item snapshots so context-basket promotion evidence remains auditable against normalized query constraints.
19. Recomputed sparse basket-promotion bundle `query_constraints_fingerprint` values from normalized query constraints so stale bundle-level fingerprint text cannot survive rehydration.
20. Rehydrated sparse basket-promotion bundle `basket_promotion_items` from canonical `promotion_items` when the duplicate basket item list is missing, keeping self-contained FTS promotion bundles promotable.
21. Added deterministic `excerpt_lookup_fingerprint` propagation to direct and sparse-rehydrated basket-promotion `promotion_items`, with regression coverage tying those promotion items back to the canonical basket item lookup identity and covering sparse bundle backfill from matching basket items by either `item_id` or `basket_item_id`.
21. Added doc-level `top_basket_item_id` propagation through doc hits, doc citations, retrieval summaries, retrieval provenance, and the manifest so document-level retrieval output points directly at the canonical FTS basket item, with provenance preserving the full doc-level `top_basket_item_ids` list for audit comparison.
22. Bound doc-level `top_basket_item_ids` into the retrieval result fingerprint and added regression coverage that reconstructs the result fingerprint from the manifest fields.
23. Backfilled sparse source/context bundle `top_basket_item_ids` and `primary_basket_item_id` from surviving doc/excerpt snapshots so normalized engine-facing payloads preserve the same doc-level basket identity when summary or manifest fields are sparse.
24. Rehydrated canonical FTS basket item identity for sparse basket-promotion snapshots missing both identity fields, with regression coverage that preserves older item-id-only compatibility snapshots.
25. Added direct FTS excerpt lookup provenance lists for canonical basket item IDs and fingerprints so payload, provenance, and audit surfaces agree on promotable identity.
26. Added canonical basket item fingerprint propagation to direct and sparse-rehydrated basket-promotion `promotion_items`, with regression coverage proving the promotion item and canonical basket item carry the same FTS basket fingerprint.
27. Added canonical basket item fingerprint propagation to downstream payload and excerpt-bundle `excerpt_hits`, with regression coverage proving raw excerpt-hit snapshots match the FTS basket-promotion item fingerprint.
28. Exported the FTS-first facade and policy helpers through the canonical `exegesis_engine.retrieval` package, with regression coverage proving canonical engine-package imports expose `build_retrieval_query`, `retrieve_fts`, `retrieve_auto`, direct FTS citation bundles, and bundle/payload helpers while PageIndex and embeddings remain absent from the active facade. The canonical package now binds those facade exports from `src.qual.engine.retrieval.__all__` and inserts legacy service exports after the explicit `DEFERRED_STRATEGY_IDS` anchor so package-level FTS reachability cannot drift or depend on positional export slicing.
29. Tightened canonical retrieval query boolean constraint normalization by removing the shadowed loose integer/float path and adding shared regression coverage that both facades accept text booleans but reject non-canonical integer booleans before query fingerprinting.
30. Added FTS-only validation for sparse basket item ID fallback snapshots so stale PageIndex, embedding-shaped, or raw excerpt IDs cannot keep context-basket promotion marked ready after promotion item evidence has been stripped.
31. Paired sparse basket item fingerprint fallback with canonical FTS basket item ID fallback so stale fingerprint-only snapshots cannot leak basket-promotion provenance after invalid deferred-strategy IDs fail closed.
32. Added sparse promotion item identity canonicalization so explicit FTS `basket_item_id` values replace stale deferred-strategy `item_id` values, both item identity fields are restored when recoverable from an FTS excerpt, and unrecoverable case-varied deferred-strategy retrieval identities fail closed before basket promotion.
33. Normalized sparse retrieval manifest, summary, and document-citation basket item ID fallback fields, including manifest-only `top_basket_item_ids`, summary `basket_item_ids`, and fingerprint-only stale snapshots, through the canonical FTS-only basket ID validator so stale PageIndex, embedding-shaped, or raw excerpt identities fail closed before source/context/provenance rehydration.
34. Normalized sparse `primary_basket_item_id` fields through the canonical FTS-only basket ID validator and rehydrated missing primary identity from canonical FTS excerpt citations only, so stale deferred-strategy primary IDs cannot survive into provenance or source/context bundle promotion evidence.
35. Required sparse basket item fingerprint fallback snapshots to pair one-for-one with surviving canonical FTS basket item IDs, so unpaired fingerprint-only provenance cannot survive source/context bundle rehydration while valid basket IDs still preserve promotion readiness.
36. Added compact sparse basket fingerprint fallback normalization so valid compressed FTS fingerprint snapshots still rehydrate, while mixed stale PageIndex/FTS positional snapshots keep fingerprints paired only with the canonical FTS basket ref.
37. Normalized stale sparse `canonical_demo_path_steps` values back to the canonical FTS MVP markers across retrieval evidence, source bundles, downstream payloads, basket-promotion bundles, and promotion items so compact engine snapshots cannot mislabel basket-promotion evidence.
38. Added stable `fts_match_query_fingerprint` output, manifest/result binding, and sparse source/context bundle rehydration so retrieval evidence can be audited against the FTS match expression without exposing plaintext query terms. The result fingerprint payload now directly includes the hashed FTS match-query identity, with shared regression coverage proving altered match-query identity changes the result fingerprint.
39. Added canonical demo-path markers to direct retrieval summaries and sparse summary normalization, alongside manifest marker rehydration, so compact summary-backed engine snapshots remain self-describing for retrieval and basket-promotion handoff.
40. Added direct `exegesis_engine.retrieval.search_service` FTS-first facade exports, with shared regression coverage proving the direct compat shim matches `exegesis_engine.retrieval.__all__`, resolves every facade helper to the canonical engine object, and keeps PageIndex/embeddings strategy classes absent.
41. Tightened sparse source/context basket fingerprint fallback so compact fingerprint lists are accepted only when every candidate basket ref is canonical FTS; mixed stale PageIndex/embedding refs now preserve the surviving FTS basket ID but drop unauditable compact fingerprint evidence.
42. Tightened sparse basket-promotion item identity extraction so raw excerpt-only sparse items cannot survive source/context bundle rehydration or contribute basket item IDs and orphaned basket fingerprints; only canonical FTS basket identities can preserve promotion-ready evidence.
43. Preserved `matched_terms` and `match_count` when sparse basket-promotion items are rebuilt from excerpt hits, with shared regression coverage proving compact bundle rehydration keeps the same FTS match evidence as canonical basket-promotion items.
44. Added canonical demo-path markers to standalone FTS excerpt lookup payloads, provenance snapshots, lookup basket-promotion items, and audit metadata, with shared regression coverage proving direct lookup evidence is self-describing for retrieval and context-basket promotion.
45. Added standalone FTS excerpt lookup basket-promotion item snapshots to provenance and audit metadata, with shared regression coverage proving nested provenance and audit events preserve the canonical basket item, item-level singleton ID/fingerprint lists, promotion readiness/count, and demo-path markers needed for context-basket promotion.

## Commands Run

Required gates for this corrected merge candidate were re-run on 2026-05-13 against branch `codex/feat-retrieval-fts` after this source-bearing FTS excerpt lookup provenance/audit basket-item finalization.

- `python -m pytest tests/unit/test_unified_retrieval.py -q -k "sparse_fts_excerpt_lookup_payload_gets_canonical_provenance or retrieve_fts_excerpt_returns_canonical_fts_payload or retrieve_fts_excerpt_audit_records_stable_lookup_identity"` - passed 3 focused FTS excerpt lookup regressions, 100 deselected, after standalone lookup provenance, payloads, and audit events preserved the stable promotion item fingerprint alongside canonical basket item evidence.
- `python -m pytest tests/unit/test_unified_retrieval.py -q` - passed all 103 unified retrieval tests and 96 subtests after standalone FTS excerpt lookup promotion item fingerprints were added.
- `./quality-format.sh --check` - passed after the FTS excerpt lookup promotion-item fingerprint finalization.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the FTS excerpt lookup promotion-item fingerprint finalization.
- `./quality-test.sh` - passed smoke tests and 486 unit tests, including all 103 unified retrieval tests, after the FTS excerpt lookup promotion-item fingerprint finalization.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is the approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane errors when broader control-plane tests attempted to write `.codex/packet_router/logs/fixer__feat-commands__20260513T023119Z.log`, write `.codex/feature_runner/state.json`, invoke `ps`, write `.codex/packet_planner/state.json` in two planner tests, and move recovery artifacts under `.codex/worktree_recovery/feat-a__git-local__20260513T023125Z`.

Earlier gate run for the previous source-bearing raw excerpt-only sparse basket item fail-closed finalization:

- `python -m pytest tests/unit/test_unified_retrieval.py -k raw_excerpt_only_basket_items -q` - passed 1 focused raw excerpt-only sparse basket item rejection regression with 102 deselected after tightening basket item normalization.
- `python -m pytest tests/unit/test_unified_retrieval.py` - passed all 103 unified retrieval tests after the sparse basket item identity fix.
- `./quality-format.sh --check` - passed after the raw excerpt-only sparse basket item finalization.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the raw excerpt-only sparse basket item finalization.
- `./quality-test.sh` - passed smoke tests and 486 unit tests, including all 103 unified retrieval tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is the approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when broader control-plane tests attempted to write `.codex/packet_router/logs/fixer__feat-commands__20260513T013915Z.log`, write `.codex/feature_runner/state.json`, invoke `ps`, write `.codex/packet_planner/state.json` in two planner tests, and move recovery artifacts under `.codex/worktree_recovery/feat-a__git-local__20260513T013920Z`.

- `PYTHONPATH=. python -m pytest tests/unit/test_unified_retrieval.py -k "compact_fingerprints_for_mixed_basket_refs or pairs_fingerprints_with_valid_fts_basket_refs or rejects_unpaired_basket_fingerprint_snapshots" -q` - first run reproduced the compact mixed-ref fingerprint leak with 1 failure and 2 passes; rerun passed 3 focused sparse basket fingerprint regressions, 99 deselected, after source-bundle normalization was tightened.
- `PYTHONPATH=. python -m pytest tests/unit/test_unified_retrieval.py -q` - first full retrieval run passed 101 tests and failed the existing mixed-ref compact-fingerprint expectation in `test_sparse_retrieval_payload_filters_manifest_basket_ids_to_fts`; rerun passed all 102 unified retrieval tests and 96 subtests after the fixture was updated to expect fail-closed fingerprint evidence.
- `./quality-format.sh --check` - passed after the sparse basket fingerprint finalization.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the sparse basket fingerprint finalization.
- `./quality-test.sh` - passed smoke tests and 485 unit tests, including all 102 unified retrieval tests, after the sparse basket fingerprint finalization.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is the approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when broader control-plane tests attempted to write `.codex/packet_router/logs/fixer__feat-commands__20260513T012740Z.log`/`fixer__feat-commands__20260513T012757Z.log`, write `.codex/feature_runner/state.json`, invoke `ps`, write `.codex/packet_planner/state.json` in two planner tests, and move recovery artifacts under `.codex/worktree_recovery`.

- `python -m pytest tests/unit/test_unified_retrieval.py -q -k "canonical_engine_retrieval_package_exports_fts_facade or canonical_search_service_exports_fts_facade or engine_retrieval_package_exports_are_fts_only"` - passed 3 focused facade/export tests, 98 deselected, and 86 subtests after direct `exegesis_engine.retrieval.search_service` exports were aligned with the canonical FTS-first facade.
- `python -m pytest tests/unit/test_unified_retrieval.py -q` - passed all 101 unified retrieval tests and 96 subtests after direct `exegesis_engine.retrieval.search_service` exports were aligned with the canonical FTS-first facade.
- `./quality-format.sh --check` - passed after the direct canonical search-service compat shim export finalization.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the direct canonical search-service compat shim export finalization.
- `./quality-test.sh` - passed smoke tests and 484 unit tests, including all 101 unified retrieval tests, after the direct canonical search-service compat shim export finalization.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is the approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when broader control-plane tests attempted to write `.codex/packet_router/logs/fixer__feat-commands__20260513T012039Z.log`, write `.codex/feature_runner/state.json`, invoke `ps`, write `.codex/packet_planner/state.json` in two planner tests, and move recovery artifacts under `.codex/worktree_recovery`.

- `python -m pytest tests/unit/test_unified_retrieval.py -q` - passed all 100 unified retrieval tests and 50 subtests after retrieval summaries/manifests gained canonical demo-path markers and sparse summary/manifest normalization rehydrated them.
- `./quality-format.sh --check` - passed after the retrieval summary/manifest demo-path marker finalization.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the retrieval summary/manifest demo-path marker finalization.
- `./quality-test.sh` - passed smoke tests and 483 unit tests, including all 100 unified retrieval tests, after the retrieval summary/manifest demo-path marker finalization.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is the approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when broader control-plane tests attempted to write `.codex/packet_router/logs/fixer__feat-commands__20260513T011308Z.log`, write `.codex/feature_runner/state.json`, invoke `ps`, write `.codex/packet_planner/state.json` in two planner tests, and move recovery artifacts under `.codex/worktree_recovery`.

- `python -m pytest tests/unit/test_unified_retrieval.py -q` - initial run passed all 100 unified retrieval tests and 50 subtests before the final result-fingerprint payload binding; rerun exposed one expected-fixture mismatch in `test_retrieve_auto_returns_stable_doc_hits_for_downstream_consumers`; final rerun passed all 100 unified retrieval tests and 50 subtests after the expected result-fingerprint shape included `fts_match_query_fingerprint`.
- `./quality-format.sh --check` - passed after the FTS match-query fingerprint finalization.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the FTS match-query fingerprint finalization.
- `./quality-test.sh` - passed smoke tests and 483 unit tests, including all 100 unified retrieval tests, after the final result-fingerprint binding.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is the approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when broader control-plane tests attempted to write `.codex/packet_router/logs/fixer__feat-commands__20260513T010215Z.log`, write `.codex/feature_runner/state.json`, invoke `ps`, write `.codex/packet_planner/state.json` in two planner tests, and move recovery artifacts under `.codex/worktree_recovery`.
- `./quality-format.sh --check` - passed after the final handoff packet refresh.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the final handoff packet refresh.

- `python -m pytest tests/unit/test_unified_retrieval.py -k 'stale_demo_path_markers or manifest_basket_refs_for_sparse_source'` - first run reproduced the stale nested `retrieval_evidence` marker gap after top-level marker normalization; rerun passed 2 focused regressions after evidence snapshots with existing marker fields were normalized.
- `python -m pytest tests/unit/test_unified_retrieval.py` - first full run exposed an over-broad evidence marker addition that changed direct payload equality; rerun passed all 100 unified retrieval tests after evidence normalization was narrowed to snapshots that already carry `canonical_demo_path_steps`.
- `./quality-format.sh --check` - passed after stale demo-path marker normalization and packet update.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after stale demo-path marker normalization and packet update.
- `./quality-test.sh` - passed smoke tests and 483 unit tests, including all 100 unified retrieval tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is the approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and the retrieval surface, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors while inherited shared-scope unit tests attempted to write `.codex/packet_router/logs/fixer__feat-commands__20260513T003231Z.log`, write `.codex/feature_runner/state.json`, invoke `ps`, write `.codex/packet_planner/state.json` in two planner tests, and move recovery artifacts under `.codex/worktree_recovery`.

- `python -m pytest tests/unit/test_unified_retrieval.py` - passed 99 unified retrieval tests after adding shared regression coverage for canonical demo-path markers on downstream payload, source/context bundle, basket-promotion bundle, and promotion items.
- `./quality-format.sh --check` - passed after the canonical demo-path marker propagation and packet update.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the canonical demo-path marker propagation and packet update.
- `./quality-test.sh` - passed smoke tests and 482 unit tests, including all 99 unified retrieval tests, after the canonical demo-path marker propagation and packet update.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after the canonical demo-path marker propagation and packet update.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors inside the broader 482-test unit run when inherited shared-scope test execution attempted to write `.codex/packet_router/logs/fixer__feat-commands__20260513T001944Z.log`, write `.codex/feature_runner/state.json`, invoke `ps`, write `.codex/packet_planner/state.json`, or move recovery artifacts under `.codex/worktree_recovery`.

- `python -m pytest tests/unit/test_unified_retrieval.py -k "sparse_context_bundle_pairs_fingerprints_with_valid_fts_basket_refs or sparse_context_bundle_rejects_unpaired_basket_fingerprint_snapshots or sparse_context_bundle_rejects_stale_basket_ref_snapshots"` - passed 3 focused sparse basket ref/fingerprint regressions, 96 deselected, after adding positional and compact FTS basket fingerprint pairing.
- `python -m pytest tests/unit/test_unified_retrieval.py` - passed 99 unified retrieval tests after the compact sparse basket fingerprint fallback edit.
- `./quality-format.sh --check` - passed after the compact sparse basket fingerprint fallback edit and packet update.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the compact sparse basket fingerprint fallback edit and packet update.
- `./quality-test.sh` - passed smoke tests and 482 unit tests, including all 99 unified retrieval tests, after the compact sparse basket fingerprint fallback edit and packet update.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after the compact sparse basket fingerprint fallback edit and packet update.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors during inherited shared-scope unit tests: writing `.codex/packet_router/logs`, writing `.codex/feature_runner/state.json`, invoking `ps`, writing `.codex/packet_planner/state.json` in two planner tests, and moving recovery artifacts under `.codex/worktree_recovery`.
- `./quality-format.sh --check` - passed after the final packet evidence update.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the final packet evidence update.
- `pytest tests/unit/test_unified_retrieval.py` - blocked during collection because the shell environment did not include the repository on `PYTHONPATH` (`ModuleNotFoundError: No module named 'src'`).
- `PYTHONPATH=. pytest tests/unit/test_unified_retrieval.py` - passed 98 unified retrieval tests after the sparse basket fingerprint pairing edit.
- `./quality-format.sh --check` - passed after the sparse basket fingerprint pairing edit.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the sparse basket fingerprint pairing edit.
- `./quality-test.sh` - passed smoke tests and 481 unit tests, including all 98 unified retrieval tests, after the sparse basket fingerprint pairing edit.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after the sparse basket fingerprint pairing edit.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors during inherited shared-scope unit tests: writing `.codex/packet_router/logs`, writing `.codex/feature_runner/state.json`, invoking `ps`, writing `.codex/packet_planner/state.json` in two planner tests, and moving recovery artifacts under `.codex/worktree_recovery`. The retrieval regression surface completed inside this run with all unified retrieval tests passing before the unrelated control-plane failures.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_sparse_retrieval_payload_filters_manifest_basket_ids_to_fts -q` - passed 1 focused sparse manifest/summary/doc/primary-fallback basket ID regression after the FTS-only primary identity normalization edit, including manifest-only `top_basket_item_ids`, summary `basket_item_ids`, document-citation fallback, and stale `primary_basket_item_id` coverage.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_sparse_context_bundle_rejects_stale_basket_ref_snapshots -q` - passed 1 focused fail-closed stale basket ID/fingerprint regression after count fallback was kept tied to canonical FTS basket IDs.
- `python3 -m unittest tests.unit.test_unified_retrieval -q` - passed 97 unified retrieval tests after the FTS-only sparse primary basket ID normalization edit, including manifest-only, summary, document-citation fallback, stale primary ID, and stale fingerprint/count coverage.
- `./quality-format.sh --check` - passed after the FTS-only sparse primary basket ID normalization edit and packet update.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the FTS-only sparse primary basket ID normalization edit and packet update.
- `./quality-test.sh` - passed smoke tests and 480 unit tests, including all 97 unified retrieval tests, after the FTS-only sparse primary basket ID normalization edit and packet update.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after the FTS-only sparse primary basket ID normalization edit and packet update.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors during inherited shared-scope unit tests: writing `.codex/packet_router/logs`, writing `.codex/feature_runner/state.json`, invoking `ps`, writing `.codex/packet_planner/state.json` in two planner tests, and moving recovery artifacts under `.codex/worktree_recovery`. The retrieval regression surface completed inside this run with all unified retrieval tests passing before the unrelated control-plane failures.
- `PYTHONPATH=. pytest tests/unit/test_unified_retrieval.py -k 'stale_basket_ref_snapshots or deduplicates_sparse_basket_refs or uses_manifest_basket_refs_for_sparse_source'` - passed 3 focused sparse basket ID/fingerprint fallback regressions, 93 deselected, after pairing fingerprint fallback with canonical FTS ID fallback.
- `PYTHONPATH=. pytest tests/unit/test_unified_retrieval.py` - passed 96 unified retrieval tests after the paired sparse fingerprint fallback edit.
- `./quality-format.sh --check` - passed after the paired sparse fingerprint fallback edit.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the paired sparse fingerprint fallback edit.
- `./quality-test.sh` - passed smoke tests and 479 unit tests, including all 96 unified retrieval tests, after the paired sparse fingerprint fallback edit.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after the paired sparse fingerprint fallback edit.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and 479 unit tests through the retrieval surface, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when inherited shared-scope test execution attempted to write `.codex/packet_router/logs`, write `.codex/feature_runner/state.json`, write `.codex/packet_planner/state.json`, move recovery artifacts under `.codex/worktree_recovery`, or invoke `ps`.
- `./quality-format.sh --check` - passed after the final packet evidence update.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the final packet evidence update.
- `pytest tests/unit/test_unified_retrieval.py -k 'stale_basket_ref_snapshots or uses_manifest_basket_refs_for_sparse_source'` - blocked during collection because the shell environment did not include the repository on `PYTHONPATH` (`ModuleNotFoundError: No module named 'src'`).
- `PYTHONPATH=. pytest tests/unit/test_unified_retrieval.py -k 'stale_basket_ref_snapshots or uses_manifest_basket_refs_for_sparse_source'` - passed 2 focused sparse basket item ID fallback regressions, 94 deselected, after the FTS-only snapshot validation edit.
- `PYTHONPATH=. pytest tests/unit/test_unified_retrieval.py -k 'stale_basket_ref_snapshots or deduplicates_sparse_basket_refs or uses_manifest_basket_refs_for_sparse_source'` - passed 3 focused sparse basket item ID/count fallback regressions, 93 deselected, after ensuring any canonical FTS snapshot list can drive the promotion count while stale-only lists fail closed.
- `PYTHONPATH=. pytest tests/unit/test_unified_retrieval.py` - passed 96 unified retrieval tests after the FTS-only sparse basket ref validation edit.
- `./quality-format.sh --check` - passed after the FTS-only sparse basket ref validation edit.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the FTS-only sparse basket ref validation edit.
- `./quality-test.sh` - passed smoke tests and 479 unit tests, including all 96 unified retrieval tests, after the FTS-only sparse basket ref validation edit.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after the FTS-only sparse basket ref validation edit.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and 479 unit tests through the retrieval surface, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when inherited shared-scope test execution attempted to write `.codex/packet_router/logs`, write `.codex/feature_runner/state.json`, write `.codex/packet_planner/state.json`, move recovery artifacts under `.codex/worktree_recovery`, or invoke `ps`.
- `./quality-format.sh --check` - passed after the final packet evidence update.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the final packet evidence update.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_context_bundle_helper_uses_manifest_basket_refs_for_sparse_source -q` - passed 1 focused manifest-backed sparse source-bundle regression after the edit.
- `python3 -m unittest tests.unit.test_unified_retrieval -k 'context_bundle_helper' -q` - passed 10 context-bundle retrieval regressions after tightening manifest normalization to avoid adding empty fields to existing payloads.
- `python3 -m unittest tests.unit.test_unified_retrieval -q` - passed 95 unified retrieval tests after the edit.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 478 unit tests, including all 95 unified retrieval tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when inherited shared-scope test execution attempted to write `.codex/packet_router/logs`, write `.codex/feature_runner/state.json`, write `.codex/packet_planner/state.json`, move recovery artifacts under `.codex/worktree_recovery`, or invoke `ps`.

- `python -m pytest tests/unit/test_unified_retrieval.py -k "canonical_engine_retrieval_package_exports_fts_facade or exports_are_fts_only or normalizes_text_boolean_constraints" -q` - passed 3 focused retrieval tests, 91 deselected, and 42 subtests after replacing positional canonical package export insertion with the explicit `DEFERRED_STRATEGY_IDS` anchor.
- `python -m compileall -q engine/src/exegesis_engine/retrieval/__init__.py src/qual/engine/retrieval/__init__.py tests/unit/test_unified_retrieval.py` - passed after the anchor-based export insertion edit.
- `./quality-format.sh --check` - passed after the anchor-based export insertion edit.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the anchor-based export insertion edit.
- `./quality-test.sh` - passed smoke tests and 477 unit tests, including all unified retrieval tests, after the anchor-based export insertion edit.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after the anchor-based export insertion edit.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when inherited shared-scope test execution attempted to write `.codex/packet_router/logs`, write `.codex/feature_runner/state.json`, write `.codex/packet_planner/state.json`, move recovery artifacts under `.codex/worktree_recovery`, or invoke `ps`.
- `python -m pytest tests/unit/test_unified_retrieval.py -k "exports_are_fts_only or canonical_engine_retrieval_package_exports_fts_facade" -q` - passed 2 focused facade export regressions after the direct FTS citation-bundle export edit.
- `python -m pytest tests/unit/test_unified_retrieval.py -k "canonical_engine_retrieval_package_exports_fts_facade or exports_are_fts_only or normalizes_text_boolean_constraints" -q` - passed 3 focused retrieval tests, 91 deselected, and 2 subtests after the no-drift canonical package export edit.
- `python -m pytest tests/unit/test_unified_retrieval.py -k "canonical_engine_retrieval_package_exports_fts_facade or exports_are_fts_only or normalizes_text_boolean_constraints" -q` - passed 3 focused retrieval tests, 91 deselected, and 42 subtests after the canonical package dynamic export binding edit.
- `python -m pytest tests/unit/test_unified_retrieval.py -q` - passed 94 unified retrieval tests and 10 subtests after the no-drift canonical package export edit.
- `python -m pytest tests/unit/test_unified_retrieval.py -q` - passed 94 unified retrieval tests and 50 subtests after the canonical package dynamic export binding edit.
- `./quality-format.sh --check` - passed after the canonical package dynamic export binding edit.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the canonical package dynamic export binding edit.
- `./quality-test.sh` - passed smoke tests and 477 unit tests, including all unified retrieval tests, after the canonical package dynamic export binding edit.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after the canonical package dynamic export binding edit.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when inherited shared-scope test execution attempted to write `.codex/packet_router/logs`, write `.codex/feature_runner/state.json`, write `.codex/packet_planner/state.json`, move recovery artifacts under `.codex/worktree_recovery`, or invoke `ps`.
- `python -m compileall -q engine/src/exegesis_engine/retrieval/__init__.py src/qual/engine/retrieval/__init__.py tests/unit/test_unified_retrieval.py` - passed after the packet update.
- `./quality-format.sh --check` - passed after the packet update.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the packet update.
- `./quality-format.sh --check` - passed after the no-drift canonical package export edit.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the no-drift canonical package export edit.
- `./quality-test.sh` - passed smoke tests and 477 unit tests, including all unified retrieval tests, after the no-drift canonical package export edit.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after the no-drift canonical package export edit.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when inherited shared-scope test execution attempted to write `.codex/packet_router/logs`, write `.codex/feature_runner/state.json`, write `.codex/packet_planner/state.json`, move recovery artifacts under `.codex/worktree_recovery`, or invoke `ps`.
- `python -m pytest tests/unit/test_unified_retrieval.py -q` - passed 94 unified retrieval tests and 10 subtests after the canonical boolean constraint normalization edit.
- `python -m pytest tests/unit/test_unified_retrieval.py -q` - passed 93 unified retrieval tests and 8 subtests after the edit.
- `./quality-format.sh --check` - passed after the canonical boolean constraint normalization edit.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the canonical boolean constraint normalization edit.
- `./quality-test.sh` - passed smoke tests and 477 unit tests, including all unified retrieval tests, after the canonical boolean constraint normalization edit.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after the canonical boolean constraint normalization edit.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when inherited shared-scope test execution attempted to write `.codex/packet_router/logs`, `.codex/feature_runner/state.json`, `.codex/packet_planner/state.json`, move recovery artifacts under `.codex/worktree_recovery`, or invoke `ps`.
- `./quality-format.sh --check && ./quality-lint.sh` - passed after the packet update.
- `python -m pytest tests/unit/test_unified_retrieval.py -k "basket_promotion"` - passed 3 focused basket-promotion regressions before the edit.
- `python -m pytest tests/unit/test_unified_retrieval.py -k "basket_promotion_items_backfill_query_context_from_bundle"` - passed 1 focused regression after the edit.
- `python -m pytest tests/unit/test_unified_retrieval.py` - passed 92 unified retrieval tests after the edit.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./quality-test.sh` - passed smoke tests and 475 unit tests, including all unified retrieval tests.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when inherited shared-scope test execution attempted to write `.codex/packet_router/logs`, `.codex/feature_runner/state.json`, `.codex/packet_planner/state.json`, move recovery artifacts under `.codex/worktree_recovery`, or invoke `ps`.
- `PYTHONPATH=. python -m pytest tests/unit/test_unified_retrieval.py -k sparse_context_bundle_pairs_fingerprints_with_valid_fts_basket_refs -q` - passed before and after the case-varied FTS basket-ref canonicalization edit.
- `PYTHONPATH=. python -m pytest tests/unit/test_unified_retrieval.py -q` - passed 99 unified retrieval tests and 50 subtests after the case-varied FTS basket-ref canonicalization edit.
- `./quality-format.sh --check` - passed after the case-varied FTS basket-ref canonicalization edit.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the case-varied FTS basket-ref canonicalization edit.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after the case-varied FTS basket-ref canonicalization edit.
- `./quality-test.sh` - passed smoke tests and 482 unit tests, including all unified retrieval tests, after the case-varied FTS basket-ref canonicalization edit.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all 482 unit tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when inherited shared-scope test execution attempted to write `.codex/packet_router/logs`, write `.codex/feature_runner/state.json`, invoke `ps`, write `.codex/packet_planner/state.json`, or move recovery artifacts under `.codex/worktree_recovery`.
- `python -m pytest tests/unit/test_unified_retrieval.py` - initially failed 7 helper/source/context equality regressions after the demo-path marker edit, then failed 1 context-bundle equality regression after the first focused fix; both failures were resolved in the second focused fix attempt.
- `python -m pytest tests/unit/test_unified_retrieval.py` - passed 99 unified retrieval tests after direct and sparse-rehydrated demo-path marker propagation was aligned.
- `./quality-format.sh --check` - passed after the demo-path marker propagation edit.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the demo-path marker propagation edit.
- `./quality-test.sh` - passed smoke tests and 482 unit tests, including all 99 unified retrieval tests, after the demo-path marker propagation edit.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after the demo-path marker propagation edit.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors inside the broader 482-test unit run when inherited shared-scope test execution attempted to write `.codex/packet_router/logs/fixer__feat-commands__20260513T001121Z.log`, write `.codex/feature_runner/state.json`, invoke `ps`, write `.codex/packet_planner/state.json`, or move recovery artifacts under `.codex/worktree_recovery`.
- `python -m pytest tests/unit/test_unified_retrieval.py -k "retrieval_context_bundle_helper_uses_manifest_basket_refs_for_sparse_source"` - passed 1 focused sparse source-bundle rehydration regression after the demo-path marker backfill edit.
- `./quality-format.sh --check` - passed after the sparse source-bundle demo-path marker backfill edit.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the sparse source-bundle demo-path marker backfill edit.
- `./quality-test.sh` - passed smoke tests and 482 unit tests, including all 99 unified retrieval tests, after the sparse source-bundle demo-path marker backfill edit.
- `./typecheck-test.sh` - passed Python source compilation under `src/` after the sparse source-bundle demo-path marker backfill edit.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and all unified retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors inside the broader 482-test unit run when inherited shared-scope test execution attempted to write `.codex/packet_router/logs/fixer__feat-commands__20260513T002336Z.log`, write `.codex/feature_runner/state.json`, invoke `ps`, write `.codex/packet_planner/state.json`, or move recovery artifacts under `.codex/worktree_recovery`.
- `./quality-format.sh --check` - passed after the handoff packet update.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after the handoff packet update.

Older gate history for this corrected merge candidate:

- `python -m pytest tests/unit/test_unified_retrieval.py -k basket_promotion -q` - passed 3 focused basket-promotion regressions after adding basket item `query_constraints_fingerprint` propagation.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `./quality-test.sh` - passed smoke tests and 475 unit tests, including all 92 unified retrieval tests.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun with `SCOPE_ALLOW_SHARED=1`.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when tests attempted to write `.codex/packet_router/logs`, `.codex/feature_runner/state.json`, `.codex/packet_planner/state.json`, move recovery artifacts under `.codex/worktree_recovery`, or invoke `ps`.
- `python -m pytest tests/unit/test_unified_retrieval.py -q` - passed 92 unified retrieval tests and 8 subtests after the packet refresh.

Prior gate history for this corrected merge candidate:

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
- `pytest tests/unit/test_unified_retrieval.py -k basket_promotion_bundle_backfills_item_policy_and_rejects_non_fts_identity` - blocked at collection because the shell environment lacked repo-root imports (`ModuleNotFoundError: No module named 'src'`).
- `PYTHONPATH=. pytest tests/unit/test_unified_retrieval.py -k basket_promotion_bundle_backfills_item_policy_and_rejects_non_fts_identity` - initially failed because sparse promotion normalization computed the canonical FTS identity but did not overwrite stale `item_id`; fixed in the first focused gate attempt.
- `PYTHONPATH=. pytest tests/unit/test_unified_retrieval.py -k "basket_promotion_bundle_backfills_item_policy_and_rejects_non_fts_identity or retrieval_downstream_payload_helper_normalizes_numeric_citation_status"` - passed 2 focused retrieval regressions after preserving the sparse missing-`basket_item_id` case.
- `PYTHONPATH=. pytest tests/unit/test_unified_retrieval.py -k "basket_promotion_bundle_backfills_item_policy_and_rejects_non_fts_identity or retrieval_downstream_payload_helper_normalizes_numeric_citation_status or basket_promotion_items_backfill_query_context_from_bundle"` - passed 3 focused retrieval regressions after restoring derivation when both sparse item identity fields are missing.
- `PYTHONPATH=. pytest tests/unit/test_unified_retrieval.py -k basket_promotion_bundle_backfills_item_policy_and_rejects_non_fts_identity` - passed the focused shared retrieval regression after tightening deferred-strategy `retrieval:` identity rejection to be case-insensitive.
- `./quality-format.sh --check` - passed after this source-bearing sparse promotion identity edit.
- `./quality-lint.sh` - passed shell syntax and trailing whitespace checks after this source-bearing sparse promotion identity edit.
- `./quality-test.sh` - passed smoke tests and 480 unit tests, including all 97 unified retrieval tests, after this source-bearing sparse promotion identity edit.
- `./typecheck-test.sh` - passed Python source compilation under `src/`.
- `make ci` - blocked at scope-check because `tests/unit/test_unified_retrieval.py` is an approved shared regression path; rerun requires the approved shared-file scope override.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed scope-check, format, lint, compile/typecheck, smoke tests, and retrieval tests, then failed with 6 unrelated sandbox/control-plane `PermissionError` errors when inherited shared-scope test execution attempted to write `.codex/packet_router/logs`, write `.codex/feature_runner/state.json`, invoke `ps`, write `.codex/packet_planner/state.json`, or move recovery artifacts under `.codex/worktree_recovery`.
- `SCOPE_ALLOW_SHARED=1 ./quality-test.sh` - reproduced the same 6 unrelated sandbox/control-plane `PermissionError` errors, confirming that exporting `SCOPE_ALLOW_SHARED` into unit tests changes control-plane test behavior outside retrieval scope; normal `./quality-test.sh` is green.

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
- Required retrieval and local format/lint/typecheck/test gates are green for this pass. Full `make ci` cannot complete in this sandbox with the approved shared regression edit: plain `make ci` stops at scope-check, and `SCOPE_ALLOW_SHARED=1 make ci` reaches the broader unit suite but fails in unrelated control-plane tests on sandbox-denied `.codex` writes and `ps` execution.
- All source-bearing work is now included in the reviewed implementation range; there is no longer a metadata-only branch-tip claim hiding source/test changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 3 Real workflow loop, especially `feat-retrieval-fts` retrieval/search and the exit criterion that retrieval returns structured results suitable for basket promotion.
- Product Vision capabilities affected: `2. Retrieval-first context handling` and `3. Canonical engine contract`.
- Architecture alignment: retrieval stays in `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, and `engine/src/exegesis_engine/retrieval/**`; no provider/routing/core app entrypoints are touched.
- Routing/provider impact: none.
- Proposed `README.md` patch text: none.
