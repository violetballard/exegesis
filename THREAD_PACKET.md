# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-required fix finalization`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal

- Keep the retrieval lane aligned to the canonical demo-path step `retrieve relevant material` by making public excerpt lookup deterministic and auditable on the FTS-first path.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: Harden the canonical FTS-only excerpt lookup contract for the retrieval step of the engine demo path.
- Risk reason: the reviewed implementation includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Checkpoint Status

- `plan complete`: aligned all handoff metadata to the reviewer-required narrowed range and canonical demo-path mapping.
- `first green tests`: all required gates passed on this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in scope remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the operative packet now states the required canonical demo-path step explicitly and keeps scope limited to the narrowed implementation range.

## Scope completed

- This narrowed slice advances only the canonical demo-path step `retrieve relevant material` by hardening the FTS-first excerpt lookup contract on the canonical engine retrieval surface.
- The reviewed implementation commit removes the PageIndex fallback from `fetch_excerpt` in `src/qual/retrieval/service.py`.
- The reviewed implementation commit adds approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.
- PageIndex and embeddings remain non-required compatibility paths in this slice; the MVP contract no longer frames them as runtime fallback paths for excerpt lookup.
- This handoff does not claim basket promotion, workflow actions, embeddings work, or broader engine-loop progress beyond the retrieval step, and it should be reviewed only as a packet alignment fix for that narrowed slice.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This change advances the canonical demo-path step `retrieve relevant material` by making excerpt lookup fail closed to the authoritative SQLite FTS path, without reintroducing PageIndex or embeddings as required runtime paths.

## Required Reviewer Fixes Addressed

1. Added an explicit handoff statement that this change advances the canonical demo-path step `retrieve relevant material`.
2. Tightened the scope mapping so it states this slice strengthens only the FTS-only excerpt lookup contract for the retrieval step of the canonical demo path.
3. Kept the reviewed implementation scope narrowed to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

- Reviewed implementation files:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Packet refresh files:
  - `THREAD_PACKET.md`
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / blockers

- Risk: `MEDIUM`
- Remaining compatibility risk: callers that previously relied on `fetch_excerpt` accepting PageIndex-only excerpt IDs will now receive `KeyError` unless they switch to canonical FTS excerpt IDs or the PageIndex-specific surface.
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` via the canonical demo-path step `retrieve relevant material`
- `feat-retrieval-fts`

### Vision capability affected

- `Retrieval-first context handling` via deterministic FTS-only excerpt lookup
- `Auditable state and workflow` via fail-closed, auditable excerpt ID handling

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval file in the reviewed implementation range.
