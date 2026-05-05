## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Merge candidate: actual branch tip after this sparse-source-strategy guard commit; final SHA is reported in the fixer deliverable.
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`
- Current merge-base before this fixer pass: `b402b065618b5ad383c527c30b677f03c03a8c88`
- Traceability correction: the branch-tip implementation after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` is part of the merge candidate. The prior claim that `10272337c899350ff4e8ee74ba44e77ed6f1be38` was metadata-only is false and is replaced by this packet. This pass adds a source-bearing guard commit and keeps the reviewed range as `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`.
- Scope classification: high-risk fixer under the 4-task cap because this reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Handoff type: retrieval feature fixer handoff for the FTS-first retrieval lane.

## Scope Completed

This re-review packet covers the complete actual merge candidate from `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`, including the original FTS-only excerpt implementation, branch-tip retrieval facade and payload work, the later basket promotion metadata changes through `10272337c899350ff4e8ee74ba44e77ed6f1be38`, the owned-path sparse basket provenance normalization fix, and this final sparse-source-strategy guard. No source-bearing commit after `378cf9a74a3658058079a32f186fcd254c4a4034` is hidden behind metadata-only wording.

The implementation keeps SQLite FTS as the authoritative retrieval path. It exports canonical FTS excerpt fetch helpers through retrieval facades, normalizes FTS strategy hit snapshots, stabilizes payload and provenance reconstruction, exposes deterministic excerpt fingerprints, fails closed if internal excerpt payload normalization or sparse basket-promotion rehydration is asked to accept a non-FTS source strategy, and carries basket promotion IDs, counts, fingerprints, query/result fingerprints, query context, and doc identity fingerprints through canonical excerpt bundles, retrieval evidence, retrieval summaries, provenance snapshots, and sparse engine payload backfills.

Focused regression coverage verifies canonical FTS excerpt lookup, PageIndex fail-closed behavior, facade exports, excerpt bundle basket metadata, retrieval summary basket references, sparse non-FTS excerpt rehydration rejection, and engine payload reconstruction from compact/sparse retrieval summary snapshots.

PageIndex and embeddings remain deferred/compatibility-only paths and are not introduced as active retrieval strategies.

## Tasks Completed

1. Made canonical excerpt lookup and excerpt payload normalization FTS-only, including stable excerpt lookup fingerprints, PageIndex fail-closed behavior, and retrieval facade exports for the canonical excerpt fetch path.
2. Normalized retrieval strategy, query, payload, source bundle, provenance, citation, and cache snapshots so downstream engine flows receive deterministic FTS-first retrieval evidence.
3. Propagated basket promotion metadata through canonical FTS excerpt lookup, excerpt bundles, retrieval evidence, retrieval summaries, provenance snapshots, context/source bundles, and engine payload reconstruction, including basket item IDs, promotion counts, fingerprints, query/result fingerprints, query context, doc identity fingerprints, and fail-closed handling for explicit non-FTS source strategies during sparse basket rehydration.
4. Updated approved shared unified retrieval regression coverage and refreshed handoff metadata so the reviewed range, file list, gate evidence, and canonical demo-path mapping cover the actual branch-tip merge candidate.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md` - historical lane kickoff metadata changed earlier in the full branch range; this sandbox returned `EPERM` when this fixer attempted to update the mirror, so `THREAD_PACKET.md` is the corrected source of truth for re-review.
- `.codex/lane_meta/feat-retrieval-fts.json` - historical lane metadata changed earlier in the full branch range; this sandbox returned `EPERM` when this fixer attempted to update the mirror, so `THREAD_PACKET.md` is the corrected source of truth for re-review.
- `THREAD_PACKET.md` - updates this handoff packet for the complete reviewed implementation range.
- `src/qual/engine/retrieval/__init__.py` - exposes canonical retrieval query and excerpt fetch surfaces through the engine retrieval facade.
- `src/qual/engine/retrieval/fts_strategy.py` - keeps FTS strategy hit snapshots deterministic and FTS-first.
- `src/qual/engine/retrieval/payload.py` - reconstructs and preserves deterministic query, provenance, source bundle, citation, evidence, basket promotion ID/count, fingerprint, query/result fingerprint, query context, and doc identity metadata from direct or sparse retrieval snapshots, while rejecting explicit non-FTS source strategies during sparse basket promotion rehydration.
- `src/qual/retrieval/__init__.py` - exposes canonical retrieval query and excerpt fetch helpers through the retrieval facade.
- `src/qual/retrieval/service.py` - implements canonical FTS excerpt lookup, FTS-only excerpt payload normalization, deterministic retrieval/provenance snapshots, FTS cache normalization, and basket promotion metadata on canonical evidence, summaries, provenance, and lookup payloads.
- `tests/unit/test_unified_retrieval.py` - verifies canonical FTS excerpt lookup, facade exports, deterministic payload/provenance normalization, basket metadata, sparse non-FTS excerpt rejection, and payload reconstruction.

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
- File budget: `9/12` changed files for the full `378cf9a...HEAD` branch-tip review range; `5` source files, `1` approved shared test file, `3` handoff/metadata files.
- Net LOC for the final source-strategy guard pass before commit: `+62/-5` across `2` files. Full `378cf9a...HEAD` branch-tip review range remains the merge-candidate range for re-review after this commit.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is the approved shared-by-approval regression file for this lane.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; both remain deferred/compatibility-only.
- Remaining risk: moderate traceability/review risk due to the large historical branch-tip range, now mitigated by making the actual merge candidate, full changed file list, branch-tip implementation surface, and this final sparse-source-strategy guard explicit for re-review.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` active MVP focus for `feat-retrieval-fts`; Milestone 3/4 retrieval layer support for retrieving relevant material and promoting or gathering context into basket flows.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable generation/state.
- Canonical demo-path mapping: this final reviewed work advances the AGENTS active MVP canonical demo-path step `retrieve relevant material`; it also supports basket/context promotion by making canonical FTS excerpt, evidence, summary, provenance, and payload snapshots expose deterministic promotion counts, item IDs, item fingerprints, query/result fingerprints, query context, and doc identity fingerprints, while failing closed if sparse payload rehydration is given an explicit PageIndex/embeddings source strategy.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

These gates were run for the actual branch-tip merge candidate after the sparse-source-strategy guard:

- `make scope-check` - passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh tests/unit/test_unified_retrieval.py` - passed after the sparse-source-strategy guard; ran smoke plus 134 unit tests, including `test_sparse_excerpt_basket_rehydration_rejects_non_fts_strategy`.
- `./quality-test.sh` - passed after the sparse-source-strategy guard; ran smoke plus 134 unit tests, including unified retrieval.
- `./typecheck-test.sh` - passed; compiled Python sources in `src/`.
- `make ci` - passed; reran setup, scope-check, format, lint, typecheck, and quality tests.

The final fixer deliverable restates the exact post-commit SHA and gate outcomes.

## Risks/Blockers

The `.codex` kickoff and lane metadata mirrors could not be rewritten from this sandbox because writes to those paths returned `EPERM`; `THREAD_PACKET.md` is the corrected handoff source of truth. Re-review should inspect `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` as the actual merge candidate, including all retrieval facade, FTS strategy, payload, service, and approved shared regression changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
