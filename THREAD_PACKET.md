## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Merge candidate for re-review: branch tip `HEAD` on `codex/feat-retrieval-fts` after this packet-fixer commit; the exact final SHA is reported in the fixer deliverable.
- Reviewed implementation range for re-review: `main...HEAD`, currently anchored at merge-base `20e79e4e2984b6cbf19fc81139a0ed012ecd141c`.
- Current merge-base before this fixer pass: `20e79e4e2984b6cbf19fc81139a0ed012ecd141c`
- Traceability correction: the current re-review range is anchored to the merge-base `20e79e4e2984b6cbf19fc81139a0ed012ecd141c`; no source-bearing commit in `main...HEAD` is excluded from re-review. Earlier packet wording about `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and about post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` metadata-only commits is superseded for this branch tip.
- Implementation commit classification: `19b99a7034e28aadba7ddc7ef20fdf9a2fcbae2a` (`Fail closed on unresolved FTS collection scopes`) is implementation work, not metadata-only work. It changes `src/qual/retrieval/service.py` and `tests/unit/test_unified_retrieval.py` in addition to refreshing `THREAD_PACKET.md`, and it is included in the reviewed implementation range.
- Scope classification: high-risk fixer under the 4-task cap because this reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Handoff type: retrieval feature fixer handoff for the FTS-first retrieval lane.

## Scope Completed

This re-review packet covers the complete current merge candidate from `main...HEAD`, including the sparse basket-reference normalization already on this branch, packet-accounting refreshes, the owned-path malformed retrieval-scope guard, and the collection-scope fail-closed guard. No source-bearing commit after merge-base `20e79e4e2984b6cbf19fc81139a0ed012ecd141c` is hidden behind metadata-only wording.

The implementation keeps SQLite FTS as the authoritative retrieval path. It exports canonical FTS excerpt fetch helpers through retrieval facades, normalizes FTS strategy hit snapshots, stabilizes payload and provenance reconstruction, exposes deterministic excerpt fingerprints, fails closed if internal excerpt payload normalization or sparse basket-promotion rehydration is asked to accept a non-FTS source strategy, and carries canonical basket promotion IDs, counts, fingerprints, query/result fingerprints, query context, and doc identity fingerprints through canonical excerpt bundles, retrieval evidence, retrieval summaries, provenance snapshots, and sparse engine payload backfills.

This fixer also keeps retrieval scopes fail-closed by rejecting malformed empty `doc:` and `collection:` scope values before the FTS candidate set is built. Doc-scoped retrieval now trims the document identifier before applying the FTS filter so whitespace-padded document scopes resolve to the same deterministic document candidate instead of an empty raw ID. Non-empty `collection:` scopes now fail closed until the FTS path has an authoritative collection resolver, instead of silently falling back to vault-wide retrieval.

Focused regression coverage verifies canonical FTS excerpt lookup, PageIndex fail-closed behavior, facade exports, excerpt bundle basket metadata, retrieval summary basket references, sparse non-FTS excerpt rehydration rejection, sparse duplicate/empty basket reference normalization, unresolved collection-scope rejection, and engine payload reconstruction from compact/sparse retrieval summary snapshots.

PageIndex and embeddings remain deferred/compatibility-only paths and are not introduced as active retrieval strategies.

## Tasks Completed

1. Made canonical excerpt lookup and excerpt payload normalization FTS-only, including stable excerpt lookup fingerprints, PageIndex fail-closed behavior, and retrieval facade exports for the canonical excerpt fetch path.
2. Normalized retrieval strategy, query, payload, source bundle, provenance, citation, and cache snapshots so downstream engine flows receive deterministic FTS-first retrieval evidence.
3. Propagated basket promotion metadata through canonical FTS excerpt lookup, excerpt bundles, retrieval evidence, retrieval summaries, provenance snapshots, context/source bundles, and engine payload reconstruction, including canonical basket item IDs, promotion counts, fingerprints, query/result fingerprints, query context, doc identity fingerprints, duplicate/empty sparse-reference normalization, fail-closed handling for explicit non-FTS source strategies during sparse basket rehydration, and fail-closed validation for malformed empty retrieval scopes plus unresolved collection scopes.
4. Updated approved shared unified retrieval regression coverage and refreshed handoff metadata so the reviewed range, file list, gate evidence, and canonical demo-path mapping cover the actual branch-tip merge candidate.

## Files Changed

- `THREAD_PACKET.md` - updates this handoff packet for the complete reviewed implementation range and explicitly classifies packet-only versus implementation commits.
- `src/qual/engine/retrieval/payload.py` - reconstructs and preserves deterministic query, provenance, source bundle, citation, evidence, basket promotion ID/count, fingerprint, query/result fingerprint, query context, and doc identity metadata from direct or sparse retrieval snapshots, canonicalizes sparse basket item ID/fingerprint lists, and rejects explicit non-FTS source strategies during sparse basket promotion rehydration.
- `src/qual/retrieval/service.py` - implements canonical FTS excerpt lookup, FTS-only excerpt payload normalization, deterministic retrieval/provenance snapshots, FTS cache normalization, basket promotion metadata on canonical evidence, summaries, provenance, and lookup payloads, and fail-closed validation for empty `doc:`/`collection:` scopes plus unresolved collection scopes.
- `tests/unit/test_unified_retrieval.py` - verifies canonical FTS excerpt lookup, facade exports, deterministic payload/provenance normalization, basket metadata, sparse non-FTS excerpt rejection, sparse duplicate/empty basket reference normalization, unresolved collection-scope rejection, and payload reconstruction.

Lane-owned source files:

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/payload.py`

Shared-by-approval files:

- `tests/unit/test_unified_retrieval.py` - approved shared regression surface for the retrieval lane canonical contract.

Integrator-locked files: none.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: the complete branch-tip review range changes `4` files, within the high-risk `<=8 files` limit.
- Net LOC: before this packet-only fixer commit, `git diff --shortstat main...HEAD` reported `4 files changed, 146 insertions(+), 56 deletions(-)`, for `+90` net LOC, within the high-risk `<=300 net LOC` limit. This packet-only commit updates review metadata and keeps the range inside the high-risk file and LOC limits.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is the approved shared-by-approval regression file for this lane.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; both remain deferred/compatibility-only.
- Remaining risk: high traceability/review risk due to the large historical branch-tip range and explicit AGENTS size-budget overrun, now mitigated only by making the actual merge candidate, full changed file list, branch-tip implementation surface, and canonical demo-path mapping explicit for re-review. Collection-specific retrieval remains intentionally deferred until an authoritative FTS collection resolver exists.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` active MVP focus for `feat-retrieval-fts`; Milestone 3/4 retrieval layer support for retrieving relevant material and promoting or gathering context into basket flows.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable generation/state.
- Canonical demo-path mapping: this final reviewed work advances the AGENTS active MVP canonical demo-path step `retrieve relevant material` because the FTS-first retrieval output is now deterministic, auditable, and fail-closed for malformed or unresolved scopes. It also makes the next demo-path movement, `promote or gather context into the basket`, more real by exposing canonical FTS excerpt, evidence, summary, provenance, and payload snapshots with deterministic promotion counts, canonical item IDs, item fingerprints, query/result fingerprints, query context, and doc identity fingerprints, while failing closed if sparse payload rehydration is given an explicit PageIndex/embeddings source strategy or if retrieval is asked to use an unresolved collection scope.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

These gates were re-run by this fixer after the collection-scope guard and packet refresh:

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`; the scope checker reported no explicit policy for the branch and exited green.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed; ran smoke plus 136 unit tests, including unified retrieval and `test_collection_scope_is_rejected_until_fts_can_resolve_it`.
- `./typecheck-test.sh` - passed; compiled Python sources in `src/`.
- `make ci` - passed; reran setup, scope-check, format, lint, typecheck, and quality tests, including smoke plus 136 unit tests.
- `python - <<'PY' ...` malformed retrieval-scope smoke check - passed; verified empty `doc:` and `collection:` scopes fail closed.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_collection_scope_is_rejected_until_fts_can_resolve_it tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_section_scope_is_rejected_until_pageindex_can_resolve_it tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_doc_scope_falls_back_to_fts_when_pageindex_missing` - passed.
- `python -m unittest tests.unit.test_unified_retrieval` - passed; ran 67 unified retrieval tests.

The final fixer deliverable restates the exact post-commit SHA and these fresh required gate outcomes.

## Risks/Blockers

Re-review should inspect `main...HEAD` as the current merge candidate, including the payload, approved shared regression, packet refresh, malformed retrieval-scope guard, and collection-scope fail-closed changes not already present on `main`. The branch intentionally keeps the current post-main implementation changes in the submitted tip; they advance the canonical demo-path step `retrieve relevant material` by making FTS evidence, basket promotion references, provenance, query context, sparse payload reconstruction, malformed-scope handling, and unresolved collection-scope handling deterministic and fail-closed.
