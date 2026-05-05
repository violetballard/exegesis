## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Merge candidate for re-review: branch tip `HEAD` on `codex/feat-retrieval-fts` after this packet traceability correction commit; before this fixer the branch tip was `b6e026a0adf4137108b2388b88a630f902ab8b9f`, and the exact final SHA is reported in the fixer deliverable.
- Actual merge-candidate diff against `main`: `main...HEAD`, currently anchored at merge-base `dc8db42ddd554e38c1d390a089eac26ae8a16aa7`.
- Reviewer-requested traceability range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..HEAD`. This is the historical range that includes every source/test change after the earlier reviewed implementation head, including changes that are already reachable from current `main`.
- Current merge-base before this fixer pass: `dc8db42ddd554e38c1d390a089eac26ae8a16aa7`
- Traceability correction: the current merge candidate is branch tip `HEAD`, not `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, not `3fa8b5edfd7dac6eb22715eeed64ac8a3325ad52`, and not `b6e026a0adf4137108b2388b88a630f902ab8b9f` after this fixer commit is created. Earlier packet wording about `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and about post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` metadata-only commits is superseded. No commit with source or test changes in `adfa8cdadd43747ffbcb612e4151e262b13e52ca..HEAD` is described as metadata-only in this packet.
- Implementation commit classification: `19b99a7034e28aadba7ddc7ef20fdf9a2fcbae2a` (`Fail closed on unresolved FTS collection scopes`) changes `src/qual/retrieval/service.py` and `tests/unit/test_unified_retrieval.py`; `d00ee5c38a6b8a49ae0c343a97bc11796b1bac81` (`Expose retrieval candidate resolution`) changes `src/qual/retrieval/service.py` and `src/qual/engine/retrieval/payload.py`; `3fa8b5edfd7dac6eb22715eeed64ac8a3325ad52` (`Keep sparse basket items authoritative`) changes `src/qual/engine/retrieval/payload.py` and `tests/unit/test_unified_retrieval.py`; `b6e026a0adf4137108b2388b88a630f902ab8b9f` (`Expose excerpt lookup fingerprints in citations`) changes `src/qual/retrieval/service.py` and `tests/unit/test_unified_retrieval.py` as well as `THREAD_PACKET.md`. These are implementation commits, not metadata-only commits, and they are included in the reviewer-requested traceability range.
- Scope classification: high-risk fixer under the 4-task cap because this reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Handoff type: retrieval feature fixer handoff for the FTS-first retrieval lane.

## Scope Completed

This re-review packet covers the complete current merge candidate from `main...HEAD` and the reviewer-requested historical traceability range `adfa8cdadd43747ffbcb612e4151e262b13e52ca..HEAD`. That range includes sparse basket-reference normalization, packet-accounting refreshes, the owned-path malformed retrieval-scope guard, the collection-scope fail-closed guard, the owned-path canonical doc-scope normalization, the owned-path sparse query scope canonicalization, the unknown doc-scope fail-closed guard, the candidate-resolution implementation in `d00ee5c38a6b8a49ae0c343a97bc11796b1bac81`, the sparse basket item authority fix in `3fa8b5edfd7dac6eb22715eeed64ac8a3325ad52`, and this packet traceability refresh. No source-bearing commit after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` is hidden behind metadata-only wording.

The implementation keeps SQLite FTS as the authoritative retrieval path. It exports canonical FTS excerpt fetch helpers through retrieval facades, normalizes FTS strategy hit snapshots, stabilizes payload and provenance reconstruction, exposes deterministic excerpt fingerprints, fails closed if internal excerpt payload normalization or sparse basket-promotion rehydration is asked to accept a non-FTS source strategy, and carries canonical basket promotion IDs, counts, fingerprints, query/result fingerprints, query context, and doc identity fingerprints through canonical excerpt bundles, retrieval evidence, retrieval summaries, provenance snapshots, and sparse engine payload backfills.

This fixer also keeps retrieval scopes fail-closed by rejecting malformed empty `doc:` and `collection:` scope values before the FTS candidate set is built. Doc-scoped retrieval now trims and canonicalizes the document identifier before applying the FTS filter and before building query fingerprints, evidence, provenance, and basket-promotion metadata, so whitespace-padded document scopes resolve to the same deterministic document candidate and the same auditable output contract. Unknown doc-scoped retrieval now fails closed before evidence and basket-promotion metadata are built, so engine callers cannot mistake an unresolved document scope for an empty but valid FTS result. Sparse engine payload reconstruction now applies the same canonical `doc:<id>` and `collection:<id>` scope shape before normalizing query snapshots or rebuilding sparse query fingerprints, so downstream context/source bundle backfills do not drift from the service-side retrieval contract. Non-empty `collection:` scopes now fail closed until the FTS path has an authoritative collection resolver, instead of silently falling back to vault-wide retrieval.

This candidate-resolution fixer adds an owned-path deterministic `candidate_resolution` snapshot to retrieval diagnostics, evidence, audit metadata, and doc-hit provenance. Engine run consumers can now distinguish explicit doc-scope resolution from vault FTS-shortlist narrowing while preserving the FTS-first contract and without activating PageIndex, embeddings, collection resolution, or alternate retrieval strategies.

This sparse basket metadata fixer makes full `basket_promotion_items` authoritative during engine payload/context/source bundle reconstruction when stale top-level basket item IDs, fingerprints, or counts are also present. That keeps context-basket promotion metadata aligned with the actual FTS excerpt promotion items instead of trusting drifted summary fields.

This finalization pass also carries the canonical FTS `excerpt_lookup_fingerprint` from retrieval-result provenance into excerpt hit dictionaries and basket promotion items. Engine flows can now promote retrieved excerpts to the context basket and later resolve or audit the same excerpt through the FTS-only lookup path without losing the deterministic lookup reference.

This basket-promotion readiness finalization pass adds the deterministic `basket_promotion_ready` flag to retrieval summaries, provenance snapshots, evidence, excerpt bundles, source/context bundles, downstream payloads, sparse payload reconstruction, and canonical FTS excerpt lookup payloads. Engine run consumers can now branch on an explicit promotion-ready contract instead of inferring readiness from counts or item arrays, while PageIndex and embeddings remain deferred.

This excerpt citation provenance finalization pass also carries the canonical FTS `excerpt_lookup_fingerprint` into excerpt citation snapshots, retrieval evidence excerpt citations, and retrieval evidence basket promotion items. Engine run consumers can now audit a retrieved excerpt citation and a promoted basket item against the same FTS-only lookup reference without rehydrating the full excerpt hit.

Focused regression coverage verifies canonical FTS excerpt lookup, PageIndex fail-closed behavior, facade exports, excerpt bundle basket metadata, retrieval summary basket references, sparse non-FTS excerpt rehydration rejection, sparse duplicate/empty basket reference normalization, unresolved collection-scope rejection, unknown doc-scope rejection through the service and engine facade, and engine payload reconstruction from compact/sparse retrieval summary snapshots.

PageIndex and embeddings remain deferred/compatibility-only paths and are not introduced as active retrieval strategies.

## Tasks Completed

1. Made canonical excerpt lookup and excerpt payload normalization FTS-only, including stable excerpt lookup fingerprints, PageIndex fail-closed behavior, and retrieval facade exports for the canonical excerpt fetch path.
2. Normalized retrieval strategy, query, payload, source bundle, provenance, citation, and cache snapshots so downstream engine flows receive deterministic FTS-first retrieval evidence, including canonical scope normalization for sparse query snapshots reconstructed by engine payload helpers.
3. Propagated basket promotion metadata through canonical FTS excerpt lookup, excerpt bundles, retrieval evidence, retrieval summaries, provenance snapshots, context/source bundles, and engine payload reconstruction, including canonical basket item IDs, promotion counts, fingerprints, query/result fingerprints, canonical doc-scope query context, doc identity fingerprints, duplicate/empty sparse-reference normalization, fail-closed handling for explicit non-FTS source strategies during sparse basket rehydration, and fail-closed validation for malformed empty retrieval scopes, unknown doc scopes, and unresolved collection scopes.
4. Added owned-path candidate-resolution metadata so diagnostics, evidence, audit records, and doc-hit provenance expose the exact final candidate docs searched and whether they came from doc scope or FTS shortlist narrowing, made sparse basket promotion items authoritative over stale summary IDs/counts during reconstruction, carried FTS excerpt lookup fingerprints into retrieval-result promotion refs and citation/evidence snapshots, added explicit basket promotion readiness across retrieval payloads and sparse reconstruction, then refreshed handoff metadata so the reviewed range, file list, gate evidence, and canonical demo-path mapping cover the actual branch-tip merge candidate.

## Files Changed

- `THREAD_PACKET.md` - updates this handoff packet for the complete branch-tip merge candidate and the reviewer-requested post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` traceability range, explicitly classifying packet-only versus implementation commits, including source-bearing commits `d00ee5c38a6b8a49ae0c343a97bc11796b1bac81`, `3fa8b5edfd7dac6eb22715eeed64ac8a3325ad52`, `dc8db42ddfa275aa1b357f3249c85c8dc3403484`, `b8f8eeab12684e6269c7bb70703370711a40790d`, `b6e026a0adf4137108b2388b88a630f902ab8b9f`, and this packet traceability correction.
- `src/qual/engine/retrieval/payload.py` - reconstructs and preserves deterministic query, provenance, source bundle, citation, evidence, basket promotion ID/count/readiness, fingerprint, query/result fingerprint, query context, doc identity, and candidate-resolution metadata from direct or sparse retrieval snapshots, canonicalizes sparse query scopes and sparse basket item ID/fingerprint lists, treats full basket promotion items as authoritative over stale summary metadata, and rejects explicit non-FTS source strategies during sparse basket promotion rehydration.
- `src/qual/retrieval/service.py` - implements canonical FTS excerpt lookup, FTS-only excerpt payload normalization, deterministic retrieval/provenance snapshots, FTS cache normalization, basket promotion metadata and readiness on canonical evidence, summaries, provenance, lookup payloads, context/source bundles, retrieval-result promotion refs, excerpt citations, and evidence basket items, fail-closed validation for empty `doc:`/`collection:` scopes plus unknown doc scopes and unresolved collection scopes, canonical doc-scope normalization before query fingerprints and downstream payloads are built, and deterministic candidate-resolution snapshots for diagnostics/evidence/audit/doc-hit provenance.
- `tests/unit/test_unified_retrieval.py` - verifies canonical FTS excerpt lookup, facade exports, deterministic payload/provenance normalization, basket metadata, sparse non-FTS excerpt rejection, sparse duplicate/empty basket reference normalization, sparse basket item authority over stale summary metadata, retrieval-result promotion refs and excerpt citations carrying the same FTS lookup fingerprint as canonical excerpt lookup, unknown doc-scope rejection, unresolved collection-scope rejection, and payload reconstruction.

Lane-owned source files:

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/payload.py`

Shared-by-approval files:

- `tests/unit/test_unified_retrieval.py` - approved shared regression surface for the retrieval lane canonical contract.

Historical post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` traceability files:

- `.codex/kickoff_packets/feat-retrieval-fts.md` - packet mirror metadata from earlier handoff accounting.
- `.codex/lane_meta/feat-retrieval-fts.json` - lane metadata from earlier handoff accounting.
- `THREAD_PACKET.md` - handoff packet updates across the historical range and this fixer.
- `src/qual/engine/retrieval/__init__.py` - engine retrieval facade exports for canonical excerpt helpers.
- `src/qual/engine/retrieval/fts_strategy.py` - FTS strategy hit snapshot normalization.
- `src/qual/engine/retrieval/payload.py` - engine retrieval payload reconstruction, sparse snapshot canonicalization, candidate-resolution backfill, and sparse basket item authority.
- `src/qual/retrieval/__init__.py` - retrieval facade exports for canonical excerpt helpers.
- `src/qual/retrieval/service.py` - FTS-only excerpt lookup, scope fail-closed behavior, candidate resolution, basket metadata, and deterministic payload/provenance snapshots.
- `tests/unit/test_unified_retrieval.py` - approved shared regression coverage for the canonical FTS retrieval contract.

Packet mirror update blocker:

- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still contain stale earlier packet wording in the worktree, but this sandbox rejects writes inside `.codex/**` with `Operation not permitted`. Treat `THREAD_PACKET.md` and the final fixer SHA as the authoritative re-review packet for this fixer pass.

Integrator-locked files: none.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: before this packet edit, the actual merge-candidate diff `main...HEAD` changes `4` files, within the high-risk `<=8 files` limit. The reviewer-requested historical traceability range `adfa8cdadd43747ffbcb612e4151e262b13e52ca..HEAD` changes `9` files, which is over the high-risk file budget and is called out here for re-review instead of being narrowed or hidden.
- Net LOC: before this packet edit, `git diff --shortstat main...HEAD` reports `4 files changed, 82 insertions(+), 21 deletions(-)`, for `+61` net LOC in the actual merge candidate. The reviewer-requested historical traceability range reports `9 files changed, 2203 insertions(+), 204 deletions(-)`, for `+1999` net LOC, which is explicitly disclosed for traceability.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is the approved shared-by-approval regression file for this lane.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; both remain deferred/compatibility-only.
- Remaining risk: high traceability/review risk due to the large historical branch-tip range and explicit AGENTS size-budget overrun, now mitigated only by making the actual merge candidate, full changed file list, branch-tip implementation surface, and canonical demo-path mapping explicit for re-review. Collection-specific retrieval remains intentionally deferred until an authoritative FTS collection resolver exists.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` active MVP focus for `feat-retrieval-fts`; Milestone 3/4 retrieval layer support for retrieving relevant material and promoting or gathering context into basket flows.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable generation/state.
- Canonical demo-path mapping: this final reviewed work advances the AGENTS active MVP canonical demo-path step `retrieve relevant material` because the FTS-first retrieval output is now deterministic, auditable, canonicalized for equivalent doc scopes, fail-closed for malformed or unresolved scopes, and explicit about the final candidate docs searched through the candidate-resolution snapshot. It also makes the next demo-path movement, `promote or gather context into the basket`, more real by exposing canonical FTS excerpt, evidence, summary, provenance, citation, and payload snapshots with deterministic promotion counts, explicit promotion readiness, canonical item IDs, item fingerprints, FTS excerpt lookup fingerprints, query/result fingerprints, canonical query context, doc identity fingerprints, and candidate-resolution metadata, while making full basket promotion item snapshots authoritative over stale summary IDs/counts and failing closed if sparse payload rehydration is given an explicit PageIndex/embeddings source strategy, if retrieval is asked to use an unresolved collection scope, or if a doc-scoped query names a document not present in the FTS metadata store.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

These gates were re-run by this fixer after the collection-scope guard, doc-scope canonicalization, sparse query scope canonicalization, unknown doc-scope guard, candidate-resolution snapshot, sparse basket item authority fix, retrieval-result lookup fingerprint propagation, basket promotion readiness propagation, and packet refresh:

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`; the scope checker reported no explicit policy for the branch and exited green.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed; ran smoke plus 138 unit tests, including unified retrieval citation/evidence lookup fingerprint coverage.
- `./typecheck-test.sh` - passed; compiled Python sources in `src/`.
- `make ci` - passed; reran setup, scope-check, format, lint, typecheck, and quality tests, including smoke plus 138 unit tests.
- `python -m unittest tests.unit.test_unified_retrieval -q` - passed before this edit; ran 69 unified retrieval tests.
- `python -m unittest tests.unit.test_unified_retrieval -q` - blocked on the first post-edit focused run; 67 tests passed, and 2 failures identified the missing evidence excerpt citation field and the expected engine payload fixture update.
- `python -m unittest tests.unit.test_unified_retrieval -q` - passed after the first focused fix attempt; ran 69 unified retrieval tests with excerpt citation/evidence lookup fingerprint coverage.

- `pytest tests/unit/test_unified_retrieval.py` - blocked because `pytest` is not installed on PATH.
- `python -m pytest tests/unit/test_unified_retrieval.py` - blocked because the active Python 3.14 interpreter does not have `pytest` installed; reran the focused suite through the repo-supported `unittest` command instead.
- `python3 -m unittest tests.unit.test_unified_retrieval -v` - passed; ran 69 unified retrieval tests after the basket promotion readiness update.
- `python - <<'PY' ...` malformed retrieval-scope smoke check - passed; verified empty `doc:` and `collection:` scopes fail closed.
- `python3 - <<'PY' ...` canonical doc-scope smoke check - passed; verified `doc:doc-pdf-1` and `doc:  doc-pdf-1  ` produce the same canonical scope, query fingerprint, result fingerprint, and excerpt IDs.
- `python - <<'PY' ...` sparse query scope canonicalization smoke check - passed; verified sparse payload query snapshots canonicalize `doc:  doc-pdf-1  ` to `doc:doc-pdf-1` and rebuild the same query fingerprint as the compact scope.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_unknown_doc_scope_is_rejected_before_retrieval_evidence tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_doc_scope_falls_back_to_fts_when_pageindex_missing tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_auto_emits_stable_query_fingerprint` - passed.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_collection_scope_is_rejected_until_fts_can_resolve_it tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_section_scope_is_rejected_until_pageindex_can_resolve_it tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_doc_scope_falls_back_to_fts_when_pageindex_missing` - passed.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_doc_scope_falls_back_to_fts_when_pageindex_missing tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_downstream_payload_helper_backfills_sparse_source_bundle_fields tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_context_bundle_helper_rebuilds_sparse_basket_refs_from_excerpt_hits` - passed.
- `python3 -m unittest tests.unit.test_unified_retrieval` - passed; ran 68 unified retrieval tests.
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_context_bundle_helper_prefers_basket_items_over_stale_summaries tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_context_bundle_helper_deduplicates_sparse_basket_refs -v` - passed.
- `python3 -m unittest tests.unit.test_unified_retrieval -v` - passed; ran 69 unified retrieval tests.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_single_retrieve_auto_interface tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_downstream_payload_exposes_policy_and_diagnostics_snapshot tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_doc_scope_falls_back_to_fts_when_pageindex_missing` - passed.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_context_bundle_helper_accepts_source_bundle_only_sources tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_downstream_payload_helper_accepts_source_bundle_only_sources tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_downstream_payload_helper_backfills_sparse_source_bundle_fields` - passed.

The final fixer deliverable restates the exact post-commit SHA and these fresh required gate outcomes.

Current fixer rerun against the packet traceability correction worktree:

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`; scope checker reported no explicit policy for the branch and exited green.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed; ran smoke plus 138 unit tests.
- `./typecheck-test.sh` - passed; compiled Python sources in `src/`.
- `make ci` - passed; reran setup, scope-check, format, lint, typecheck, and quality tests, including smoke plus 138 unit tests.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` packet mirror update - blocked by sandbox filesystem permissions: writes inside `.codex/**` fail with `Operation not permitted`.

## Risks/Blockers

Re-review should inspect `main...HEAD` as the current merge candidate, including the payload, approved shared regression, packet refresh, malformed retrieval-scope guard, collection-scope fail-closed behavior, candidate-resolution snapshot changes, and sparse basket item authority fix not already present on `main`. The branch intentionally keeps the current post-main implementation changes in the submitted tip; they advance the canonical demo-path step `retrieve relevant material` by making FTS evidence, basket promotion references, provenance, query context, sparse payload reconstruction, candidate resolution, malformed-scope handling, unresolved collection-scope handling, and sparse basket metadata reconciliation deterministic and fail-closed.
