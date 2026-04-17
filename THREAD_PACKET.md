# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-required metadata-only fixer pass`
- Current packet-refresh branch head before this fixer commit: `69dd2bc3ddc7c3c3e58d8162be7d75281d612408`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: Keep the FTS-first retrieval lane scoped to deterministic excerpt and provenance output on the canonical engine retrieval surface.
- Risk reason: the reviewed implementation includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Checkpoint Status

- `plan complete`: the packet is reissued against the reviewer packet's source-of-truth implementation range and explicitly names the canonical demo-path step advanced.
- `first green tests`: all required gates were rerun on this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in scope remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the handoff stays anchored to the reviewed implementation range above and keeps the packet refresh separate from that implementation slice.

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path in this reviewed slice.
- The reviewed implementation removes the PageIndex fallback from `fetch_excerpt` in `src/qual/retrieval/service.py`, so public excerpt lookup now resolves only through the canonical FTS-backed path.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs now fail closed with `KeyError`.
- PageIndex and embeddings remain compatibility paths in this slice and are not required runtime paths for the MVP contract.

## Canonical Demo-Path Step Advanced

- Canonical demo-path step advanced: `retrieve relevant material`

This handoff explicitly advances the canonical demo-path step `retrieve relevant material`. It does so by keeping public excerpt lookup on the FTS-only retrieval contract and by preserving deterministic, auditable excerpt behavior for downstream basket promotion and workflow use.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

- Reviewed implementation files:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Packet refresh files:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / blockers

- Risk: `HIGH`
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval file in the reviewed implementation range.
