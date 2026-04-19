# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix finalization`
- Current branch tip before this fixer pass: `6b783b60b840c5fd63c3b07b19aa0c67ebf09081`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet traceability note: commit `206e37e3509c1e3331b45258c6e82ab31e52a82e` is a metadata-only packet refresh that changed only `THREAD_PACKET.md`. This fixer pass also refreshes only `THREAD_PACKET.md` and does not move the reviewed implementation head or range.

## Scope goal

- Harden the canonical `fetch_excerpt()` contract so excerpt lookup stays on the canonical FTS-only path, removes the PageIndex fallback, and proves PageIndex-only excerpt IDs fail closed.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: keep retrieval/search FTS-first, deterministic, and auditable on the canonical engine surface.
- Risk reason: the reviewed implementation includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Remove the PageIndex fallback from `fetch_excerpt()` so canonical excerpt lookup is FTS-only.
2. Add approved shared regression coverage proving PageIndex-only excerpt IDs fail closed with `KeyError`.
3. Correct packet traceability so reviewed implementation files and metadata-only packet files match git history exactly.
4. Re-emit the authoritative handoff packet with the explicit canonical demo-path step advanced by this work.

### Checkpoint Status

- `plan complete`: the packet now anchors re-review to the narrowed implementation range from the reviewer packet.
- `first green tests`: recorded after rerunning the required local gates for this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in the reviewed range remains `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: this packet now separates reviewed implementation files from metadata-only packet refresh files and states the canonical demo-path step explicitly.

## Scope completed

- `fetch_excerpt()` now resolves through the canonical FTS-only path and no longer falls back to PageIndex-backed excerpt payloads.
- Approved shared regression coverage proves PageIndex-only excerpt IDs fail closed with `KeyError`.
- This slice does not add new basket-promotion or broader retrieval-mode behavior; any downstream basket value is indirect contract hardening from the stricter FTS-only excerpt lookup surface.
- SQLite FTS remains the authoritative MVP retrieval path; PageIndex and embeddings remain compatibility-only, non-required paths in this slice.

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`

This handoff advances `retrieve relevant material` by enforcing authoritative FTS-only excerpt lookup with deterministic fail-closed behavior for non-FTS excerpt IDs.
It does not claim newly completed basket-promotion behavior; any downstream basket effect remains an indirect consequence of the hardened excerpt contract.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt()` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.
3. Tightened the handoff scope language so it describes indirect downstream basket contract hardening only and does not claim new basket-promotion behavior.

## Files changed

- Reviewed implementation files in `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Metadata-only packet refresh files in `206e37e3509c1e3331b45258c6e82ab31e52a82e`:
  - `THREAD_PACKET.md`
- Metadata-only reviewer-fix packet files in this fixer pass:
  - `THREAD_PACKET.md`

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer fix closure

1. Packet traceability now matches the cited git history: commit `206e37e3509c1e3331b45258c6e82ab31e52a82e` is recorded as `THREAD_PACKET.md` only.
2. The `Files changed` section now separates reviewed implementation files from the actual metadata-only packet refresh files.
3. The handoff explicitly states the canonical demo-path step advanced: `retrieve relevant material`.
4. Scope language now explicitly avoids claiming broader retrieval-mode or basket-promotion work beyond the `fetch_excerpt()` FTS-only contract hardening proved in the reviewed implementation.

## Risks / blockers

- Risk: `HIGH`
- Residual risk: callers holding PageIndex-generated excerpt IDs now receive `KeyError` from canonical excerpt lookup surfaces instead of a fallback payload.
- Blockers: none

## Required handoff fields

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

## Scope-check / ownership note

- Shared/integrator-locked edits in the reviewed implementation range: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval implementation file in the reviewed retrieval scope.
- Packet-only fixer files are handoff metadata files and do not change reviewed retrieval runtime behavior.
