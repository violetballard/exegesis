# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Current branch head before this fixer commit: `0118722a6a9d591eae03073c1a438c4e9caf6d4c`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh role: `reviewer-required fix finalization`
- Packet-only commits after reviewed head:
  - `0118722a6a9d591eae03073c1a438c4e9caf6d4c`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output on the canonical retrieval surface.

- This packet carries the reviewer-required high-risk framing and canonical demo-path statement for re-review.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output on the canonical retrieval surface.
- Risk reason: the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so this handoff must satisfy the shared/high-risk packet requirements.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Checkpoint Status

- `plan complete`: narrowed the operative handoff back to the reviewer-requested implementation range and packet scope.
- `first green tests`: all required gates were re-run on the lane branch for this fixer pass.
- `before risky/shared file edit`: no new shared code edit was needed; the only shared implementation file in the reviewed range remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the operative packet now carries the explicit AGENTS demo-path statement and stays tied to the exact two-file implementation slice the reviewer requested.

## Budget classification

- Shared/high-risk handoff under the `4`-task cap because the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Packet-only commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` do not change the reviewed implementation range.

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path on the canonical retrieval surface.
- This reviewed range is intentionally narrow: it removes the PageIndex fallback from `fetch_excerpt` in `src/qual/retrieval/service.py` and adds shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs now fail closed with `KeyError`.
- No broader retrieval facade, payload, or alternate-strategy work is claimed in this packet beyond that narrowed implementation slice.

## Canonical demo-path step advanced

- `retrieve relevant material`
- This reviewed range makes `retrieve relevant material` more real by making excerpt lookup fail closed on the FTS-first engine path, so downstream basket and workflow consumers only receive canonical FTS-backed excerpt payloads.
- This uses the exact MVP-path language from `AGENTS.md` and `ROADMAP.md`, per the reviewer-required handoff fix.
- This packet does not claim completion of basket promotion, workflow actions, or alternate retrieval paths beyond that FTS-first retrieval step.

## Required reviewer fixes addressed

1. Added an explicit AGENTS plan-alignment statement that this lane advances the canonical demo-path step `retrieve relevant material`.
2. Tied that statement to the exact narrowed slice: removing the `fetch_excerpt` PageIndex fallback so excerpt lookup now fails closed on the canonical FTS-first retrieval path.
3. Stated that mapping using the exact MVP-path wording from `AGENTS.md` and `ROADMAP.md`, as requested by the reviewer.
4. Tightened the packet scope to the reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and to the two changed implementation files only.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

- Reviewed implementation files:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Packet-only files after reviewed head:
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
