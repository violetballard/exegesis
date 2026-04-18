# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-required handoff regeneration for the narrowed implementation slice`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh note: this fixer commit is metadata-only and keeps the reviewed retrieval implementation anchored to `adfa8cdadd43747ffbcb612e4151e262b13e52ca`; later packet-refresh commits remain metadata-only unless this handoff is explicitly regenerated.

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

- `plan complete`: the packet is reissued against the narrowed reviewed implementation range and explicitly names the canonical demo-path step advanced.
- `first green tests`: all required gates were rerun on this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in scope remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the handoff stays anchored to the reviewed implementation range above and keeps this metadata-only fixer commit separate from that reviewed implementation slice.

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path in this reviewed slice.
- Public excerpt lookup resolves only through the canonical FTS-backed path in `src/qual/retrieval/service.py`, so PageIndex-only excerpt IDs fail closed instead of silently backfilling from compatibility storage.
- PageIndex and embeddings remain compatibility-only paths in this slice; excerpt lookup no longer promotes PageIndex as a required runtime fallback path for the MVP contract.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` exercises the narrowed reviewed slice, including the FTS-only excerpt contract and deterministic downstream payload behavior.

## Canonical Demo-Path Step Advanced

- Canonical demo-path step advanced: `retrieve relevant material`

This handoff explicitly advances the canonical demo-path step `retrieve relevant material`. Removing the `PageIndex` fallback from `fetch_excerpt` strengthens the FTS-first retrieval contract for the engine-side Milestone 3 loop and preserves deterministic, auditable excerpt behavior for downstream basket promotion and workflow use without expanding scope beyond the MVP retrieval path.

## Tasks completed

1. Removed the `PageIndex` fallback from `fetch_excerpt` so public excerpt lookup stays on the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

- Reviewed implementation files:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Metadata-only handoff files:
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

## Reviewer fix closure

1. Regenerated the handoff with an explicit canonical demo-path mapping: `retrieve relevant material`.
2. Stated concretely that removing the `PageIndex` fallback from `fetch_excerpt` strengthens the FTS-first retrieval contract for the engine-side Milestone 3 loop without expanding scope beyond the MVP retrieval path.
3. Kept the reviewed implementation range anchored to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and treated later packet refreshes as metadata-only.

## Risks / blockers

- Risk: `HIGH`
- Blockers: none

## Required handoff fields

### Canonical demo-path step advanced

- `retrieve relevant material`

This change makes `retrieve relevant material` more real by keeping public excerpt lookup on the canonical FTS-only path and preserving deterministic, auditable excerpt provenance for downstream basket promotion and workflow use.

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
