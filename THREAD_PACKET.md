# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Reviewer fix note: this packet explicitly maps the retrieval lane to the canonical demo-path step `retrieve relevant material` so the AGENTS handoff remains complete for re-review.
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Scope goal: keep the retrieval lane FTS-first for the MVP by narrowing excerpt lookup hardening to one canonical FTS-only contract on `fetch_excerpt(...)`, `fetch_fts_excerpt(...)`, and `retrieve_fts_excerpt(...)`, plus the approved shared regression coverage for that contract.
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this slice advances `retrieve relevant material` by making `fetch_excerpt(...)` fail closed unless the excerpt is resolvable through the canonical SQLite FTS lookup path that feeds basket promotion and downstream workflow use, so PageIndex is not a required runtime excerpt path for the MVP.

## Scope Completed

- Removed the reintroduced PageIndex fallback from `fetch_excerpt(...)` so the public excerpt lookup surface matches the FTS-first lane gate again.
- Kept PageIndex-only excerpt IDs fail-closed across `fetch_excerpt(...)`, `fetch_fts_excerpt(...)`, and `retrieve_fts_excerpt(...)`.
- Extended the regression to the engine/package facades so imported `fetch_excerpt(...)` helpers fail closed on PageIndex-only excerpt IDs too.
- Regenerated the handoff packet so it describes the reviewed implementation range above instead of a stale metadata-only branch-head story.

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

## Reviewed Implementation Files

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Files Changed In This Fixer Pass

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

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

- `Milestone 3: Product Readiness`

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Canonical demo-path step advanced

- `retrieve relevant material`
- This slice advances that step by making `fetch_excerpt(...)` and its public facades fail closed unless the excerpt resolves through the canonical SQLite FTS path used before basket promotion, so PageIndex-only excerpt IDs are not a required runtime MVP path.

### Routing/provider impact note

- None

### Proposed README.md patch text

- None
