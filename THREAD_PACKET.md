# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Branch head before handoff commit: `49729c7378ebe7d69e3c852559febe4f3d25b02f`
- Scope completed: hardened the FTS-first strategy cache so fresh and cached retrieval runs always surface a stable list-shaped hit snapshot even when the runner returns tuples or other iterables.

## Thread Kickoff

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: keep the retrieval lane narrowly focused on deterministic, auditable FTS-first engine behavior without widening beyond the canonical retrieval package.

### Budget

- Task budget: `8`
- Time budget: `45m`
- Size limits: `<=12 files`, `<=500 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Inspect the active retrieval lane code and confirm the next owned-path hardening target.
2. Implement a narrow FTS-first determinism fix in the retrieval strategy surface.
3. Re-run focused retrieval verification and the required gate suite.
4. Refresh the handoff packet with the current lane state and required integration fields.

### Checkpoint Status

- `plan complete`: confirmed the lane stayed in retrieval-owned paths and targeted `FTSStrategy`.
- `first green tests`: `python -m unittest tests.unit.test_unified_retrieval` passed after the change.
- `before risky/shared file edit`: not applicable; this pass did not edit shared or integrator-locked files.
- `ready for handoff`: required local gates are green and the handoff packet reflects the current retrieval hardening pass.

## Tasks Completed

1. Normalized `FTSStrategy` runner output into a defensive list snapshot before caching or returning hits, so tuple/generator-style outputs cannot leak container shape or mutable aliasing into engine retrieval flows.
2. Preserved the existing FTS-first cache-key semantics and cache invalidation behavior while tightening the `StrategyRun.hits` contract to the documented list shape.
3. Verified the change with the focused retrieval unit suite, an ad hoc tuple/generator sanity check, and the full required gate sequence.

## Files Changed

- `src/qual/engine/retrieval/fts_strategy.py`
- `THREAD_PACKET.md`

## Commands Run With Results

- `python -m unittest tests.unit.test_unified_retrieval`: `PASS`
- ad hoc `python` sanity check for tuple/generator runner outputs: `PASS`
- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `LOW`
- Blockers: `None`
- Note: unrelated untracked root-level files were present before this pass and were left untouched.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 4: Retrieval Layer`
- `Milestone 3: Product Readiness` via a narrower deterministic retrieval contract at the engine-facing strategy surface

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None
