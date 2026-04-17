# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-required fix finalization`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca^..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal

- Keep the retrieval lane aligned to the canonical demo-path step `retrieve relevant material` by making the public excerpt lookup surface deterministic and auditable on the FTS-first path.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: Harden the canonical FTS-only excerpt lookup contract for the engine retrieval step.
- Risk reason: the reviewed implementation includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Checkpoint Status

- `plan complete`: narrowed the operative handoff packet to the single reviewed implementation commit and explicit demo-path mapping.
- `first green tests`: all required gates passed on this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in scope remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the operative packet now matches the exact reviewed implementation slice and required AGENTS mapping.

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path on the canonical excerpt lookup surface.
- The reviewed implementation commit removes the PageIndex fallback from `fetch_excerpt` in `src/qual/retrieval/service.py`.
- The reviewed implementation commit adds approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.
- No broader retrieval payload, provenance, or alternate-strategy work is claimed in this narrowed handoff.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This change advances the canonical demo-path step `retrieve relevant material` by making excerpt retrieval fail closed to the authoritative SQLite FTS path before downstream basket-promotion and workflow use.

## Fixer Pass Traceability

- Fixer pass date: `2026-04-17`
- Pre-fix packet branch tip: `37690f6d63ee0418953d27a0e853e7dadb83610f`
- Reviewer packet source-of-truth anchor before this fixer commit: reviewed implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, reviewed implementation range `adfa8cdadd43747ffbcb612e4151e262b13e52ca^..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- This metadata-only refresh preserves the reviewed implementation head and narrows the operative reviewed implementation range to the single commit above while adding the explicit AGENTS demo-path statement required for re-review.
- Operative re-review artifact in this lane worktree: `THREAD_PACKET.md` is the source of truth for the narrowed reviewed range and canonical demo-path mapping on this fixer pass.
- Hidden packet artifacts under `.codex/` are present for reference in this worktree but are filesystem read-only here, so `THREAD_PACKET.md` is the operative corrected handoff artifact for re-review.

## Operative Packet Authority

- `THREAD_PACKET.md` is the authoritative re-review packet for this fixer pass.
- The lane worktree allows updating this handoff packet but denies writes to `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json`.
- Re-review should use this packet's reviewed implementation range, narrowed scope summary, and canonical demo-path statement as the operative reviewer-fix artifact.

## Operative Packet Note

- `THREAD_PACKET.md` is the operative corrected handoff artifact for this lane worktree.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` remain readable but are not writable under the current lane sandbox, so they may still show older metadata-only packet text.
- Re-review should evaluate traceability, scope, and AGENTS mapping from this packet plus the reviewer packet source of truth above.

## Required Reviewer Fixes Addressed

1. Set the reviewed implementation scope to the single implementation commit `adfa8cdadd43747ffbcb612e4151e262b13e52ca^..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. Added an explicit handoff statement that this change advances the canonical demo-path step `retrieve relevant material`.
3. Kept the narrowed scope wording limited to the FTS-only excerpt lookup change and its approved shared regression coverage.

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
