## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Pre-fixer branch-tip SHA: `089b6fc4bef9ebbcf1bff6afd0c60b44c8f15905`
- Final HEAD SHA: reported in the fixer final response because a commit cannot contain its own SHA.
- Handoff classification: high-risk/shared because this fix touches retrieval behavior and approved shared retrieval regression coverage.
- Shared-file approval provenance: reviewer packet `fixer__feat-retrieval-fts__20260430T003042Z.prompt.txt` required a regression in `tests/unit/test_unified_retrieval.py`.

## Required Fixes Addressed

1. Added explicit FTS cache invalidation after `RetrievalService.add_or_update_document()` rebuilds FTS rows.
2. Added regression coverage that runs a query, updates the same document with changed matching text, reruns the same query, and asserts fresh FTS rows are used instead of stale cached hits.
3. Re-ran the required gates and recorded outcomes below.

## Scope Completed

SQLite FTS remains the authoritative retrieval path. The one-entry `FTSStrategy` cache is now explicitly cleared whenever document text is written and FTS rows are upserted, preventing stale excerpt snapshots from being reused after corpus mutation.

PageIndex and embeddings remain compatibility-only fallback surfaces outside the required FTS excerpt path. Routing/provider behavior is unchanged.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: expose `FTSStrategy.clear_cache()` for deterministic corpus-state invalidation.
2. Canonical demo-path step `retrieve relevant material`: clear the FTS strategy cache after `_upsert_fts_entries()` in `RetrievalService.add_or_update_document()`.
3. Canonical demo-path step `retrieve relevant material`: add regression coverage for same-query retrieval after document update, asserting fresh excerpt text and `cache_used=False`.
4. Canonical demo-path step `retrieve relevant material`: rerun scope, format, lint, test, typecheck, and CI gates.

## Files Changed

- `src/qual/engine/retrieval/fts_strategy.py`: adds explicit cache clearing for the one-entry FTS result cache.
- `src/qual/retrieval/service.py`: clears the FTS cache after FTS entries are upserted on document add/update.
- `tests/unit/test_unified_retrieval.py`: adds cache invalidation regression coverage for document updates.
- `THREAD_PACKET.md`: refreshes this handoff with current fixer scope and gate outcomes.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; within the high-risk cap.
- Changed files: `4`; within the high-risk `<=8` file guideline.
- Current uncommitted diff before final commit: `82 insertions(+), 37 deletions(-)`, net `+45`; within the high-risk `<=300` net LOC guideline.
- Integrator-locked files touched: none.
- Shared-by-approval files touched: `tests/unit/test_unified_retrieval.py` only.
- Lane-owned implementation files touched: `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/retrieval/service.py`.
- Routing/provider impact: none.

## Roadmap / Vision Mapping

- Roadmap items affected: `ROADMAP.md` Milestone 4 Retrieval Layer.
- Vision capabilities affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling, and capability 6, Auditable state and workflow.
- Canonical demo-path step advanced: `retrieve relevant material`.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m pytest tests/unit/test_unified_retrieval.py -k document_update_invalidates_fts_cache -q`: BLOCKED; `pytest` is not installed in this environment.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_document_update_invalidates_fts_cache`: PASS.
- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS; smoke passed and 125 unit tests passed.
- `./typecheck-test.sh`: PASS; Python sources under `src/` compile.
- `make ci`: PASS; setup, scope-check, format, lint, compile/typecheck, smoke, and 125 unit tests completed successfully.

## Risks / Blockers

- No implementation blocker is known.
- `pytest` is unavailable, so focused regression verification used `unittest`; all required repo gates passed.
