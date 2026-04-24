# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Current branch tip before this handoff refresh commit: `748004b1f28f30b1f662718ffc2d8c6960ebafe8`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Scope goal: keep the retrieval lane FTS-first for the MVP by enforcing the FTS-only excerpt contract on `retrieve_fts_excerpt` / `fetch_fts_excerpt` while preserving generic `fetch_excerpt(...)` PageIndex compatibility.
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required plan-alignment statement: This narrowed slice makes `retrieve relevant material` more real by keeping the canonical FTS excerpt entrypoints fail-closed on the SQLite FTS path used before basket promotion, without tightening the broader `fetch_excerpt(...)` compatibility surface.

## Scope Completed

- Restored the broader `fetch_excerpt(...)` compatibility surface so PageIndex-only excerpt IDs still resolve for legacy callers.
- Kept the canonical `retrieve_fts_excerpt(...)` / `fetch_fts_excerpt(...)` entrypoints fail-closed on PageIndex-only excerpt IDs so the FTS-only contract remains isolated to the existing FTS-specific APIs.
- Kept the reviewed scope narrowed to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`; this packet does not claim the full retrieval MVP is complete.
- Re-ran the required gate suite on the current packet-refresh branch head without changing the reviewed implementation head.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct the reviewer-requested implementation so the FTS-only excerpt contract stays on the canonical FTS-specific APIs and the handoff names the canonical demo-path step explicitly.
- Risk reason: this reviewed slice includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Restore generic `fetch_excerpt(...)` compatibility for PageIndex-only excerpt IDs.
2. Keep fail-closed coverage focused on `retrieve_fts_excerpt(...)` and `fetch_fts_excerpt(...)`.
3. Update the packet so it states the canonical demo-path step this slice advances and why.
4. Re-run the required gates and record the results on the current branch head.

## Tasks Completed

1. Restored `fetch_excerpt(...)` PageIndex compatibility so the generic excerpt lookup surface no longer fails closed on PageIndex-only IDs.
2. Revised the regression coverage to keep fail-closed behavior on `retrieve_fts_excerpt(...)` and `fetch_fts_excerpt(...)`, which are the canonical FTS-specific excerpt APIs.
3. Updated the handoff packet to state explicitly that this slice advances the canonical `retrieve relevant material` step by making the FTS-only excerpt path more deterministic before basket promotion without introducing a broader public-interface tightening.
4. Re-ran `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`, all passing on the current branch head.

## Files Changed

- Fixer pass for this review response:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `HIGH`
- Blockers: `None`

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`
- The narrowed slice makes the canonical `retrieve relevant material` step more real by keeping the FTS-specific excerpt lookup path deterministic before basket promotion while preserving generic compatibility for legacy `fetch_excerpt(...)` callers.

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Canonical demo-path step advanced

- `retrieve relevant material`
- This slice advances that step by keeping the canonical FTS-specific excerpt entrypoints deterministic on the FTS-first retrieval path used before basket promotion without breaking the broader compatibility surface.

### Routing/provider impact note

- None

### Proposed README.md patch text

- None

## Validation Refresh

- Full required gate suite rerun on `2026-04-24`
- Reviewed implementation range for this handoff: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Current branch head at validation time: `748004b1f28f30b1f662718ffc2d8c6960ebafe8`
- This fixer pass updates the implementation and packet together while keeping the reviewed implementation range above as the change under re-review.
