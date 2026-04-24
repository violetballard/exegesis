# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Current branch tip before handoff commit: `152cb4f1c5435250d5e3e31fe9054a93fe5efeb1`
- Scope goal: keep direct excerpt lookup audits aligned with the canonical FTS-first retrieval contract so failed lookups remain explicitly auditable as FTS attempts.

## Scope Completed

- Kept the retrieval lane FTS-first by hardening `src/qual/retrieval/service.py` only.
- Changed failed direct excerpt lookup audits to record `strategies_used=["fts"]` instead of an empty strategy list.
- Preserved the canonical lookup fingerprint path while making failure audits match the same authoritative FTS routing contract used by successful excerpt lookups.
- Verified the change with a targeted Python probe and the full required local gate suite.

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

1. Read the required repo control documents and verified the lane stayed in owned retrieval paths.
2. Re-ran `./quality-test.sh` as a baseline and used a targeted local probe to confirm failed excerpt lookup audits emitted `strategies_used=[]`.
3. Updated `src/qual/retrieval/service.py` so failed direct excerpt lookups now fingerprint and audit as explicit FTS attempts.
4. Re-ran `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`, all passing.

## Files Changed

- `src/qual/retrieval/service.py`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `python3 - <<'PY' ... retrieve_fts_excerpt('missing-excerpt') ... PY`: `PASS` before and after patch; after the change the recorded audit metadata reports `strategies_used=['fts']`.
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
- Failed excerpt lookups now remain explicitly attributable to the canonical FTS path, which makes downstream basket promotion and later revise/apply flows easier to audit when a quoted excerpt cannot be rehydrated.

### Routing/provider impact note

- None

### Proposed README.md patch text

- None

## Validation Refresh

- Full required gate suite rerun on `2026-04-24T02:05:31 PDT`
- Net code delta: `1` retrieval-owned file changed, `+5/-1` in `src/qual/retrieval/service.py`
