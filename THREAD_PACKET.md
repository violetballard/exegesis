# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix packet regeneration`
- Current branch tip before this fixer pass: `ad1cff2b91c60287de2b9dc7f43e92d8a0bb6d1a`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet-only descendants above the reviewed implementation head: metadata-only handoff refresh commits through `ad1cff2b`
- Packet traceability note: the reviewed retrieval implementation for this handoff ends at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`. Later commits above that point update packet wording only and do not change the reviewed retrieval implementation files.

## Scope goal

- Strengthen excerpt lookup on the retrieval service so only canonical FTS-backed excerpt IDs resolve successfully.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: keep retrieval excerpt lookup on the canonical FTS-first path by failing closed unless the excerpt came from the authoritative FTS flow.
- Risk reason: the reviewed implementation includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Restrict `fetch_excerpt` to canonical FTS-backed excerpt IDs.
2. Fail closed for PageIndex-only excerpt IDs instead of reconstructing them through non-canonical paths.
3. Preserve shared regression coverage for the FTS-only excerpt contract.
4. Regenerate the handoff packet so its scope stays anchored to the reviewed implementation slice.

### Checkpoint Status

- `plan complete`: the packet is regenerated against the reviewer-requested slice `378cf9a7..adfa8cda`.
- `first green tests`: recorded after rerunning the required gates for this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in the reviewed range remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the handoff now keeps the reviewed implementation head at `adfa8cda...` and treats later commits as packet-only descendants.

## Scope completed

- Narrowed `fetch_excerpt` in `src/qual/retrieval/service.py` so excerpt lookup succeeds only for canonical FTS-backed excerpt IDs.
- Preserved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs now fail closed.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This handoff strengthens `retrieve relevant material` by ensuring excerpt lookup on the retrieval service fails closed unless the excerpt came from the canonical FTS path.

## Tasks completed

1. Restricted `fetch_excerpt` to canonical FTS-backed excerpt IDs in `src/qual/retrieval/service.py`.
2. Removed the PageIndex-backed reconstruction path so non-FTS excerpt IDs fail closed.
3. Maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the canonical FTS-only excerpt contract.
4. Regenerated the handoff packet so it stays scoped to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Files changed

- Reviewed implementation files:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Packet-only descendant files above the reviewed implementation head:
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

1. The handoff now stays anchored to the reviewer-requested implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. The packet now states the canonical demo-path step explicitly: this slice strengthens `retrieve relevant material` by ensuring excerpt lookup fails closed unless the excerpt came from the canonical FTS path.
3. The scope summary is narrowed to the reviewed `fetch_excerpt` change and its shared regression coverage, without broadening back to general retrieval MVP claims outside this slice.

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
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval implementation file in the reviewed range.
- Ownership detail: no integrator-locked runtime files are part of the reviewed retrieval implementation range. Runtime edits remain in the lane-owned retrieval paths, and the only non-owned edit is the approved shared regression file `tests/unit/test_unified_retrieval.py`.
