# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Packet refresh trace anchor before this fixer pass: `ee2befa746328053cd9917307f87ae68ae3bc75e`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- Packet/supporting files refreshed in this fixer pass: `THREAD_PACKET.md`, `docs/gate_passed.txt`
- Re-review authority note: in this worktree, use `THREAD_PACKET.md` and `docs/gate_passed.txt` as the updated reviewer-facing record because `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are unwritable (`operation not permitted`).
- Canonical demo-path step advanced: `retrieve relevant material`
- Demo-path sentence: this slice advances the canonical demo-path step `retrieve relevant material` by making `fetch_excerpt` resolve only through the canonical FTS lookup path, so PageIndex-only excerpt IDs fail closed and Milestone 3 stays aligned to FTS-first structured retrieval before basket promotion.
- Canonical demo-path strengthening statement: this slice makes excerpt lookup auditable and fail-closed on the FTS-first engine path used before basket promotion.
- Reviewer-required plan-alignment statement: this reviewed slice is a narrow Milestone 3 retrieval contract correction, not a lane-completion claim; `fetch_excerpt` now resolves only through the canonical FTS lookup path, and the shared approved regression test proves PageIndex-only excerpt IDs fail closed, which keeps the `retrieve relevant material` step aligned to Milestone 3's FTS-first structured retrieval requirement.
- Milestone mapping: `Milestone 3: Real workflow loop`
- FTS-first gate statement: the reviewed implementation range remains FTS-first for the MVP; PageIndex and embeddings remain deferred or compatibility paths and are not required runtime retrieval paths in this handoff.

## Scope Goal

- Return this lane for re-review as a metadata-corrected, scope-tight handoff for the existing narrow Milestone 3 retrieval contract correction.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path in the reviewed slice.
- `fetch_excerpt` resolves through the canonical FTS-only lookup path in `src/qual/retrieval/service.py`.
- PageIndex-only excerpt IDs now fail closed on `fetch_excerpt`, so public excerpt lookup stays bound to the canonical FTS-backed provenance path.
- Approved shared regression coverage proves that PageIndex-only excerpt IDs fail closed with `KeyError`.
- PageIndex and embeddings remain deferred or compatibility paths; they are not required runtime fallbacks for this public excerpt contract.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: refresh the retrieval handoff metadata so re-review stays anchored to the narrowed `adfa8cdadd43747ffbcb612e4151e262b13e52ca` FTS-only excerpt change and its approved shared regression coverage.
- Risk reason: approved shared regression coverage in `tests/unit/test_unified_retrieval.py` makes this shared/high-risk work under `AGENTS.md`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Reissue the kickoff metadata in the High-Risk template required for shared-file work.
2. Tighten the handoff text to the reviewed implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
3. Keep `fetch_excerpt` described as FTS-only on the public lookup path while PageIndex and embeddings remain deferred or compatibility paths.
4. Re-run the required local gates and record the outcomes for re-review.

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

## AGENTS Checkpoint Evidence

- `plan complete`: the high-risk kickoff and planned tasks were locked to the narrowed reviewed implementation slice `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and to the canonical demo-path step `retrieve relevant material`.
- `first green tests`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed for this metadata-only fixer pass.
- `before risky/shared file edit`: the shared/high-risk boundary was called out before refreshing the handoff because the reviewed implementation scope still includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: `THREAD_PACKET.md` and `docs/gate_passed.txt` now carry the same reviewed implementation head, narrowed reviewed range, and checkpoint trail required for re-review, while the `.codex` mirror files remain blocked by filesystem permissions in this worktree.

### Handoff Packet

- branch name
- tasks completed (numbered)
- files changed
- commands run + outcomes
- risks/blockers
- all required fields from `INTEGRATION.md`

## Tasks Completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.
3. Regenerated the writable thread handoff and gate summary artifacts in the required shared/high-risk format and recorded the blocked `.codex` mirror files explicitly.
4. Re-ran the required local gates and recorded the results for re-review.

## Files Changed

- Reviewed implementation files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- Packet/supporting files: `THREAD_PACKET.md`, `docs/gate_passed.txt`
- Blocked mirror files: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / Blockers

- Risk: `HIGH`
- Compatibility risk: callers must preserve canonical FTS excerpt IDs; PageIndex-only excerpt IDs now fail closed with `KeyError` on the public lookup path.
- Blockers: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are unwritable in this worktree (`operation not permitted`), so the reviewer-targeted packet mirrors could not be refreshed here.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`: retrieval/search

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared-by-approval edits in reviewed range: `YES`
- Integrator-locked edits in reviewed range: `NO`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
