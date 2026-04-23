# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix refresh against the current branch tip`
- Current submitted tip before this packet refresh commit: `e3ba89260c66e03a0d01f3147943410bfacfb7a9`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet traceability note: this refresh commit is metadata-only. It preserves the reviewed implementation head `adfa8cdadd43747ffbcb612e4151e262b13e52ca` while refreshing the handoff packet on the later metadata-only branch tip `e3ba89260c66e03a0d01f3147943410bfacfb7a9`.
- Canonical demo-path step advanced: `retrieve relevant material`; excerpt lookup now fails closed to the canonical FTS-backed retrieval surface and no longer treats PageIndex as a runtime fallback path.

## Scope Goal

- Keep the handoff claim narrowly scoped to the canonical demo-path step `retrieve relevant material`, specifically the FTS-only excerpt lookup contract and its regression-backed deterministic provenance behavior.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: finalize the retrieval handoff on the actual branch tip while keeping the reviewer-visible claim limited to the canonical FTS excerpt lookup slice proved by `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Risk reason: the lane touches the retrieval contract and includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the shared/high-risk 4-task cap applies.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Refresh the handoff packet against the actual metadata-only branch tip `e3ba89260c66e03a0d01f3147943410bfacfb7a9`.
2. Add the explicit canonical demo-path line requested by review and keep the claim scoped to the FTS-only excerpt lookup contract.
3. Tighten `Scope goal`, `Scope completed`, and related handoff language so this packet claims only what `adfa8cdadd43747ffbcb612e4151e262b13e52ca` proves.
4. Re-run the required gates and commit the metadata-only reviewer-fix packet refresh.

### Checkpoint Status

- `plan complete`: the packet targets the actual metadata-only branch tip `e3ba89260c66e03a0d01f3147943410bfacfb7a9`, and the reviewer fix is narrowed to the canonical excerpt lookup claim only.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on `e3ba89260c66e03a0d01f3147943410bfacfb7a9`.
- `before risky/shared file edit`: this pass edits packet metadata only.
- `ready for handoff`: the packet, reviewed range, canonical demo-path line, and gate evidence all point at the same branch tip.

## Scope Completed

- Canonical demo-path step advanced: `retrieve relevant material`; excerpt lookup now fails closed to the canonical FTS-backed retrieval surface and no longer treats PageIndex as a runtime fallback path.
- Plan-alignment statement: this reviewed slice only advances `retrieve relevant material`; it does not claim broader engine-surface completion, alternate retrieval modes, or full lane completion.
- `src/qual/retrieval/service.py` now makes `fetch_excerpt()` resolve only through the canonical FTS lookup path.
- `tests/unit/test_unified_retrieval.py` now proves PageIndex-only excerpt IDs fail closed with `KeyError` under approved shared regression coverage.
- This packet refresh is metadata-only and does not change the reviewed implementation range above.

## Reviewed Scope Boundary

- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation files:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Metadata-only packet-refresh files in this resubmission:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`
- Stale mirror files not writable in this sandbox:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

## Tasks Completed

1. Refreshed the handoff packet against the actual metadata-only branch tip `e3ba89260c66e03a0d01f3147943410bfacfb7a9`.
2. Added the explicit canonical demo-path line requested by review and kept the claim scoped to the FTS-only excerpt lookup contract.
3. Tightened the handoff language so this packet claims only the deterministic, auditable excerpt-lookup contract change proved by `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
4. Re-ran the required gates and produced a metadata-only reviewer-fix packet refresh for re-review.

## Files Changed

- Reviewed implementation files in `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Metadata-only packet-refresh files in this resubmission:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- Gate rerun date: `2026-04-23`
- Gate rerun target: `e3ba89260c66e03a0d01f3147943410bfacfb7a9`
- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The packet now states the canonical demo-path step explicitly using the reviewer-requested `retrieve relevant material` wording.
2. The scope statement stays narrow to the FTS-only excerpt lookup contract and its deterministic downstream provenance behavior.
3. The authoritative writable handoff artifacts have been regenerated on the actual branch tip for re-review.

## Risks / Blockers

- Risk: `MEDIUM`
- Residual risk: this packet intentionally narrows the claim to the excerpt-lookup contract change; broader retrieval-lane work remains out of scope for this specific re-review.
- Blockers: the `.codex` kickoff and lane-meta mirror files are visible but not writable in this sandbox (`EPERM`), so this refresh is carried by `THREAD_PACKET.md`.

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md: Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`
- Canonical demo-path step advanced: `retrieve relevant material`; excerpt lookup now fails closed to the canonical FTS-backed retrieval surface and no longer treats PageIndex as a runtime fallback path.

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits in this packet refresh commit: `NO`
- Shared-by-approval coverage in the reviewed implementation range remains limited to `tests/unit/test_unified_retrieval.py`.
