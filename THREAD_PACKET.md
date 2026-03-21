## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Scope goal: Deliver the retrieval-owned FTS MVP work in `src/qual/retrieval/**` while keeping the handoff fully inside retrieval-owned paths.
- Scope completed: Delivered the retrieval-owned FTS MVP work in `src/qual/retrieval/**` by preserving relevance-ordered `doc_hits`, returning deterministic retrieval-backed excerpt IDs and provenance, and explicitly rejecting `section:` queries until PageIndex can resolve concrete section targets.
- Tasks completed:
  1. Returned deterministic FTS excerpt IDs and retrieval-backed `fetch_excerpt()` output inside `src/qual/retrieval/service.py`.
  2. Preserved `doc_hits` relevance order so document-level ranking matches the top-ranked underlying excerpt hit.
  3. Added focused unit coverage for deterministic provenance, document ranking order, and retrieval-service excerpt fetch behavior.
  4. Completed the handoff metadata required by `INTEGRATION.md` with explicit retrieval-lane ownership and roadmap/vision mapping for the MVP FTS work.
- Files changed:
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Commands run with results:
  - Final re-review validation rerun on `2026-03-20` in this lane worktree against reviewer-required fixes `#1-#4`
  - `python -m unittest tests.unit.test_unified_retrieval` -> passed (`Ran 8 tests`, `OK`)
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed (`Ran 75 tests`, `OK`)
  - `./typecheck-test.sh` -> passed (`python3 -m compileall -q src`, exit `0`)
  - `make ci` -> passed (includes scope-check, format, lint, typecheck, smoke, and unit test gates)
- Reviewer fix closure:
  - `#1` made section-scoped retrieval explicit by rejecting `section:` queries in the FTS-only MVP path until PageIndex can resolve concrete section targets.
  - `#2` restored the correct low-risk/default-budget classification because the branch no longer carries engine-lane edits.
  - `#3` documented the section-scope limitation in both the packet and the retrieval tests so it cannot silently widen to the full corpus.
  - `#4` roadmap/vision notes now explicitly map only the retrieval-owned MVP work; the earlier engine-facing compatibility shim is out of scope for this handoff.
- Checkpoint status:
  - plan complete
  - first green tests: `python -m unittest tests.unit.test_unified_retrieval` passed (`Ran 8 tests`, `OK`) after the scope correction
  - ready for handoff: all required local gates passed on `2026-03-20`
- Risks/blockers:
  - No shared, integrator-locked, or cross-lane files remain in this handoff.
  - Engine-facing compatibility for `fts_*` excerpt IDs is intentionally out of scope for this lane and should be handled in an engine-owned lane if still required.
  - `section_hint` remains advisory-only in the FTS MVP path and does not resolve `section:` scopes until PageIndex can provide a concrete target.
- Roadmap item(s) affected:
  - Retrieval-owned MVP work: `Milestone 4: Retrieval Layer` -> FTS-first ingestion/index path for context/vault documents
  - Retrieval-owned MVP work: `Milestone 4: Retrieval Layer` -> Source-attribution model for retrieved chunks
  - Retrieval-owned MVP work: `Milestone 4: Retrieval Layer` -> Retrieval orchestration data needed before drafting/diff generation
  - `Milestone 2: Test Hardening` -> Add focused unit coverage for core behaviors
- Vision capability affected:
  - Retrieval-owned MVP work: `2. Retrieval-first context handling` -> SQLite FTS is the current MVP retrieval path and generation consumes retrieved chunks
  - Retrieval-owned MVP work: `3. Auditable generation` -> retrieval evidence remains deterministic and traceable
  - Retrieval-owned MVP work: `4. Operator-first control surface` -> downstream consumers receive stable retrieval-owned document and excerpt data without changing engine-owned adapters in this lane
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
