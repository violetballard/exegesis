# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Packet refresh trace anchor before this fixer commit: `67cf9ec372b66c7e332efa310f8820f8f2824e61`
- Reviewed implementation head: `0a222d08310c907b67e6ce9d1585d55cd00d88aa`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..0a222d08310c907b67e6ce9d1585d55cd00d88aa`
- Canonical demo-path step advanced: `retrieve relevant material`
- Plan-alignment statement: this reviewed implementation advances `retrieve relevant material` by keeping excerpt provenance lookup deterministic on the FTS-only path and preventing PageIndex-only excerpt IDs from acting like an MVP retrieval path.
- Explicit Milestone 3 mapping: this makes the Milestone 3 demo-path step `retrieve relevant material` more real by advancing `Define generation provenance contract (retrieval evidence attached to outputs)` with deterministic FTS-only excerpt provenance.
- Traceability note: re-review this lane against the reviewed implementation range above. Commits after `0a222d08310c907b67e6ce9d1585d55cd00d88aa` are metadata-only packet refreshes; this fixer pass does not broaden retrieval runtime scope beyond that reviewed implementation head.

## Scope Goal

- Regenerate the reviewer-facing handoff metadata so the branch-tip lineage, metadata-only refresh files, and Milestone 3 demo-path mapping are truthful.

## Scope Completed

- The reviewed implementation keeps SQLite FTS authoritative for MVP retrieval while `fetch_excerpt` stays on the canonical FTS-only path in `src/qual/retrieval/service.py`.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves that PageIndex-only excerpt IDs fail closed with `KeyError`.
- The packet now truthfully absorbs the runtime-bearing `0a222d08310c907b67e6ce9d1585d55cd00d88aa` service change into the reviewed implementation head and leaves only metadata-only packet refreshes after that point.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct the reviewer-facing metadata so it truthfully describes the reviewed retrieval implementation slice, the packet-refresh lineage, and the Milestone 3 retrieval-step mapping.
- Risk reason: this lane includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the handoff stays on the AGENTS high-risk/shared 4-task basis.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Re-anchor the reviewed implementation head so every runtime-bearing commit after `adfa8cd...` is either absorbed into the reviewed range or excluded as metadata-only.
2. Restamp every reviewer-facing packet surface with the same packet trace anchor, metadata-only file list, and shared/high-risk budget basis.
3. State explicitly that this work advances the canonical demo-path step `retrieve relevant material` in Milestone 3.
4. Re-run the required local gates and record the refreshed metadata-only verification state.

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

1. Moved the reviewed implementation head forward to `0a222d08310c907b67e6ce9d1585d55cd00d88aa` so the branch-tip lineage is truthful about the last runtime retrieval change.
2. Restamped the writable packet surfaces with one consistent metadata-only refresh anchor `67cf9ec372b66c7e332efa310f8820f8f2824e61` and one consistent writable file set for this fixer pass.
3. Added the explicit canonical demo-path mapping for `retrieve relevant material`, tied to deterministic FTS-only excerpt provenance and the Milestone 3 provenance-contract step.
4. Re-ran the required local gates on the metadata-only packet refresh state.

## Files Changed

### Reviewed implementation files

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py` (approved shared regression coverage)

### Writable metadata-only packet refresh files

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

### Blocked metadata-only packet refresh files

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

### Prior metadata-only refresh before this fixer commit

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The packet now tells a truthful branch-tip lineage: the last runtime retrieval change is included in the reviewed implementation head `0a222d08310c907b67e6ce9d1585d55cd00d88aa`, and later commits are metadata-only packet refreshes.
2. The writable packet traceability fields now match reality for both packet refresh commits and file lists.
3. The handoff now includes the explicit canonical demo-path statement naming `retrieve relevant material` and tying it to deterministic FTS-only excerpt provenance.
4. The remaining `.codex` packet refresh is blocked by `Operation not permitted`, so the authoritative kickoff/lane-meta files still need the same restamp once those paths are writable.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: cannot write `.codex/kickoff_packets/feat-retrieval-fts.md` or `.codex/lane_meta/feat-retrieval-fts.json` because the filesystem rejects writes there with `Operation not permitted`.

## Ready For Handoff

- Status: not ready for re-review until the blocked `.codex` packet files are restamped to the same reviewed implementation head and packet trace anchor.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 4: Retrieval Layer (Planned)`
- `FTS-first ingestion/index path for context/vault documents`
- `Milestone 3: Product Readiness (Planned)`
- `Define generation provenance contract (retrieval evidence attached to outputs)`

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable generation`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
