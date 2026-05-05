## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Merge candidate: actual branch tip after this fixer packet commit; final SHA is reported in the fixer deliverable.
- Reviewed implementation range for re-review: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`
- Current merge-base before this fixer pass: `b402b065618b5ad383c527c30b677f03c03a8c88`
- Traceability correction: the branch-tip implementation after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` is part of the merge candidate. The prior claim that `10272337c899350ff4e8ee74ba44e77ed6f1be38` was metadata-only is false and is replaced by this packet.
- Scope classification: high-risk fixer under the 4-task cap because this reviewed range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Handoff type: retrieval feature fixer handoff for the FTS-first retrieval lane.

## Scope Completed

This re-review packet covers the complete actual merge candidate from `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD`, including the original FTS-only excerpt implementation, branch-tip retrieval facade and payload work, and the later basket promotion metadata changes through `10272337c899350ff4e8ee74ba44e77ed6f1be38`. No source-bearing commit after `378cf9a74a3658058079a32f186fcd254c4a4034` is hidden behind metadata-only wording.

The implementation keeps SQLite FTS as the authoritative retrieval path. It exports canonical FTS excerpt fetch helpers through retrieval facades, normalizes FTS strategy hit snapshots, stabilizes payload and provenance reconstruction, exposes deterministic excerpt fingerprints, and carries basket promotion IDs, counts, and fingerprints through canonical excerpt bundles, retrieval summaries, provenance snapshots, and sparse engine payload backfills.

Focused regression coverage verifies canonical FTS excerpt lookup, PageIndex fail-closed behavior, facade exports, excerpt bundle basket metadata, retrieval summary basket references, and engine payload reconstruction from compact/sparse retrieval summary snapshots.

PageIndex and embeddings remain deferred/compatibility-only paths and are not introduced as active retrieval strategies.

## Tasks Completed

1. Made canonical excerpt lookup FTS-only, including stable excerpt lookup fingerprints, PageIndex fail-closed behavior, and retrieval facade exports for the canonical excerpt fetch path.
2. Normalized retrieval strategy, query, payload, source bundle, provenance, citation, and cache snapshots so downstream engine flows receive deterministic FTS-first retrieval evidence.
3. Propagated basket promotion metadata through canonical FTS excerpt lookup, excerpt bundles, retrieval summaries, provenance snapshots, context/source bundles, and engine payload reconstruction, including basket item IDs, promotion counts, and fingerprints.
4. Updated approved shared unified retrieval regression coverage and refreshed handoff metadata so the reviewed range, file list, gate evidence, and canonical demo-path mapping cover the actual branch-tip merge candidate.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md` - historical lane kickoff metadata changed earlier in the full branch range; this sandbox returned `EPERM` when this fixer attempted to update the mirror, so `THREAD_PACKET.md` is the corrected source of truth for re-review.
- `.codex/lane_meta/feat-retrieval-fts.json` - historical lane metadata changed earlier in the full branch range; this sandbox returned `EPERM` when this fixer attempted to update the mirror, so `THREAD_PACKET.md` is the corrected source of truth for re-review.
- `THREAD_PACKET.md` - updates this handoff packet for the complete reviewed implementation range.
- `src/qual/engine/retrieval/__init__.py` - exposes canonical retrieval query and excerpt fetch surfaces through the engine retrieval facade.
- `src/qual/engine/retrieval/fts_strategy.py` - keeps FTS strategy hit snapshots deterministic and FTS-first.
- `src/qual/engine/retrieval/payload.py` - reconstructs and preserves deterministic query, provenance, source bundle, citation, basket promotion ID/count, and fingerprint metadata from direct or sparse retrieval snapshots.
- `src/qual/retrieval/__init__.py` - exposes canonical retrieval query and excerpt fetch helpers through the retrieval facade.
- `src/qual/retrieval/service.py` - implements canonical FTS excerpt lookup, deterministic retrieval/provenance snapshots, FTS cache normalization, and basket promotion metadata on canonical summaries and provenance.
- `tests/unit/test_unified_retrieval.py` - verifies canonical FTS excerpt lookup, facade exports, deterministic payload/provenance normalization, basket metadata, and payload reconstruction.

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
- Net LOC for the full `378cf9a...HEAD` branch-tip review range before this packet refresh: `+1687/-220`.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is the approved shared-by-approval regression file for this lane.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; both remain deferred/compatibility-only.
- Remaining risk: moderate traceability/review risk due to the large historical branch-tip range, now mitigated by making the actual merge candidate, full changed file list, and branch-tip implementation surface explicit for re-review.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` active MVP focus for `feat-retrieval-fts`; Milestone 3/4 retrieval layer support for retrieving relevant material and promoting or gathering context into basket flows.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable generation/state.
- Canonical demo-path mapping: this final reviewed work advances the AGENTS active MVP canonical demo-path step `retrieve relevant material`; it also supports basket/context promotion by making canonical FTS excerpt, summary, provenance, and payload snapshots expose deterministic promotion counts, item IDs, and item fingerprints.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

These gates are required for the actual branch-tip merge candidate and will be re-run after this packet refresh commit so their results are tied to the final SHA reported in the fixer deliverable:

- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`

Previous branch-tip gate evidence before this packet refresh was green for scope-check, format, lint, quality tests, typecheck, and CI. The final fixer deliverable restates the exact post-commit SHA and gate outcomes.

## Risks/Blockers

The `.codex` kickoff and lane metadata mirrors could not be rewritten from this sandbox because writes to those paths returned `EPERM`; `THREAD_PACKET.md` is the corrected handoff source of truth. Re-review should inspect `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` as the actual merge candidate, including all retrieval facade, FTS strategy, payload, service, and approved shared regression changes after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
