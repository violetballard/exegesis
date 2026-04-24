# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Current branch tip before handoff commit: `7372c97fcee7f8a0ab1aea22b25d58bbff0e7eb9`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Scope goal: keep the public excerpt lookup surface on the canonical FTS-only path so non-FTS excerpt IDs fail closed and excerpt provenance stays deterministic.
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required plan-alignment statement: This change makes `retrieve relevant material` more real by keeping excerpt rehydration on the authoritative SQLite FTS path, so PageIndex-only excerpt IDs fail closed and basket-promotion inputs stay deterministic.

## Scope Completed

- Kept the reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` FTS-first by hardening the public `fetch_excerpt` path to resolve through the canonical FTS lookup only.
- Removed the PageIndex fallback from excerpt lookup so PageIndex-only excerpt IDs now fail closed with `KeyError`.
- Preserved deterministic excerpt provenance for canonical FTS lookup hits and kept the shared regression surface limited to `tests/unit/test_unified_retrieval.py`.
- Verified the narrowed fix with the required local gate suite.

## Thread Kickoff

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: remove the non-canonical PageIndex excerpt fallback without widening retrieval scope beyond the canonical FTS-first lane.

### Budget

- Task budget: `8`
- Time budget: `45m`
- Size limits: `<=12 files`, `<=500 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Confirm the current retrieval lane state and run a green baseline test pass.
2. Confirm the reviewed implementation range and isolate the non-canonical `fetch_excerpt` fallback behavior.
3. Patch the canonical retrieval service and approved shared regression coverage for the FTS-only excerpt contract.
4. Re-run the required gates and refresh the writable handoff artifact.

## Tasks Completed

1. Read the required repo control documents, confirmed the lane stayed in owned retrieval paths, and re-ran the focused retrieval unit baseline.
2. Confirmed the reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and isolated the non-canonical PageIndex fallback in `fetch_excerpt`.
3. Updated `src/qual/retrieval/service.py` and the approved shared regression surface `tests/unit/test_unified_retrieval.py` so excerpt lookup now stays on the canonical FTS-only path and PageIndex-only excerpt IDs fail closed.
4. Re-ran `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`, all passing.

## Files Changed

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- `THREAD_PACKET.md`

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
- `retrieve relevant material` now has deterministic FTS-only excerpt rehydration in the reviewed implementation range

### Vision capability affected

- `Retrieval-first context handling`
- deterministic FTS-only excerpt payloads stay structured for downstream basket promotion

### Canonical demo-path step advanced

- `retrieve relevant material`
- `fetch_excerpt` now stays on the canonical FTS-only path in `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`, so excerpt rehydration for this step is deterministic and non-FTS IDs fail closed instead of silently using PageIndex fallback data

### Routing/provider impact note

- None

### Proposed README.md patch text

- None

## Validation Refresh

- Full required gate suite rerun on `2026-04-24`
- Reviewed implementation range for this handoff: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Narrowed diff summary: `2` reviewed implementation files changed, `28` insertions and `31` deletions
