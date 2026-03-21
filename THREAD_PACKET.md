## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Reviewed implementation commit: `2c16551a6b3576eb9031d55a98525c21e04be255`
- Reviewed commit type: Retrieval implementation for the FTS-first MVP.
- Scope completed: The retrieval FTS implementation returns deterministic excerpt IDs, serves retrieval-backed `fetch_excerpt()` output, preserves `doc_hits` relevance order for document ranking, and has focused unit coverage for deterministic provenance, document ranking, and retrieval-service excerpt fetch behavior. PageIndex and embeddings remain deferred and are not required MVP paths.
- Related implementation files (reference only):
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Tasks completed:
  1. Returned deterministic FTS excerpt IDs and retrieval-backed `fetch_excerpt()` output inside the retrieval service.
  2. Preserved `doc_hits` relevance order so document-level ranking matches the top-ranked underlying excerpt hit.
  3. Added focused unit coverage for deterministic provenance, document ranking order, and retrieval-service excerpt fetch behavior.
  4. Completed the handoff metadata required by INTEGRATION.md with concrete scope, file, roadmap, and vision mapping for retrieval-owned MVP FTS work.
- Files changed:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Commands run with results:
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- Reviewer fix closure:
  - `#1` retargeted the packet to the retrieval implementation commit that contains the source and test changes.
  - `#2` removed any non-owned tooling paths from the feature delta and kept the file set inside lane-owned retrieval paths.
  - `#3` replaced the cleanup framing with a concrete scope-completed summary that matches the final retrieval code state.
- Checkpoint status:
  - plan complete
  - first green tests: `./quality-test.sh` passed
  - ready for handoff: all required local gates passed
- Risks/blockers:
  - No blockers. The packet wording is now explicit about the retrieval implementation boundary and the `section:` fallback behavior.
- Compatibility note:
  - Temporary compatibility guard: `section:` queries are rejected in the reviewed retrieval implementation until PageIndex can resolve concrete section targets; PageIndex and embeddings remain deferred and are not required paths for the current FTS-first MVP.
- Roadmap item(s) affected:
  - Milestone 4: Retrieval Layer -> FTS-first ingestion/index path for context/vault documents
  - Milestone 4: Retrieval Layer -> Retrieval orchestration data needed before drafting/diff generation
  - Milestone 4: Retrieval Layer -> Source-attribution model for retrieved chunks
  - Milestone 2: Test Hardening -> Add focused unit coverage for core behaviors
- Vision capability affected:
  - 2. Retrieval-first context handling
  - 3. Auditable generation
  - 4. Operator-first control surface
- Routing/provider impact note: None.
- Proposed `README.md` patch text: None.
