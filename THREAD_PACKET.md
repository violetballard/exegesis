# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `truthful branch-tip handoff refresh`
- Current submitted tip before this packet refresh commit: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh commit: `118c4f1dd0e008f5bf084678a0ffe00c091a1966`
- Packet traceability note: the reviewed implementation remains narrowed to the reviewer-approved range above. The packet refresh commit only updates `THREAD_PACKET.md` and `docs/gate_passed.txt`; it does not broaden implementation scope beyond `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Canonical demo-path step advanced: `retrieve relevant material`

## Scope Goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt, provenance, and payload output.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: hand off the reviewer-approved FTS-only excerpt lookup slice with truthful traceability and no metadata drift.
- Risk reason: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Correct the packet refresh traceability so it points at the reviewer-approved implementation head `adfa8cda` and range `378cf9a7..adfa8cda`.
2. Keep the metadata-only file accounting exact for packet refresh commit `118c4f1d`.
3. State explicitly that this narrowed retrieval fix advances the canonical demo-path step `retrieve relevant material`.
4. Re-run the required gates and record files changed plus command results against the corrected reviewed range.

### Checkpoint Status

- `plan complete`: the packet is being corrected back to the reviewer-approved narrowed implementation slice instead of the broadened branch tip.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on the corrected packet state.
- `before risky/shared file edit`: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the authoritative packet and gate summary agree on the same narrowed reviewed range, demo-path step, exact packet-refresh file list, and gate results.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path across the reviewed slice.
- `src/qual/retrieval/service.py` removes the PageIndex fallback from excerpt lookup so excerpt resolution stays FTS-only and fail-closed for non-FTS IDs.
- `tests/unit/test_unified_retrieval.py` locks in the fail-closed behavior for PageIndex-only excerpt IDs under the approved shared regression exception.
- This handoff advances the canonical demo-path step `retrieve relevant material` by making the retrieval contract deterministic and auditable for downstream basket and workflow use.

## Reviewed Scope Boundary

- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation files:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Packet refresh files for commit `118c4f1dd0e008f5bf084678a0ffe00c091a1966`:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Tasks Completed

1. Kept excerpt lookup narrowed to the reviewer-approved FTS-only behavior in `src/qual/retrieval/service.py` without broadening back toward PageIndex compatibility or alternate retrieval modes.
2. Kept approved shared regression coverage in `tests/unit/test_unified_retrieval.py` focused on fail-closed behavior for PageIndex-only excerpt IDs.
3. Corrected packet refresh traceability so commit `118c4f1d` accounts only for `THREAD_PACKET.md` and `docs/gate_passed.txt`.
4. Added an explicit plan-alignment statement naming `retrieve relevant material` as the canonical demo-path step advanced by this work.

## Files Changed

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

## Reviewer Fix Closure

1. The handoff points review back to the reviewer-approved implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. The packet refresh commit `118c4f1dd0e008f5bf084678a0ffe00c091a1966` now has truthful metadata-only file accounting: `THREAD_PACKET.md` and `docs/gate_passed.txt` only.
3. The packet explicitly states that this narrowed retrieval fix advances the canonical demo-path step `retrieve relevant material` by making retrieval deterministic and auditable for downstream basket and workflow use.
4. The reviewed scope remains narrowed and does not broaden back toward PageIndex compatibility work or alternate retrieval modes.

## Risks / Blockers

- Risk: `HIGH`
- Blocker: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains in `tests/unit/test_unified_retrieval.py`.
