## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Scope completed: Delivered the retrieval-owned FTS MVP work in `src/qual/retrieval/**` by preserving relevance-ordered `doc_hits` and returning deterministic retrieval-backed excerpt IDs, plus one approved engine-lane compatibility shim in `src/qual/engine/tools/excerpt_tools.py` so engine-facing flows can resolve those `fts_*` IDs without reintroducing non-FTS retrieval paths.
- Tasks completed:
  1. Returned deterministic FTS excerpt IDs and retrieval-backed `fetch_excerpt()` support so engine excerpt tooling can resolve `fts_*` IDs.
  2. Preserved `doc_hits` relevance order so document-level ranking matches the top-ranked underlying excerpt hit.
  3. Added focused unit coverage for both document ranking order and engine-facing FTS excerpt fetch behavior.
  4. Completed the handoff metadata required by `INTEGRATION.md` with explicit high-risk ownership, approved exception, and roadmap/vision separation between retrieval-owned MVP work and the engine-facing compatibility shim.
- Files changed:
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
  - `src/qual/engine/tools/excerpt_tools.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Commands run with results:
  - Final re-review validation rerun on `2026-03-20` in this lane worktree against reviewer-required fixes `#1-#4`
  - `python -m unittest tests.unit.test_unified_retrieval` -> passed (`Ran 7 tests`, `OK`)
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed (`Ran 74 tests`, `OK`)
  - `./typecheck-test.sh` -> passed (`python3 -m compileall -q src`, exit `0`)
  - `make ci` -> passed (includes scope-check, format, lint, typecheck, smoke, and unit test gates)
- Reviewer fix closure:
  - `#1` retained the engine file with an explicit approved cross-lane exception for `src/qual/engine/tools/excerpt_tools.py` instead of incorrectly framing the branch as retrieval-owned-only
  - `#2` engine-facing excerpt fetching resolves retrieval-backed `fts_*` excerpt IDs through `src.qual.engine.tools.excerpt_tools.fetch_excerpt()`
  - `#3` packet and lane metadata now accurately state that the branch includes one engine-owned path and no longer claim low-risk owned-path-only scope
  - `#4` roadmap/vision notes now separate retrieval-owned FTS MVP work from the engine compatibility shim and explain why the non-owned change is required
- Checkpoint status:
  - plan complete
  - first green tests: `python -m unittest tests.unit.test_unified_retrieval` passed before the full gate rerun
  - before risky/shared file edit: reclassified the thread as high-risk and limited `src/qual/engine/tools/excerpt_tools.py` scope to the approved engine-facing excerpt fetch compatibility shim only
  - ready for handoff: all required local gates passed on `2026-03-20`
- Risks/blockers:
  - High-risk classification applies because this branch includes the engine-owned path `src/qual/engine/tools/excerpt_tools.py` outside the retrieval lane's owned paths.
  - Approved cross-lane exception: `src/qual/engine/tools/excerpt_tools.py` is intentionally limited to the engine-facing compatibility shim required for engine consumers to resolve retrieval-owned `fts_*` excerpt IDs.
  - `pin_to_context_set()` remains `DocIndexService`-specific; this fix only broadens engine excerpt resolution for retrieval-backed IDs.
- Roadmap item(s) affected:
  - Retrieval-owned MVP work: `Milestone 4: Retrieval Layer` -> FTS-first ingestion/index path for context/vault documents
  - Retrieval-owned MVP work: `Milestone 4: Retrieval Layer` -> Source-attribution model for retrieved chunks
  - Engine compatibility shim: `Milestone 4: Retrieval Layer` -> Retrieval orchestration in engine before drafting/diff generation
  - `Milestone 2: Test Hardening` -> Add focused unit coverage for core behaviors
- Vision capability affected:
  - Retrieval-owned MVP work: `2. Retrieval-first context handling` -> SQLite FTS is the current MVP retrieval path and generation consumes retrieved chunks
  - Retrieval-owned MVP work: `3. Auditable generation` -> retrieval evidence remains deterministic and traceable
  - Engine compatibility shim: `4. Operator-first control surface` -> existing engine/CLI excerpt contracts stay usable while the MVP remains FTS-first
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
