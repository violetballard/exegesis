# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix truthful range refresh`
- Current submitted tip before this packet refresh commit: `58474e0967272070e48febd42c29107e6000744b`
- Reviewed implementation head: `cf644d98c43cc396cd5b7c6b8d725b87fb715c61`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..cf644d98c43cc396cd5b7c6b8d725b87fb715c61`
- Packet traceability note: review this lane against the truthful implementation range above. In the current worktree, `git diff --name-only cf644d98c43cc396cd5b7c6b8d725b87fb715c61..58474e0967272070e48febd42c29107e6000744b` returns only `THREAD_PACKET.md` and `docs/gate_passed.txt`, so later commits on the branch tip are packet-refresh artifacts only.
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required plan-alignment statement: this work advances `retrieve relevant material` by keeping SQLite FTS authoritative, hardening excerpt lookup failure auditing, and making canonical retrieval payload rebuilds fail closed so downstream engine consumers only receive deterministic, auditable retrieval metadata.

## Scope Goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt, provenance, and failure-audit output.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: make the handoff truthful for the actual promoted retrieval range ending at `cf644d98c43cc396cd5b7c6b8d725b87fb715c61`.
- Risk reason: this lane includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Retarget the reviewed implementation range to the last retrieval/runtime commit actually present on the branch.
2. Recompute `Scope completed`, `Tasks completed`, `Files changed`, and budget status against that truthful range.
3. Keep the canonical demo-path step explicit in the handoff packet itself.
4. Rerun the required gates on the actual branch tip and record the results.

### Checkpoint Status

- `plan complete`: the packet is anchored to the truthful runtime range `378cf9a7..cf644d98`.
- `first green tests`: recorded after rerunning the required gate suite on the packet-refresh branch tip.
- `before risky/shared file edit`: approved shared regression coverage remains in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the packet artifacts and gate summary agree on the same reviewed implementation range and demo-path step.

## Scope Completed

- SQLite FTS remains the authoritative retrieval path across the reviewed implementation range.
- The canonical retrieval payload surface is deterministic enough for downstream engine flows: payload snapshots, provenance, rank/query metadata, and exported retrieval helpers stay normalized and auditable.
- The excerpt lookup surface fails closed on the canonical FTS path, and failed excerpt lookups now emit the hardened audit shape and aliases added after `adfa8cda`.
- Canonical retrieval payload rebuilds fail closed instead of silently reconstructing missing metadata.
- This handoff explicitly advances the canonical demo-path step `retrieve relevant material`.

## Reviewed Scope Boundary

- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..cf644d98c43cc396cd5b7c6b8d725b87fb715c61`
- Reviewed implementation files:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `docs/gate_passed.txt`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_packet_planner.py`
- `tests/unit/test_unified_retrieval.py`
- Packet-refresh-only files after `cf644d98` on the current tip:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Tasks Completed

1. Kept retrieval FTS-first on the canonical surfaces, including the FTS-only excerpt lookup path and shared regression coverage proving PageIndex-only excerpt IDs fail closed.
2. Hardened failed excerpt lookup audit output so the canonical excerpt failure path emits stable audit shape and alias fields.
3. Made canonical retrieval payload rebuilds fail closed and kept payload, provenance, rank, and query metadata deterministic for downstream engine consumers.
4. Re-emitted the handoff artifacts so the reviewed implementation range, files changed, budget note, and canonical demo-path step all match the actual promoted branch state.

## Files Changed

- Truthful reviewed implementation files in `378cf9a74a3658058079a32f186fcd254c4a4034..cf644d98c43cc396cd5b7c6b8d725b87fb715c61`:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `docs/gate_passed.txt`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_packet_planner.py`
- `tests/unit/test_unified_retrieval.py`
- Current packet-refresh files after `cf644d98`:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Budget Compliance

- Task budget: `PASS` against the 4 summarized high-risk tasks above.
- Size budget: `FAIL` for the truthful promoted range. `git diff --stat 378cf9a7..cf644d98` reports `15 files changed` with a net delta far above the `<=8 files` and `<=300 net LOC` high-risk limits.
- This packet no longer claims the truthful promoted range fits the narrowed high-risk size budget.

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The reviewed implementation range now matches the last retrieval/runtime commit actually present on the branch: `378cf9a7..cf644d98`.
2. `Scope completed`, `Tasks completed`, `Files changed`, and budget status are recomputed against that truthful range.
3. Later commits on the current tip are described as packet-refresh artifacts only because the current diff after `cf644d98` is limited to `THREAD_PACKET.md` and `docs/gate_passed.txt`.
4. The packet itself explicitly states the canonical demo-path step `retrieve relevant material`.
5. The required gate suite was rerun on the actual branch tip and is recorded below and in `docs/gate_passed.txt`.

## Risks / Blockers

- Risk: `HIGH` because the truthful promoted range is a cumulative shared/high-risk lane slice that exceeds the nominal size budget.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
