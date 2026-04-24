# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Packet refresh trace anchor before this fixer commit: `8a545525c6fbaa908a82d249d07c3cbb85cb7add`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this reviewed slice strengthens `retrieve relevant material` by making excerpt lookup resolve only through the authoritative FTS path, which keeps downstream basket and workflow provenance deterministic.
- Reviewer-required canonical demo-path sentence: This work makes the "retrieve relevant material" step of the canonical demo path more real by forcing excerpt lookup to resolve only through the authoritative FTS-backed retrieval path.
- Explicit Milestone 3 mapping: this slice advances `Milestone 3: Real workflow loop` by keeping retrieval/search FTS-first and structured enough for basket promotion.
- Traceability note: re-review this lane against the reviewed implementation range above. Commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` are metadata-only packet refreshes unless a later handoff explicitly broadens the reviewed implementation range.

## Scope Goal

- Resubmit the retrieval handoff as a completed AGENTS high-risk packet for the reviewed FTS-only excerpt slice without broadening runtime retrieval scope.

## Scope Completed

- SQLite FTS remains the authoritative MVP retrieval path in the reviewed slice.
- `fetch_excerpt` now resolves through the canonical FTS-only lookup path in `src/qual/retrieval/service.py`.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves that PageIndex-only excerpt IDs fail closed with `KeyError`.
- PageIndex and embeddings remain compatibility-only paths and are not required MVP runtime paths in this slice.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: resubmit the retrieval handoff as a completed AGENTS high-risk packet for the reviewed FTS-only excerpt slice without broadening runtime retrieval scope.
- Risk reason: this lane includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the handoff stays on the shared/high-risk 4-task basis.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Restamp the handoff as a completed shared/high-risk packet for the reviewed slice anchored to `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. Add the explicit `Risk reason` and `Planned Tasks` sections the reviewer requested.
3. State explicitly that this work advances the canonical demo-path step `retrieve relevant material` in Milestone 3.
4. Re-run the required local gates and record the refreshed outcomes on the packet surfaces.

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

1. Reissued the writable handoff as a completed AGENTS high-risk packet for the reviewed slice anchored to `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. Added the explicit `Risk reason` and `Planned Tasks` sections the reviewer required on the writable packet surfaces.
3. Added the explicit canonical demo-path mapping to `retrieve relevant material` within Milestone 3.
4. Re-ran the required gates on the packet-refresh branch head and recorded the outcomes.

## Files Changed

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Blocked Packet Mirrors

- `.codex/kickoff_packets/feat-retrieval-fts.md` (live write-access recheck failed in this sandbox: `Operation not permitted`)
- `.codex/lane_meta/feat-retrieval-fts.json` (live write-access recheck failed in this sandbox: `Operation not permitted`)

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The handoff is now explicitly resubmitted as a completed `Thread Kickoff (High-Risk)` packet.
2. The writable packet now includes a concrete `Risk reason` tied to the approved shared regression surface in `tests/unit/test_unified_retrieval.py`.
3. The writable packet now includes the actual `Planned Tasks` for this narrowed reviewer-fix slice, capped at four items.
4. The handoff now explicitly states that this work advances the canonical demo-path step `retrieve relevant material`.

## Risks / Blockers

- Risk: `HIGH`
- Compatibility risk: callers that still pass PageIndex-only excerpt IDs to `RetrievalService.fetch_excerpt` now fail closed with `KeyError`, so downstream consumers must resolve and persist canonical FTS excerpt IDs instead of relying on the removed fallback path.
- Blockers: none

## Ready For Handoff

- Status: ready for re-review

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`: retrieval/search
- `retrieval returns structured results suitable for basket promotion`

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
