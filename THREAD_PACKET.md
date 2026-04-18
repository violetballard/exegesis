# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix packet regeneration`
- Current branch tip before this fixer pass: `9afb6edbdd87`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet-only descendants above the reviewed implementation head: metadata-only packet refresh commits; final HEAD SHA is reported with the fixer handoff
- Packet traceability note: use the reviewer packet as the source of truth for scope. This handoff stays narrowed to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and does not broaden the reviewed retrieval implementation range.

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: keep excerpt lookup on the canonical SQLite FTS path and preserve deterministic provenance output for downstream engine flows.
- Risk reason: the submitted scope includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep excerpt lookup fail-closed on the canonical FTS path.
2. Preserve deterministic excerpt and provenance payload output.
3. Maintain approved shared regression coverage for the FTS-only excerpt contract.
4. Regenerate the handoff packet so it explicitly states the canonical demo-path step advanced by this narrowed change.

### Checkpoint Status

- `plan complete`: the packet is narrowed to the reviewer-specified implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- `first green tests`: recorded after rerunning the required gates for this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in scope remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the packet now states explicitly which canonical demo-path step this change advances and keeps scope narrowed to the reviewer packet.

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path in this narrowed slice.
- The reviewed implementation commit makes excerpt lookup fail closed on the canonical FTS-only path by removing the PageIndex fallback from `fetch_excerpt`.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs now raise `KeyError`.
- PageIndex and embeddings remain non-required compatibility paths in this slice; excerpt lookup no longer promotes PageIndex as a runtime fallback path for the MVP contract.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This handoff advances `retrieve relevant material` by making `fetch_excerpt()` fail closed on canonical SQLite FTS hits, which keeps downstream basket promotion and audit provenance tied to deterministic FTS-backed excerpt payloads.

## Tasks completed

1. `src/qual/retrieval/service.py` now makes `fetch_excerpt()` resolve through the canonical FTS-only path instead of falling back to PageIndex.
2. `tests/unit/test_unified_retrieval.py` adds approved shared regression coverage proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

- Reviewed implementation files:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Metadata-only handoff file:
  - `THREAD_PACKET.md`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. The packet now states explicitly which canonical demo-path step this change advances.
2. That statement is tied to the narrowed scope: this change strengthens `retrieve relevant material` by making `fetch_excerpt()` fail closed on canonical SQLite FTS hits and preserving deterministic provenance payloads.
3. The reviewed scope remains narrowed to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and is not broadened by this fixer pass.
4. This handoff packet is the writable source of truth for the reviewer-required metadata corrections in this worktree.

## Risks / blockers

- Residual risk: non-canonical callers that still pass PageIndex-generated excerpt IDs into `qual.retrieval.fetch_excerpt()`, `qual.engine.retrieval.fetch_excerpt()`, or `RetrievalService.fetch_excerpt()` now receive `KeyError` instead of PageIndex-backed excerpt payloads.
- In-tree canonical retrieval flows do not rely on that fallback path; the remaining exposure is compatibility-only callers outside the MVP demo path or downstream consumers still holding PageIndex excerpt IDs.
- Blockers: none

## Required handoff fields

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

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits in the reviewed implementation range: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval implementation file in the reviewed range.
