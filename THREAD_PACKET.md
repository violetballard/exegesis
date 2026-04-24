# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Branch head before handoff commit: `206ee919c0bb7a1736e07a86a5cba5aff314a785`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..206ee919c0bb7a1736e07a86a5cba5aff314a785`
- Scope completed: regenerated the handoff against the actual branch tip so it now truthfully covers the cumulative FTS-first retrieval slice, including the latest `FTSStrategy` hardening that normalizes runner `None` hits to the stable empty-list contract used by fresh and cached engine retrieval paths.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: submit the actual branch tip for review, including the latest FTSStrategy empty-hit normalization and the approved shared regression coverage, without widening beyond the FTS-first retrieval contract.
- Risk reason: the reviewed implementation includes the approved shared regression file `tests/unit/test_unified_retrieval.py`, so this handoff must stay inside the shared/high-risk budget.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Regenerate the handoff packet against the actual branch tip `206ee919c0bb7a1736e07a86a5cba5aff314a785`.
2. Update scope, files-changed, and reviewed-range traceability so the packet matches the real code under review.
3. Add an explicit canonical demo-path statement naming the step this retrieval work advances.
4. Re-run the required local gates and record the results on the real reviewed tip.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Checkpoint Status

- `plan complete`: confirmed the reviewer packet was stale because the actual branch tip includes retrieval code and test changes in `206ee919`.
- `first green tests`: focused retrieval coverage and the full required gate suite were rerun on the actual branch tip after the handoff refresh.
- `before risky/shared file edit`: no new shared code behavior changed in this fixer pass; the reviewed shared surface remains the approved `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the packet now names the actual reviewed implementation head, the full reviewed range, and the canonical demo-path step advanced by the branch-tip behavior.

## Tasks Completed

1. Regenerated the handoff packet against actual branch tip `206ee919c0bb7a1736e07a86a5cba5aff314a785` instead of describing it as metadata-only.
2. Updated the traceability fields so the reviewed implementation range, branch-head role, and files changed all match the real code under review, including `src/qual/engine/retrieval/fts_strategy.py` and `tests/unit/test_unified_retrieval.py`.
3. Added explicit scope for the latest retrieval hardening: `FTSStrategy` now normalizes `None` runner hits to deterministic empty lists on both fresh and cached paths, which keeps the FTS-first engine surface fail-closed and auditable.
4. Added the required canonical demo-path statement: this work makes `retrieve relevant material` more real by keeping excerpt lookup and empty-hit handling on the authoritative SQLite FTS path with deterministic retrieval output for engine consumers.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `docs/gate_passed.txt`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_packet_planner.py`
- `tests/unit/test_unified_retrieval.py`

## Commands Run With Results

- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_fetch_excerpt_requires_an_fts_lookup_hit`: `PASS`
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_auto_provenance_bundle_matches_result_snapshot`: `PASS`
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_fts_source_bundle_matches_result_snapshot`: `PASS`
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_fts_strategy_normalizes_none_runner_hits_to_empty_list`: `PASS`
- `python3 -m unittest tests.unit.test_unified_retrieval`: `PASS`
- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `LOW`
- Blockers: `None`
- Note: unrelated untracked root-level scratch files were present before this pass and were left untouched.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 4: Retrieval Layer`
- `Milestone 3: Product Readiness` via the retrieval evidence/provenance contract preserved by the deterministic FTS-first surface

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Routing/provider impact note

- None

### Canonical demo-path step advanced

- `retrieve relevant material`

### How this handoff makes that step more real

- It keeps excerpt lookup and empty-hit handling on the authoritative SQLite FTS path while preserving deterministic retrieval payloads, provenance, and cache/replay behavior for engine consumers.

### Proposed `README.md` patch text

- None
