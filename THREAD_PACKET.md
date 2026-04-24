# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Scope goal: keep the retrieval lane FTS-first for the MVP by enforcing one canonical FTS-only excerpt contract on `fetch_excerpt(...)`, `fetch_fts_excerpt(...)`, and `retrieve_fts_excerpt(...)`.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this fix pass makes `retrieve relevant material` more real by ensuring excerpt lookup fails closed unless the excerpt came from the SQLite FTS path that feeds basket promotion and downstream workflow use.

## Scope Completed

- Removed the reintroduced PageIndex fallback from `fetch_excerpt(...)` so the public excerpt lookup surface matches the FTS-first lane gate again.
- Kept PageIndex-only excerpt IDs fail-closed across `fetch_excerpt(...)`, `fetch_fts_excerpt(...)`, and `retrieve_fts_excerpt(...)`.
- Extended the regression to the engine/package facades so imported `fetch_excerpt(...)` helpers fail closed on PageIndex-only excerpt IDs too.
- Regenerated the handoff packet so it describes the current branch-tip retrieval behavior instead of a stale metadata-only branch-head story.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: restore one FTS-only excerpt contract and repair handoff traceability for re-review.
- Risk reason: this fix pass updates approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Removed the generic PageIndex compatibility fallback from `fetch_excerpt(...)`.
2. Updated shared regression coverage so PageIndex-only excerpt IDs fail closed on every public excerpt lookup surface.
3. Added facade-level coverage so engine/package `fetch_excerpt(...)` imports enforce the same fail-closed FTS-only contract.
4. Re-ran the required gate suite and recorded the results for this handoff.

## Files Changed

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- `THREAD_PACKET.md`

## Commands Run With Results

- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_fetch_excerpt_requires_an_fts_lookup_hit -v`: `PASS`
- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `LOW`
- Blockers: `None`
- Metadata note: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are read-only in this worktree sandbox, so the refreshed writable handoff for this fixer pass is recorded in `THREAD_PACKET.md`.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 4: Retrieval Layer`
- `Milestone 3: Product Readiness`

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Canonical demo-path step advanced

- `retrieve relevant material`
- This slice advances that step by keeping excerpt resolution auditable and deterministic on the canonical SQLite FTS path used before basket promotion.

### Routing/provider impact note

- None

### Proposed README.md patch text

- None
