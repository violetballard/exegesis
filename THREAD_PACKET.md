## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Merge candidate implementation head: `99d56e7cfa5bcee902778da04a8c16fd0ea5d200`
- Authoritative reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..99d56e7cfa5bcee902778da04a8c16fd0ea5d200`
- Final fixer commit: packet-only reconciliation commit created after `99d56e7cfa5bcee902778da04a8c16fd0ea5d200`; its final HEAD SHA is reported with the fixer deliverable.
- Scope classification: high-risk/shared because the candidate includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Packet type: retrieval feature handoff for the full branch-tip FTS-first retrieval candidate.

## Scope Completed

The real merge candidate is the branch-tip implementation at `99d56e7cfa5bcee902778da04a8c16fd0ea5d200`, reviewed as `378cf9a74a3658058079a32f186fcd254c4a4034..99d56e7cfa5bcee902778da04a8c16fd0ea5d200`. This supersedes the stale narrowed `adfa8cdadd43747ffbcb612e4151e262b13e52ca` packet slice.

The candidate keeps SQLite FTS as the authoritative retrieval path, exports canonical retrieval query construction through the engine retrieval facade, normalizes boolean/date constraints deterministically, rejects invalid or reversed date ranges before FTS execution, removes stale FTS strategy caching, keeps PageIndex and embeddings as compatibility-only fallback shims, makes payload/source/context snapshots deterministic, normalizes sparse retrieval evidence safely, preserves safe FTS title hints, rejects non-FTS strategy provenance before canonical merge, reports token-exact matched-term provenance, canonicalizes ingested document types, adds auditable query/date/candidate/shortlist evidence fields, and exposes doc-level citation anchors plus basket item fingerprints for downstream basket/audit consumers.

## Required Fixes Addressed

1. Chose the real merge candidate: branch-tip implementation head `99d56e7cfa5bcee902778da04a8c16fd0ea5d200`.
2. Did not submit the stale `adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice. Later source/test commits are intentionally included in the reviewed candidate.
3. Regenerated the handoff for the full reviewed range `378cf9a74a3658058079a32f186fcd254c4a4034..99d56e7cfa5bcee902778da04a8c16fd0ea5d200`, including all changed files and the broader retrieval scope.
4. Reran the required gates against the final packet-reconciled candidate; results are recorded below.
5. Added the explicit AGENTS.md canonical demo-path mapping: this work advances `retrieve relevant material` for the engine-first demo path.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: kept retrieval FTS-first by making excerpt lookup require FTS excerpt hits, normalizing copied FTS excerpt IDs at lookup boundaries, removing stale FTS strategy caching, and keeping PageIndex/embeddings fallback-only.
2. Canonical demo-path step `retrieve relevant material`: exported and normalized canonical retrieval query construction through the engine retrieval facade, including deterministic boolean and date constraint handling.
3. Canonical demo-path step `retrieve relevant material`: made retrieval payloads, matched-term provenance/evidence snapshots, citation bundles, doc-type metadata, query date ranges, and sparse source/context rehydration deterministic for downstream engine flows.
4. Canonical demo-path step `retrieve relevant material`: added downstream audit anchors for retrieved evidence, including doc-level citation fields, query/date/candidate/shortlist evidence context, policy-bound basket promotion refs, compact basket item fingerprint lists, and sparse basket fingerprint backfill.

## Files Changed

Authoritative candidate files changed for `378cf9a74a3658058079a32f186fcd254c4a4034..99d56e7cfa5bcee902778da04a8c16fd0ea5d200`:

- `.codex/kickoff_packets/feat-retrieval-fts.md` - stale kickoff packet mirror present in the candidate; this fixer session could not refresh it because the patch tool rejects `.codex` writes as outside the project boundary.
- `.codex/lane_meta/feat-retrieval-fts.json` - stale lane metadata mirror present in the candidate; this fixer session could not refresh it because the patch tool rejects `.codex` writes as outside the project boundary.
- `THREAD_PACKET.md` - authoritative handoff packet regenerated for the actual branch-tip candidate.
- `src/qual/engine/retrieval/__init__.py` - exports canonical query construction with strict optional-boolean normalization.
- `src/qual/engine/retrieval/fts_strategy.py` - removes stale result caching while preserving the compatibility `clear_cache` hook and explicitly exports only `FTSStrategy`.
- `src/qual/engine/retrieval/payload.py` - normalizes deterministic retrieval payloads, source/context bundles, present sparse retrieval-evidence list fields, sparse query confidentiality profiles, policy-bound basket-promotion items, compact basket item fingerprint lists, and sparse snapshot backfill.
- `src/qual/retrieval/service.py` - keeps FTS as the authoritative lookup path, normalizes copied FTS excerpt IDs while rejecting blank IDs, rejects invalid or reversed date ranges, rejects non-FTS strategy provenance before merge, preserves safe title hints, canonicalizes ingested document types, and emits deterministic evidence/citation/basket audit fields.
- `tests/unit/test_unified_retrieval.py` - approved shared regression coverage for the FTS-first retrieval contract, deterministic payloads, facade exports, basket refs, sparse normalization, FTS-only excerpt lookup, date-range validation, non-FTS provenance rejection, token-exact matched terms, doc-level citation anchors, and evidence context parity.

Full branch-tip candidate stat before this packet reconciliation commit: `8 files changed, 1499 insertions(+), 218 deletions(-)`.

Source/test surface included for implementation review:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Source/test stat included for implementation review: `5 files changed, 1104 insertions(+), 129 deletions(-)`.

Lane-owned source files:

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`

Shared-by-approval files:

- `tests/unit/test_unified_retrieval.py` - approved shared regression surface for the retrieval lane.

Out-of-lane tooling files: none.

Integrator-locked files: none.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: `8/8` high-risk files.
- Source/test file count: `5` files.
- Full branch-tip candidate net LOC before this packet reconciliation commit: `+1281`.
- Source/test net LOC included for implementation review: `+975`.
- Size exception required: yes. The actual branch-tip candidate exceeds the AGENTS.md high-risk `<=300` net LOC guideline because it includes the full retrieval payload/service/test implementation, not only the stale narrowed packet slice.
- Explicit size exception request: approve review of the full source/test candidate through `99d56e7cfa5bcee902778da04a8c16fd0ea5d200` as a single high-risk retrieval handoff because splitting the already-committed branch tip would reintroduce the traceability gap the reviewer flagged.
- Shared-file approval note: `tests/unit/test_unified_retrieval.py` is included as the approved shared-by-approval regression surface for the retrieval lane.
- Shared/integrator-locked confirmation: no additional shared-by-approval files and no integrator-locked files require approval.
- Routing/provider impact: none.
- PageIndex/embeddings impact: none; PageIndex and embeddings remain deferred/compatibility-only and are not active retrieval paths.
- Merge risk: high until reviewer accepts the corrected full branch-tip range and size exception; implementation risk is contained to retrieval-owned paths plus the approved shared test file.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` Milestone 4 retrieval layer; active MVP focus for FTS-first retrieval.
- Vision capabilities affected: `PRODUCT_VISION.md` retrieval-first context handling and auditable state/workflow.
- Canonical demo-path mapping: this work advances `retrieve relevant material` for the canonical engine-first demo path by returning deterministic, auditable FTS excerpts and failing closed for PageIndex-only excerpt IDs.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Commands Run

Required gates for the corrected candidate, rerun on 2026-05-05 after this packet reconciliation:

- `make scope-check` PASS.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS.
- `./typecheck-test.sh` PASS.
- `make ci` PASS.

Additional focused evidence from the branch:

- `python3 -m unittest tests.unit.test_unified_retrieval -v` PASS, 63 tests.
- `python -m pytest tests/unit/test_unified_retrieval.py -k 'merge_hits_rejects_non_fts_provenance_strategy or retrieval_hits_reject_non_fts_source_strategies'` FAIL, active Python 3.14 has no `pytest` module; no environment changes were made.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_merge_hits_rejects_non_fts_provenance_strategy tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_hits_reject_non_fts_source_strategies` PASS, 2 focused tests.

## Risks/Blockers

No implementation blocker is known. The remaining reviewer-facing risks are the requested AGENTS.md size exception for the full high-risk branch-tip candidate and the stale protected `.codex` mirrors, which remain changed files in the historical candidate but could not be edited by this fixer because `.codex` writes are rejected as outside the writable project boundary. `THREAD_PACKET.md` is the corrected authoritative handoff packet and now identifies the actual source/test surface that would be merged.
