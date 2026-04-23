# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Current submitted tip before this packet refresh commit: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet traceability note: the current branch tip is a packet-refresh commit. Review the narrowed retrieval implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`; later packet-refresh commits remain metadata-only unless this handoff is regenerated.
- Canonical demo-path step advanced: `retrieve relevant material`

## Scope Goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: harden the canonical FTS-only excerpt lookup path and its regression coverage without broadening retrieval scope beyond the narrowed reviewed slice.
- Risk reason: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Restore the packet metadata to the narrowed reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. State explicitly that this slice advances the canonical demo-path step `retrieve relevant material`.
3. Keep the scope summary limited to the FTS-only excerpt lookup change and its approved shared regression coverage.
4. Re-run the required gates and commit the metadata-only reviewer fix.

### Checkpoint Status

- `plan complete`: the handoff metadata is being narrowed back to the reviewer packet's implementation range and canonical demo-path statement.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on this metadata-only refresh.
- `before risky/shared file edit`: this pass edits packet metadata and approved shared-handoff support files only.
- `ready for handoff`: the reviewed range, scope summary, and canonical demo-path mapping all match the reviewer packet.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path in this narrowed slice.
- The reviewed implementation commit removes the PageIndex fallback from `fetch_excerpt`, so the public excerpt lookup surface resolves through the canonical FTS-only path.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs now fail closed with `KeyError`.
- This slice makes the canonical demo-path step `retrieve relevant material` more real by making excerpt lookup fail closed on the canonical FTS-only path while preserving deterministic provenance behavior.

## Reviewed Scope Boundary

- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation files:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Metadata-only handoff files:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`

## Tasks Completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files Changed

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The handoff packet now states explicitly that this narrowed change advances the canonical demo-path step `retrieve relevant material`.
2. The scope statement stays tight: it says this slice hardens `retrieve relevant material` by making excerpt lookup fail closed on the canonical FTS-only path while preserving deterministic provenance behavior.
3. The reviewed range remains narrowed to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains in `tests/unit/test_unified_retrieval.py`.
