# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Current branch tip before handoff commit: `6ed15b42efa484dc7d0db8e3f2c37fdb8a34eb35`
- Scope goal: keep failed direct excerpt lookup audits schema-aligned with the canonical FTS-first retrieval contract so audit consumers can treat success and failure paths uniformly.

## Scope Completed

- Kept the retrieval lane FTS-first by hardening `src/qual/retrieval/service.py` only.
- Expanded failed direct excerpt lookup audits to emit the same top-level metadata shape used by successful excerpt lookup audits, with explicit null or empty placeholders for unavailable fields.
- Preserved the canonical FTS lookup fingerprint and `strategies_used=["fts"]` semantics while removing schema drift for audit consumers that inspect lookup provenance and basket-promotion-adjacent fields.
- Verified the change with a targeted Python probe plus the full required local gate suite.

## Thread Kickoff

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: tighten failed excerpt lookup audit metadata without widening retrieval scope beyond the canonical FTS-first lane.

### Budget

- Task budget: `8`
- Time budget: `45m`
- Size limits: `<=12 files`, `<=500 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Confirm the current retrieval lane state and run a green baseline test pass.
2. Identify a retrieval-owned determinism or auditability gap in the direct excerpt lookup path.
3. Patch the canonical retrieval service inside lane-owned code only.
4. Re-run the required gates and refresh the writable handoff artifact.

## Tasks Completed

1. Read the required repo control documents, confirmed the lane stayed in owned retrieval paths, and re-ran the focused retrieval unit baseline.
2. Confirmed the current head already recorded failed excerpt lookups as FTS attempts, then identified remaining schema drift between success and failure audit payloads in the same lookup path.
3. Updated `src/qual/retrieval/service.py` so `excerpt_lookup_failed` emits the full aligned top-level audit shape with explicit null or empty placeholders for unavailable lookup context.
4. Re-ran `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`, all passing.

## Files Changed

- `src/qual/retrieval/service.py`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `python -m unittest tests.unit.test_unified_retrieval`: `PASS`
- `python3 - <<'PY' ... service.retrieve_fts_excerpt("missing-excerpt") ... PY`: `PASS`; the recorded `excerpt_lookup_failed` audit event now includes aligned null or empty metadata fields plus `strategies_used=['fts']`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `LOW`
- Blockers: `None`

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Product Readiness`
- `Milestone 4: Retrieval Layer`

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable generation`

### Canonical demo-path step advanced

- `retrieve relevant material`
- failed excerpt lookups now stay schema-aligned with successful FTS excerpt lookups, which reduces audit special-casing for basket promotion and later revise/apply flows when excerpt rehydration fails

### Routing/provider impact note

- None

### Proposed README.md patch text

- None

## Validation Refresh

- Full required gate suite rerun on `2026-04-24`
- Net code delta: `1` retrieval-owned file changed, `+30/-0` in `src/qual/retrieval/service.py`
