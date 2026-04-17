# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-required fix finalization`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal

- Keep the retrieval lane aligned to the canonical demo-path step `retrieve relevant material` by making the public excerpt lookup surface deterministic and auditable on the FTS-first path.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: Harden the canonical FTS-only excerpt lookup contract for the engine retrieval step.
- Risk reason: the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Checkpoint Status

- `plan complete`: narrowed the operative handoff packet to the reviewed retrieval slice and explicit demo-path mapping.
- `first green tests`: all required gates passed on this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in the reviewed range remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the operative packet now matches the reviewed implementation, risk class, and retrieval contract.

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path on the canonical retrieval surface.
- This reviewed range removes the PageIndex fallback from `fetch_excerpt` in `src/qual/retrieval/service.py`.
- This reviewed range adds approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.
- No broader retrieval facade, payload, or alternate-strategy work is claimed beyond this narrowed implementation slice.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

Canonical demo-path step advanced: `retrieve relevant material`.
This narrowed reviewed slice makes `retrieve relevant material` more real by making excerpt retrieval fail closed to the authoritative SQLite FTS path, strengthening the retrieval surface used before basket promotion in the engine-side workflow loop.

## Fixer Pass Traceability

- Fixer pass date: `2026-04-17`
- Pre-fix packet branch tip for this commit: `8b219039ab16d934eb41b96d5143504e203f644e`
- Reviewer packet source-of-truth anchor before this fixer commit: packet refresh commit `8b219039ab16d934eb41b96d5143504e203f644e`, packet refresh role `metadata-only reviewer-fix finalization`, reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- This metadata-only refresh preserves the reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` while carrying the reviewer-required canonical demo-path mapping for re-review.

## Required Reviewer Fixes Addressed

1. Reclassified the handoff as shared/high-risk work instead of low-risk work.
2. Removed the stale claim that PageIndex remains a runtime fallback behind the canonical retrieval package.
3. Stated the canonical demo-path step in narrowed terms that match the reviewed implementation slice and the reviewer-recommended wording.
4. Tightened that demo-path statement to the Milestone 3 contract by stating that `fetch_excerpt` now enforces FTS-only excerpt resolution and non-FTS excerpt IDs fail closed with `KeyError`.
5. Kept the packet scope aligned to the reviewed implementation head and range above.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.

## Files changed

- Reviewed implementation files:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Packet refresh file:
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
- Worktree constraint: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are present but not writable in this lane worktree, so `THREAD_PACKET.md` is the operative corrected handoff artifact for this fixer commit.
