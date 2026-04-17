# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-required fix finalization`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh commit before this fixer commit: `70c83fbf82ac53e79e62d2095f0d3c24df7ee892`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.
- Risk reason: the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Checkpoint Status

- `plan complete`: narrowed all reviewer-facing metadata to the same implementation slice and added the explicit AGENTS demo-path statement.
- `first green tests`: all required gates were re-run on the lane branch for this fixer pass.
- `before risky/shared file edit`: no new shared code edit was needed; the only shared implementation file in the reviewed range remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the operative handoff packet carries the narrowed scope and canonical demo-path statement required for re-review.

## Budget classification

- Shared/high-risk handoff under the `4`-task cap because the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Packet-only metadata after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` does not change the reviewed implementation range.

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path on the canonical retrieval surface.
- This reviewed range is intentionally narrow: it removes the PageIndex fallback from `fetch_excerpt` in `src/qual/retrieval/service.py` and adds shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs now fail closed with `KeyError`.
- No broader retrieval facade, payload, or alternate-strategy work is claimed in this packet beyond that narrowed implementation slice.

## Canonical demo-path step advanced

- `retrieve relevant material`

This reviewed range makes `retrieve relevant material` more real by removing the `fetch_excerpt` PageIndex fallback, so the canonical retrieval surface now fails closed on the FTS-first path and downstream basket-promotion consumers only receive canonical FTS-backed excerpt payloads.

## Required reviewer fixes addressed

1. Added an explicit AGENTS plan-alignment statement naming the canonical demo-path step this work advances: `retrieve relevant material`.
2. Tied that statement to the narrowed diff by stating that removing the `fetch_excerpt` PageIndex fallback makes the canonical retrieval path strictly FTS-first, deterministic, and auditable for downstream basket promotion.
3. Kept the packet scope narrowed to the reviewer-specified implementation commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

- Reviewed implementation files:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Packet refresh files:
  - `THREAD_PACKET.md`

## Packet mirror note

- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` remain read-only in this lane sandbox.
- `THREAD_PACKET.md` is the operative handoff packet for this fixer pass and carries the reviewer-required shared/high-risk classification plus the explicit canonical demo-path step advanced by the narrowed retrieval slice.
- Re-review should use this packet as the source of truth for plan alignment and budget classification on the current branch tip.

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
