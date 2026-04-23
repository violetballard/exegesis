# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix refresh`
- Current submitted tip before this packet refresh commit: `c461c2ad96f9253c6d710373d7038bf634802e70`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet traceability note: review this lane against the narrowed implementation range above. Later packet-refresh commits after `adfa8cda`, including `c461c2ad96f9253c6d710373d7038bf634802e70`, are metadata-only and do not broaden retrieval scope.
- Canonical demo-path step advanced: `retrieve relevant material`

## Scope Goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt, provenance, and payload output.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: preserve the narrowed FTS-first retrieval implementation handoff and refresh packet metadata truthfully without widening scope beyond `378cf9a7..adfa8cda`.
- Risk reason: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Correct the packet traceability so the reviewed implementation head/range stay anchored to `adfa8cda` and `378cf9a7..adfa8cda`.
2. Correct the metadata-only handoff file accounting for commit `c461c2ad96f9253c6d710373d7038bf634802e70`.
3. State explicitly that this handoff advances the canonical demo-path step `retrieve relevant material` by making retrieval deterministic and auditable for downstream basket/workflow use.
4. Re-run the required gates and record results against the narrowed reviewed implementation range.

### Checkpoint Status

- `plan complete`: the packet is being corrected back to the approved `378cf9a7..adfa8cda` review slice.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- `before risky/shared file edit`: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the authoritative packet and gate summary agree on the same narrowed reviewed range, exact metadata-only file list for `c461c2ad`, demo-path step, and gate results; `.codex` mirrors remain stale because writes there are blocked in this environment.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path across the reviewed implementation range.
- The excerpt lookup surface is FTS-only and fails closed for PageIndex-only excerpt IDs under approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- This handoff advances the canonical demo-path step `retrieve relevant material` by making excerpt lookup and retrieval provenance deterministic and auditable for downstream basket/workflow use.

## Reviewed Scope Boundary

- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation files:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Metadata-only handoff files in commit `c461c2ad96f9253c6d710373d7038bf634802e70`:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Tasks Completed

1. Removed the PageIndex excerpt fallback so excerpt lookup now stays on the canonical FTS path.
2. Added fail-closed shared regression coverage for PageIndex-only excerpt IDs in `tests/unit/test_unified_retrieval.py`.
3. Preserved the narrowed review boundary at `378cf9a7..adfa8cda` instead of broadening the packet back toward later retrieval or alternate-mode work.
4. Refreshed the handoff metadata so commit `c461c2ad` and this fixer pass both report truthful packet-only file changes.

## Files Changed

- Current fixer-pass metadata files:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`
- Reviewed implementation files in `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Metadata-only handoff files in cited refresh commit `c461c2ad96f9253c6d710373d7038bf634802e70`:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The packet no longer broadens review to branch tip `850eacce`; it stays anchored to reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. The cited metadata-only refresh commit `c461c2ad96f9253c6d710373d7038bf634802e70` now has truthful file accounting: only `THREAD_PACKET.md` and `docs/gate_passed.txt`.
3. The handoff explicitly names canonical demo-path step `retrieve relevant material` and states that deterministic, auditable FTS-only excerpt lookup is the plan-alignment reason.
4. The reviewed implementation scope remains narrowed and does not reintroduce PageIndex compatibility work or alternate retrieval modes.

## Risks / Blockers

- Risk: `MEDIUM`
- Blocker: writes under `.codex/` are rejected with `Operation not permitted`, so mirrored kickoff/lane-meta packet artifacts remain stale.

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
