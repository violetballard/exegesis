# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Packet refresh trace anchor before this fixer commit: `ed0995f552723203222f938fe2b4c07b76c1929d`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this reviewed implementation advances `retrieve relevant material` by keeping excerpt provenance lookup deterministic on the FTS-only path and preventing PageIndex-only excerpt IDs from acting like an MVP retrieval path.
- Traceability note: review this lane against the reviewed implementation range above. This fixer pass is metadata-only and does not broaden retrieval scope beyond `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Scope Goal

- Correct the reviewer-facing handoff packet so it matches the narrowed reviewed implementation slice anchored at `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and the actual metadata-only packet refresh files touched by this fixer pass.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path in the reviewed slice.
- `fetch_excerpt` now resolves through the canonical FTS-only path instead of falling back to PageIndex for excerpt lookup.
- Approved shared regression coverage proves that PageIndex-only excerpt IDs fail closed with `KeyError`.
- PageIndex and embeddings remain compatibility-only paths in this slice rather than required MVP retrieval modes.
- Existing broader retrieval normalization and helper surfaces predate this narrowed slice and are outside `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

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

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

### Handoff Packet

- branch name
- tasks completed (numbered)
- files changed
- commands run + outcomes
- risks/blockers
- all required fields from `INTEGRATION.md`

## Tasks Completed

1. Restamped the handoff to reviewed implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. Corrected `Scope completed` and `Files changed` so they match the narrowed reviewer-approved slice: the FTS-only excerpt lookup change in `src/qual/retrieval/service.py` and the approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
3. Added the explicit canonical demo-path mapping sentence for `retrieve relevant material`, tied to deterministic excerpt provenance lookup on the FTS-only path.
4. Marked broader retrieval normalization/helper surfaces as pre-existing context outside this reviewed implementation range and refreshed the visible packet surfaces.

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
- Final verification note: required gates were rerun on the packet-only finalization state on `2026-04-24` before this fixer handoff commit.

## Reviewer Fix Closure

1. The `Files changed` section now matches the narrowed reviewed implementation slice plus the actual metadata-only refresh files touched by this fixer pass.
2. The handoff now includes an explicit canonical demo-path statement naming `retrieve relevant material` and tying it to deterministic FTS-only excerpt provenance lookup.
3. The handoff now carries the missing AGENTS high-risk sections for early review triggers, stop triggers, checkpoint cadence, and the explicit handoff packet fields.
4. The metadata-only refresh list now matches the packet files restamped in this fixer pass.
5. The demo-path mapping is tied directly to the narrowed change: `fetch_excerpt` now fails closed to the canonical FTS lookup path, keeping excerpt provenance deterministic and auditable for `retrieve relevant material`.
6. Broader retrieval normalization and helper surfaces are explicitly treated as pre-existing context outside this reviewed implementation range.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts - authoritative FTS-first retrieval feeding the engine loop`

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable generation`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
