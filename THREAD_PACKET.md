## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`

## Scope completed
- Kept SQLite FTS as the authoritative MVP retrieval path.
- Normalized FTS strategy cache keys so reversed `date_range` inputs map to the same canonical retrieval request.
- Added regression coverage proving mapping-shaped and dataclass-shaped retrieval queries share the same cache key when their date windows are semantically equivalent.

## AGENTS.md handoff packet
- Task budget: `8`
- Tasks completed:
  1. Canonicalized reversed `date_range` values inside `src/qual/engine/retrieval/fts_strategy.py` so the FTS-first cache key matches the canonical retrieval query shape.
  2. Added a focused regression in `tests/unit/test_unified_retrieval.py` for equivalent mapping/dataclass queries with reversed date bounds.
- Files changed:
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `tests/unit/test_unified_retrieval.py`

## Commands run with results
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_fts_strategy_normalizes_reversed_date_ranges_in_mapping_queries tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_fts_strategy_normalizes_string_boolean_constraints_in_mapping_queries tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_query_constructor_accepts_generic_iterable_constraint_values`: PASS
- `python -m unittest tests.unit.test_unified_retrieval`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks/blockers
- Risks: low; change is limited to FTS cache-key normalization and existing retrieval behavior remains FTS-first.
- Blockers: none

## Roadmap item(s) affected
- `ROADMAP.md`: `Milestone 4: Retrieval Layer`

## Vision capability affected
- `PRODUCT_VISION.md`: `2. Retrieval-first context handling`
- `PRODUCT_VISION.md`: `3. Auditable generation`

## Routing/provider impact note
- None

## Proposed README.md patch text
- None
