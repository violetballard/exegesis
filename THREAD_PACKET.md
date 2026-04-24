# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `feature lane handoff`
- Current branch tip before this handoff refresh commit: `81e954da3f89e7b47b3adb3560d476fef87fdcba`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Scope goal: keep the retrieval lane FTS-first for the MVP by removing the non-canonical `fetch_excerpt` PageIndex fallback and preserving deterministic excerpt provenance on the SQLite FTS path used before basket promotion.
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required plan-alignment statement: This narrowed slice makes `retrieve relevant material` more real by removing the `fetch_excerpt` PageIndex fallback, which keeps excerpt provenance deterministic on the FTS-first retrieval path used before basket promotion.
- AGENTS-required canonical step mapping: The concrete Milestone 3 step advanced by this handoff is `retrieve relevant material`, specifically through the FTS-only `fetch_excerpt` behavior in the reviewed slice above.

## Scope Completed

- Removed the non-canonical PageIndex fallback from `fetch_excerpt(...)` so excerpt lookup now resolves through the authoritative SQLite FTS path only.
- Preserved deterministic excerpt provenance on the FTS-first retrieval flow used before basket promotion by failing closed when callers present PageIndex-only excerpt IDs.
- Kept the reviewed scope narrowed to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`; this packet does not claim the full retrieval MVP is complete.
- Re-ran the required gate suite on the current packet-refresh branch head without changing the reviewed implementation head.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct the reviewer-facing handoff so it stays narrowed to the approved FTS-only excerpt fail-closed slice at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Risk reason: this reviewed slice includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Confirm the reviewer-required reviewed implementation head and narrowed reviewed range.
2. Rewrite the handoff so it explicitly names the canonical demo-path step advanced by this slice.
3. Tie that step mapping directly to the `fetch_excerpt` PageIndex fallback removal and deterministic FTS provenance before basket promotion.
4. Re-run the required gates and record the results on the current packet-refresh branch head.

## Tasks Completed

1. Confirmed the reviewed implementation head remains `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and the corrected reviewed implementation range for this resubmission is `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. Regenerated the handoff so it now states explicitly that this slice advances `retrieve relevant material`.
3. Tied that statement to the exact narrowed behavior change: removing the `fetch_excerpt` PageIndex fallback keeps excerpt provenance deterministic on the FTS-first retrieval path used before basket promotion.
4. Re-ran `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`, all passing on the current packet-refresh branch head.

## Files Changed

- Metadata-only fixer pass for this handoff refresh:
- `THREAD_PACKET.md`
- Reviewed implementation files in `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:
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
- The narrowed slice makes the canonical `retrieve relevant material` step more real by keeping excerpt lookup deterministic on the FTS-first path.

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Canonical demo-path step advanced

- `retrieve relevant material`
- This slice advances that step by removing the `fetch_excerpt` PageIndex fallback so excerpt provenance stays deterministic on the FTS-first retrieval path used before basket promotion.

### Routing/provider impact note

- None

### Proposed README.md patch text

- None

## Reviewer Fix Closure

1. The handoff now includes the explicit line `Canonical demo-path step advanced: retrieve relevant material`.
2. That line is tied directly to the exact narrowed slice under review: removing the `fetch_excerpt` PageIndex fallback makes excerpt provenance deterministic on the FTS-first retrieval path used before basket promotion.
3. The packet keeps its scope wording narrowed to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and does not claim the entire retrieval MVP is complete.

## Validation Refresh

- Full required gate suite rerun on `2026-04-24`
- Reviewed implementation range for this handoff: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Current packet-refresh branch head at validation time: `81e954da3f89e7b47b3adb3560d476fef87fdcba`
- This fixer pass is metadata-only and does not change the reviewed implementation head or reviewed implementation range above.
- Validation evidence on that branch head: `quality-test.sh` passed `tests/smoke.sh` and `216` unit tests, `typecheck-test.sh` passed `python3 -m compileall -q src`, and `make ci` completed successfully.
