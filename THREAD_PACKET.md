# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix refresh`
- Current submitted tip before this packet refresh commit: `11d7079e3652cbcf14e9de2524b37ef2f8ab8a05`
- Reviewed implementation head: `11d7079e3652cbcf14e9de2524b37ef2f8ab8a05`
- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..11d7079e3652cbcf14e9de2524b37ef2f8ab8a05`
- Packet traceability note: review this lane against the narrowed implementation range above. The current packet refresh commit is metadata-only and does not broaden retrieval scope beyond `adfa8cda..11d7079e`.
- Canonical demo-path step advanced: `retrieve relevant material`

## Scope Goal

- Keep FTS-first retrieval deterministic and auditable by preserving canonical query-constraint snapshots during excerpt lookup rehydration.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct the reviewer packet against the real post-review retrieval fixes without widening the lane beyond deterministic FTS retrieval behavior.
- Risk reason: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so it is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Re-anchor the handoff to the real reviewed implementation head `11d7079e` and reviewed range `adfa8cda..11d7079e`.
2. Explain why sparse query-constraint rehydration is required for deterministic, auditable FTS excerpt lookup instead of being off-lane expansion.
3. Reissue the reviewed file list, completed tasks, and canonical demo-path statement to match the current branch contents.
4. Re-run the required gates and record results against the real reviewed implementation head/range.

### Checkpoint Status

- `plan complete`: the packet is now anchored to the real post-review retrieval implementation range `adfa8cda..11d7079e`.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
- `before risky/shared file edit`: this handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the packet and gate summary agree on the same reviewed implementation head, reviewed range, reviewed files, and canonical demo-path step.

## Scope Completed

- SQLite FTS remains the authoritative retrieval path for the reviewed implementation range.
- Excerpt lookup still fails closed on the canonical FTS path for PageIndex-only excerpt IDs.
- Sparse excerpt query snapshots now rehydrate canonical constraint fields from both nested `query.constraints` payloads and the mirrored top-level `query_constraints` or `query_*` fields, so excerpt lookup, provenance, and basket-promotion payloads stay deterministic and auditable instead of silently dropping prior constraints.
- This handoff advances the canonical demo-path step `retrieve relevant material` by keeping FTS excerpt lookup faithful to the stored query contract that downstream basket and workflow consumers audit.

## Reviewed Scope Boundary

- Reviewed implementation range: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..11d7079e3652cbcf14e9de2524b37ef2f8ab8a05`
- Reviewed implementation files:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Current metadata-only handoff files in this packet refresh:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Tasks Completed

1. Kept `fetch_excerpt` on the canonical FTS-only lookup path so PageIndex-only excerpt IDs fail closed.
2. Backfilled sparse excerpt query-constraint fields from canonical top-level mirrors when a nested `query.constraints` snapshot is partial or empty.
3. Merged sparse top-level `query_constraints` payloads into excerpt query snapshot rebuilding so lookup provenance and basket-promotion payloads preserve the original auditable query contract.
4. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving partial sparse query snapshots still normalize back to the canonical deterministic query payload.

## Files Changed

- Reviewed implementation files in `adfa8cdadd43747ffbcb612e4151e262b13e52ca..11d7079e3652cbcf14e9de2524b37ef2f8ab8a05`:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Current metadata-only packet refresh files:
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

1. The packet now matches the real branch tip by reviewing the code-changing range `adfa8cda..11d7079e` instead of calling those commits metadata-only.
2. The handoff explicitly states that this lane advances canonical demo-path step `retrieve relevant material`.
3. The scope summary explains why sparse query-constraint rehydration is required for deterministic, auditable FTS retrieval output rather than broadening the lane.
4. The reviewed file list, task list, and gate summary all match the current reviewed implementation range and branch contents.

## Risks / Blockers

- Risk: `MEDIUM`
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
