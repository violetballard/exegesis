# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Reviewed implementation commit: `36893f06df85409c4595d64adb8af60455c086a6`
- Cleanup / handoff alignment commit: `453e8664dadcee989a2579a97179e87db04b1607`
- Reviewed commit type: Canonical auto payload plumbing for the FTS-first MVP.
- Scope completed: The reviewed implementation routes `retrieve_auto()` through the retrieval service's canonical FTS-first payload path, exposes `retrieve_auto_payload()` for downstream consumers, re-exports `primary_strategy_id` from the engine retrieval package, and adds focused unit coverage for payload parity and package-export behavior. PageIndex and embeddings remain deferred and are not required MVP paths.

### Related implementation files (reference only)
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/tools/retrieval_tools.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

### Code-diff evidence
- `src/qual/engine/retrieval/__init__.py`: re-exports retrieval package entrypoints used by downstream engine consumers.
- `src/qual/engine/tools/retrieval_tools.py`: routes auto retrieval through the canonical retrieval-service payload path.
- `src/qual/retrieval/service.py`: provides the FTS-first payload implementation and deterministic downstream payload shaping.
- `tests/unit/test_unified_retrieval.py`: covers payload parity, export behavior, and downstream-facing retrieval results.
- No PageIndex or embeddings path is required by this handoff; those strategies remain deferred.

### Priority outcomes
1. State clearly that the reviewed commit is the canonical payload plumbing commit, not a docs-only cleanup.
2. Keep the file list aligned with the reviewed implementation diff and separate any handoff-only artifacts if they are mentioned elsewhere.
3. Do not imply unrelated retrieval tooling scope or `section:` targeting behavior.

### Tasks
1. Route `retrieve_auto()` through the canonical retrieval-service FTS-first payload path.
2. Expose `retrieve_auto_payload()` and `primary_strategy_id()` through the engine retrieval surface.
3. Add focused unit coverage for canonical payload parity and package-export behavior.
4. Complete the handoff metadata required by INTEGRATION.md with concrete scope, file, roadmap, and vision mapping for the reviewed commit.
5. Distinguish the implementation commit from the docs-only cleanup commit so review is anchored to the real code diff.

### Files changed
- Reviewed implementation code:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/tools/retrieval_tools.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Handoff-only artifacts:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`

### Compatibility note
- None.

### Guardrails
- Keep the handoff tied to the retrieval implementation commit and its owned-path file set.
- Preserve commit accuracy between the packet, lane metadata, and handoff artifacts.
- Do not imply unrelated retrieval tooling scope or resolved `section:` targeting.
