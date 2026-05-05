## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Merge candidate: current branch tip `a9f19bbc20dc71e3064e296993e59bb8de9ea554` before this malformed-scope guard commit; the final post-commit SHA is reported in the fixer deliverable.
- Reviewed implementation range for re-review: `20e79e4e2984b6cbf19fc81139a0ed012ecd141c..HEAD`
- Current merge-base before this fixer pass: `20e79e4e2984b6cbf19fc81139a0ed012ecd141c`
- Traceability correction: the current re-review range is anchored to the merge-base `20e79e4e2984b6cbf19fc81139a0ed012ecd141c`; no source-bearing commit in `20e79e4e2984b6cbf19fc81139a0ed012ecd141c..HEAD` is excluded from re-review. Earlier packet wording about post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` metadata-only commits remains superseded for this branch tip.
- Scope classification: high-risk fixer under the 4-task cap because this reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Handoff type: retrieval feature fixer handoff for the FTS-first retrieval lane.

## Scope Completed

This re-review packet covers the complete current merge candidate from `20e79e4e2984b6cbf19fc81139a0ed012ecd141c..HEAD`, including the sparse basket-reference normalization already on this branch, packet-accounting refreshes, and this owned-path malformed retrieval-scope guard. No source-bearing commit after `20e79e4e2984b6cbf19fc81139a0ed012ecd141c` is hidden behind metadata-only wording.

The implementation keeps SQLite FTS as the authoritative retrieval path. It exports canonical FTS excerpt fetch helpers through retrieval facades, normalizes FTS strategy hit snapshots, stabilizes payload and provenance reconstruction, exposes deterministic excerpt fingerprints, fails closed if internal excerpt payload normalization or sparse basket-promotion rehydration is asked to accept a non-FTS source strategy, and carries canonical basket promotion IDs, counts, fingerprints, query/result fingerprints, query context, and doc identity fingerprints through canonical excerpt bundles, retrieval evidence, retrieval summaries, provenance snapshots, and sparse engine payload backfills.

This fixer also keeps retrieval scopes fail-closed by rejecting malformed empty `doc:` and `collection:` scope values before the FTS candidate set is built. Doc-scoped retrieval now trims the document identifier before applying the FTS filter so whitespace-padded document scopes resolve to the same deterministic document candidate instead of an empty raw ID.

Focused regression coverage verifies canonical FTS excerpt lookup, PageIndex fail-closed behavior, facade exports, excerpt bundle basket metadata, retrieval summary basket references, sparse non-FTS excerpt rehydration rejection, sparse duplicate/empty basket reference normalization, and engine payload reconstruction from compact/sparse retrieval summary snapshots.

PageIndex and embeddings remain deferred/compatibility-only paths and are not introduced as active retrieval strategies.

## Tasks Completed

1. Made canonical excerpt lookup and excerpt payload normalization FTS-only, including stable excerpt lookup fingerprints, PageIndex fail-closed behavior, and retrieval facade exports for the canonical excerpt fetch path.
2. Normalized retrieval strategy, query, payload, source bundle, provenance, citation, and cache snapshots so downstream engine flows receive deterministic FTS-first retrieval evidence.
3. Propagated basket promotion metadata through canonical FTS excerpt lookup, excerpt bundles, retrieval evidence, retrieval summaries, provenance snapshots, context/source bundles, and engine payload reconstruction, including canonical basket item IDs, promotion counts, fingerprints, query/result fingerprints, query context, doc identity fingerprints, duplicate/empty sparse-reference normalization, fail-closed handling for explicit non-FTS source strategies during sparse basket rehydration, and fail-closed validation for malformed empty retrieval scopes.
4. Updated approved shared unified retrieval regression coverage and refreshed handoff metadata so the reviewed range, file list, gate evidence, and canonical demo-path mapping cover the actual branch-tip merge candidate.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md` - historical lane kickoff metadata changed earlier in the full branch range; this sandbox returned `EPERM` when this fixer attempted to update the mirror, so `THREAD_PACKET.md` is the corrected source of truth for re-review.
- `.codex/lane_meta/feat-retrieval-fts.json` - historical lane metadata changed earlier in the full branch range; this sandbox returned `EPERM` when this fixer attempted to update the mirror, so `THREAD_PACKET.md` is the corrected source of truth for re-review.
- `THREAD_PACKET.md` - updates this handoff packet for the complete reviewed implementation range.
- `src/qual/engine/retrieval/__init__.py` - exposes canonical retrieval query and excerpt fetch surfaces through the engine retrieval facade.
- `src/qual/engine/retrieval/fts_strategy.py` - keeps FTS strategy hit snapshots deterministic and FTS-first.
- `src/qual/engine/retrieval/payload.py` - reconstructs and preserves deterministic query, provenance, source bundle, citation, evidence, basket promotion ID/count, fingerprint, query/result fingerprint, query context, and doc identity metadata from direct or sparse retrieval snapshots, canonicalizes sparse basket item ID/fingerprint lists, and rejects explicit non-FTS source strategies during sparse basket promotion rehydration.
- `src/qual/retrieval/__init__.py` - exposes canonical retrieval query and excerpt fetch helpers through the retrieval facade.
- `src/qual/retrieval/service.py` - implements canonical FTS excerpt lookup, FTS-only excerpt payload normalization, deterministic retrieval/provenance snapshots, FTS cache normalization, basket promotion metadata on canonical evidence, summaries, provenance, and lookup payloads, and fail-closed validation for empty `doc:`/`collection:` scopes.
- `tests/unit/test_unified_retrieval.py` - verifies canonical FTS excerpt lookup, facade exports, deterministic payload/provenance normalization, basket metadata, sparse non-FTS excerpt rejection, sparse duplicate/empty basket reference normalization, and payload reconstruction.

Lane-owned source files:

- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`

Shared-by-approval files:

- `tests/unit/test_unified_retrieval.py` - approved shared regression surface for the retrieval lane canonical contract.

Integrator-locked files: none.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: `4/12` changed files for the current `20e79e4e2984b6cbf19fc81139a0ed012ecd141c..HEAD` branch-tip review range before this commit, plus this owned-path `src/qual/retrieval/service.py` update; cumulative historical retrieval scope still includes the approved shared regression surface.
- Net LOC for the current branch-tip review range before this commit is `+113/-40` across `3` files; this fixer adds `+8/-3` in `src/qual/retrieval/service.py` before packet refresh accounting.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is the approved shared-by-approval regression file for this lane.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; both remain deferred/compatibility-only.
- Remaining risk: high traceability/review risk due to the large historical branch-tip range and explicit AGENTS size-budget overrun, now mitigated only by making the actual merge candidate, full changed file list, branch-tip implementation surface, and canonical demo-path mapping explicit for re-review.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` active MVP focus for `feat-retrieval-fts`; Milestone 3/4 retrieval layer support for retrieving relevant material and promoting or gathering context into basket flows.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable generation/state.
- Canonical demo-path mapping: this final reviewed work advances the AGENTS active MVP canonical demo-path step `retrieve relevant material`; it also supports basket/context promotion by making canonical FTS excerpt, evidence, summary, provenance, and payload snapshots expose deterministic promotion counts, canonical item IDs, item fingerprints, query/result fingerprints, query context, and doc identity fingerprints, while failing closed if sparse payload rehydration is given an explicit PageIndex/embeddings source strategy.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

These gates were re-run by this fixer after the malformed-scope guard and packet refresh:

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`; the scope checker reported no explicit policy for the branch and exited green.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed; ran smoke plus 135 unit tests, including unified retrieval and `test_retrieval_context_bundle_helper_deduplicates_sparse_basket_refs`.
- `./typecheck-test.sh` - passed; compiled Python sources in `src/`.
- `make ci` - passed; reran setup, scope-check, format, lint, typecheck, and quality tests.
- `python - <<'PY' ...` malformed retrieval-scope smoke check - passed; verified empty `doc:` and `collection:` scopes fail closed.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_doc_scope_falls_back_to_fts_when_pageindex_missing tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_section_scope_is_rejected_until_pageindex_can_resolve_it tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_fts_is_the_canonical_entrypoint` - passed.
- `python -m unittest tests.unit.test_unified_retrieval` - passed; ran 66 unified retrieval tests.

The final fixer deliverable restates the exact post-commit SHA and these fresh required gate outcomes.

## Risks/Blockers

The `.codex` kickoff and lane metadata mirrors still contain stale historical packet wording. This fixer attempted no `.codex` mirror write; `THREAD_PACKET.md` remains the corrected source of truth for re-review. Re-review should inspect `20e79e4e2984b6cbf19fc81139a0ed012ecd141c..HEAD` as the current merge candidate, including the payload, approved shared regression, packet refresh, and malformed retrieval-scope guard changes not already present on `main`. The branch intentionally keeps the current post-main implementation changes in the submitted tip; they advance the canonical demo-path step `retrieve relevant material` by making FTS evidence, basket promotion references, provenance, query context, sparse payload reconstruction, and malformed-scope handling deterministic and fail-closed.
