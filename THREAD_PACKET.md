# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Packet refresh trace anchor before this fixer attempt: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this reviewed slice strengthens `retrieve relevant material` by making excerpt lookup resolve only through the authoritative FTS path, which keeps downstream provenance deterministic and supports later basket promotion.
- Reviewer-required canonical demo-path sentence: This work makes the "retrieve relevant material" step of the canonical demo path more real by forcing excerpt lookup to resolve only through the authoritative FTS-backed retrieval path.
- Explicit Milestone 3 mapping: this slice advances `Milestone 3: Real workflow loop` by keeping retrieval/search FTS-first and structured enough to support downstream basket promotion without changing basket-promotion behavior in this reviewed range.
- Traceability note: re-review this lane against the reviewed implementation range above. Later packet-refresh commits remain metadata-only unless a later handoff explicitly broadens the reviewed implementation range.

## Scope Goal

- Resubmit the retrieval handoff as a completed AGENTS high-risk packet for the reviewed FTS-only excerpt slice without broadening runtime retrieval scope.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path in the reviewed slice.
- `fetch_excerpt` now resolves through the canonical FTS-only lookup path in `src/qual/retrieval/service.py`.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves that PageIndex-only excerpt IDs fail closed with `KeyError`.
- PageIndex and embeddings remain compatibility-only paths and are not required MVP runtime paths in this slice.
- This reviewed range strengthens downstream basket promotion support by keeping retrieval provenance deterministic, but it does not change basket-promotion behavior directly.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: resubmit the retrieval handoff as a completed AGENTS high-risk packet for the reviewed FTS-only excerpt slice without broadening runtime retrieval scope.
- Risk reason: approved shared regression coverage in `tests/unit/test_unified_retrieval.py` makes this a shared/high-risk handoff even though the narrowed implementation slice stays within two reviewed files.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Regenerate the canonical kickoff/handoff packet for `feat-retrieval-fts` using the High-Risk template instead of the low-risk shape.
2. State the concrete high-risk reason tied to the approved shared regression file `tests/unit/test_unified_retrieval.py`.
3. Add the explicit canonical demo-path mapping for `retrieve relevant material` and keep basket promotion framed as downstream support only.
4. Keep the reviewed implementation scope anchored to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and the two reviewed files only.

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

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.
3. Regenerated the canonical handoff artifacts so they explicitly name the `retrieve relevant material` demo-path step advanced by this slice.
4. Tightened the handoff language so downstream basket promotion is described as supported by deterministic retrieval provenance, not directly changed in this reviewed range.

## Files Changed

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- `THREAD_PACKET.md`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The handoff now explicitly names the canonical demo-path step advanced by this reviewed slice: `retrieve relevant material`.
2. Basket promotion is now described only as downstream support from deterministic retrieval provenance, not as direct behavior changed in this reviewed range.
3. The reviewed implementation scope remains anchored to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`, with the existing shared-test exception note and gate results preserved.
4. The writable handoff artifact in this worktree is `THREAD_PACKET.md`; the `.codex` packet mirrors remain read-only and therefore unchanged in this metadata-only fixer pass.

## Risks / Blockers

- Risk: `HIGH`
- Metadata note: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are present but not writable in this worktree (`Operation not permitted`), so this fixer pass records the reviewer-required packet corrections in the writable `THREAD_PACKET.md`.
- Blockers: none

## Ready For Handoff

- Status: ready for handoff

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

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
