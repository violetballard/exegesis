## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Scope completed: Preserved relevance-ordered `doc_hits`, exposed retrieval-backed excerpt fetching through the engine excerpt tool so `fts_*` IDs resolve in engine-facing flows, added focused unit coverage, and updated the handoff mapping for MVP FTS retrieval work.
- Tasks completed:
  1. Returned deterministic FTS excerpt IDs and retrieval-backed `fetch_excerpt()` support so engine excerpt tooling can resolve `fts_*` IDs.
  2. Preserved `doc_hits` relevance order so document-level ranking matches the top-ranked underlying excerpt hit.
  3. Added focused unit coverage for both document ranking order and engine-facing FTS excerpt fetch behavior.
  4. Completed the handoff metadata required by `INTEGRATION.md` with concrete scope, file, roadmap, and vision mapping for MVP FTS retrieval work.
- Files changed:
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
  - `src/qual/engine/tools/excerpt_tools.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Commands run with results:
  - Final re-review validation rerun on `2026-03-20` in this lane worktree against reviewer-required fixes `#1-#3`
  - `python -m unittest tests.unit.test_unified_retrieval` -> passed (`Ran 7 tests`, `OK`)
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed (`Ran 74 tests`, `OK`)
  - `./typecheck-test.sh` -> passed (`python3 -m compileall -q src`, exit `0`)
  - `make ci` -> passed (includes scope-check, format, lint, typecheck, smoke, and unit test gates)
- Reviewer fix closure:
  - `#1` packet now includes `Scope completed`, the real changed-file list, and concrete roadmap/vision mappings for MVP FTS retrieval work
  - `#2` engine-facing excerpt fetching resolves retrieval-backed `fts_*` excerpt IDs through `src.qual.engine.tools.excerpt_tools.fetch_excerpt()`
  - `#3` `doc_hits` preserve first-seen relevance order from ranked excerpt hits, with focused unit coverage proving document-level ranking follows top-ranked hits
- Risks/blockers:
  - Cross-lane edit in `src/qual/engine/tools/excerpt_tools.py` is intentionally minimal and limited to the reviewer-required engine-facing excerpt fetch path.
  - `pin_to_context_set()` remains `DocIndexService`-specific; this fix only broadens engine excerpt resolution for retrieval-backed IDs.
- Roadmap item(s) affected:
  - `Milestone 4: Retrieval Layer` -> FTS-first ingestion/index path for context/vault documents
  - `Milestone 4: Retrieval Layer` -> Retrieval orchestration in engine before drafting/diff generation
  - `Milestone 4: Retrieval Layer` -> Source-attribution model for retrieved chunks
  - `Milestone 2: Test Hardening` -> Add focused unit coverage for core behaviors
- Vision capability affected:
  - `2. Retrieval-first context handling` -> SQLite FTS is the current MVP retrieval path and generation consumes retrieved chunks
  - `3. Auditable generation` -> retrieval evidence remains deterministic and traceable
  - `4. Operator-first control surface` -> engine-facing contracts stay usable from CLI/engine flows
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
