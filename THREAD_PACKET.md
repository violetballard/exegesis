# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Packet refresh trace anchor before this fixer commit: `6c4a28c2cb158e3fbe812021c9f547d85fa56ee1`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this reviewed implementation advances `retrieve relevant material` by keeping excerpt provenance lookup deterministic on the FTS-only path and preventing PageIndex-only excerpt IDs from acting like an MVP retrieval path.
- Traceability note: review this lane against the reviewed implementation range above. This fixer pass is metadata-only and does not broaden retrieval scope beyond `378cf9a7..adfa8cda`.

## Scope Goal

- Correct the reviewer-facing handoff packet so it matches the narrowed reviewed implementation slice anchored at `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and the actual metadata-only packet refresh files touched by this fixer pass.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path in the reviewed slice.
- `fetch_excerpt` now resolves through the canonical FTS-only path instead of falling back to PageIndex for excerpt lookup.
- Approved shared regression coverage proves that PageIndex-only excerpt IDs fail closed with `KeyError`.
- PageIndex and embeddings remain compatibility-only paths in this slice rather than required MVP retrieval modes.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct the reviewer-facing metadata so it truthfully describes the narrowed retrieval implementation slice ending at `adfa8cda` and the exact current packet-refresh files.
- Risk reason: this lane includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the handoff stays on the high-risk/shared 4-task basis.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Restamp the reviewed implementation range to the narrowed slice `378cf9a7..adfa8cda`.
2. Keep the packet’s completed scope limited to the FTS-only excerpt lookup change and the approved shared regression coverage that verifies fail-closed behavior.
3. State explicitly that this advances the canonical demo-path step `retrieve relevant material`.
4. Refresh the visible metadata-only packet surfaces and rerun the required gates.

## Tasks Completed

1. Restamped the handoff to reviewed implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. Corrected `Scope completed` and `Files changed` so they match the narrowed reviewer-approved slice: the FTS-only excerpt lookup change in `src/qual/retrieval/service.py` and the approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
3. Added the explicit canonical demo-path mapping sentence for `retrieve relevant material`, tied to deterministic excerpt provenance lookup on the FTS-only path.
4. Refreshed the visible metadata-only packet surfaces and reran the required local gates.

## Files Changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py` (approved shared regression coverage)

### Current metadata-only packet refresh files

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

1. The `Files changed` section now matches the narrowed reviewed implementation slice plus the actual metadata-only refresh files touched by this fixer pass.
2. The handoff now includes an explicit canonical demo-path statement naming `retrieve relevant material`.
3. The metadata-only refresh list no longer includes uncited files that were not touched by the current packet-refresh commit.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts - authoritative FTS-first retrieval feeding the engine loop`

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
