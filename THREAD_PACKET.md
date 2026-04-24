# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Reviewed implementation head: `reported from final branch HEAD after commit`
- Reviewed implementation range: `current fix pass on branch tip`
- Scope goal: keep the retrieval lane FTS-first for the MVP by making the engine-side `FTSStrategy` fail closed unless the incoming payload is a canonical FTS-first retrieval query.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice advances `retrieve relevant material` by keeping routing and cache eligibility aligned with the active SQLite FTS contract, so malformed query text or unsupported retrieval metadata cannot be treated as valid retrieval work on the engine path.

## Scope Completed

- Tightened `src/qual/engine/retrieval/fts_strategy.py` so `supports(...)` now requires canonical query text, supported scope, supported intent, and supported confidentiality profile instead of checking scope alone.
- Kept `retrieve(...)` aligned with the same guard so malformed mapping-shaped payloads fail closed before the runner/cache path executes.
- Preserved the FTS-first MVP contract: SQLite FTS remains the only active retrieval strategy, while PageIndex and embeddings stay deferred outside the engine retrieval path.
- Refreshed this handoff packet so the INTEGRATION-required fields describe the current retrieval-lane work and verification results.

## Thread Kickoff

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: tighten engine-side FTS query support checks so only canonical FTS-first retrieval payloads are considered supported.

### Budget

- Task budget: `8`
- Time budget: `45m`
- Size limits: `<=12 files`, `<=500 net LOC`
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Tightened `FTSStrategy.supports(...)` so only canonical FTS-first query payloads are reported as supported.
2. Aligned `FTSStrategy.retrieve(...)` with the same guard so malformed query payloads fail closed before the runner/cache path executes.
3. Verified the new guard directly with an ad hoc Python probe for blank query text, unsupported intent, and valid FTS payload behavior.
4. Re-ran the retrieval suite and the full required gate suite and recorded the results for this handoff.

## Files Changed

- `src/qual/engine/retrieval/fts_strategy.py`
- `THREAD_PACKET.md`

## Commands Run With Results

- `python -m unittest tests.unit.test_unified_retrieval -q`: `PASS`
- `python - <<'PY' ... FTSStrategy probe ... PY`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `LOW`
- Blockers: `None`
- Metadata note: the implementation change stayed inside retrieval-owned code; the only non-lane file touched in this pass is this handoff packet because the lane prompt requires the INTEGRATION handoff fields to be refreshed.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Product Readiness`
- `Milestone 4: Retrieval Layer`

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Canonical demo-path step advanced

- `retrieve relevant material`
- This slice advances that step by making the engine-side FTS strategy fail closed unless the query payload is canonical for the active SQLite FTS path, which keeps retrieval routing and caching aligned with the auditable MVP contract.

### Routing/provider impact note

- None

### Proposed README.md patch text

- None
