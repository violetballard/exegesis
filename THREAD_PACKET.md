# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix refresh against the current branch tip`
- Current submitted tip before this packet refresh commit: `b8ae6c7a0e73d9d3ec5e1024ceb1c34d232e46c6`
- Reviewed implementation head: `b8ae6c7a0e73d9d3ec5e1024ceb1c34d232e46c6`
- Reviewed implementation range: `d9542206f6fd14db37d1ddf5efd76f941d32314b..b8ae6c7a0e73d9d3ec5e1024ceb1c34d232e46c6`
- Packet traceability note: this refresh commit is metadata-only. It preserves the reviewed implementation head `b8ae6c7a0e73d9d3ec5e1024ceb1c34d232e46c6`, which is the actual current branch tip before this packet refresh commit.
- Fixer note: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` remain locked in this sandbox, so `THREAD_PACKET.md` and `docs/gate_passed.txt` are the authoritative writable handoff artifacts for this pass.
- Canonical demo-path step advanced: `retrieve relevant material`; excerpt lookup now fails closed to canonical FTS hits only, keeping retrieval provenance deterministic for downstream basket promotion.

## Scope Goal

- Keep the handoff claim narrowly scoped to the canonical demo-path step `retrieve relevant material`, specifically the FTS-only excerpt lookup contract and its regression-backed downstream provenance behavior.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`
- Scope goal: finalize the retrieval handoff on the actual branch tip while keeping the reviewer-visible claim limited to the canonical FTS excerpt lookup slice.
- Risk reason: retrieval contract code is in scope and the lane remains under the retrieval-specific review gate.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Refresh the handoff packet against the actual branch tip `b8ae6c7a0e73d9d3ec5e1024ceb1c34d232e46c6`.
2. Add the explicit canonical demo-path line required by review and keep that claim limited to the FTS-only excerpt lookup contract.
3. Refresh gate evidence against the same branch tip.
4. Commit the metadata-only reviewer-fix packet refresh.

### Early Review Triggers

- before changing public retrieval contract wording
- before broadening the canonical demo-path claim beyond excerpt lookup
- before changing reviewed-range traceability

### Checkpoint Status

- `plan complete`: the packet now targets the actual branch tip `b8ae6c7a0e73d9d3ec5e1024ceb1c34d232e46c6`, and the required reviewer fix is narrowed to the canonical excerpt lookup claim only.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on `b8ae6c7a0e73d9d3ec5e1024ceb1c34d232e46c6`.
- `before risky/shared file edit`: this pass edits handoff artifacts only.
- `ready for handoff`: the packet, canonical demo-path line, reviewed range, and gate evidence all point at the same branch tip.

## Scope Completed

- Canonical demo-path step advanced: `retrieve relevant material`; excerpt lookup now fails closed to canonical FTS hits only, keeping retrieval provenance deterministic for downstream basket promotion.
- Plan-alignment statement: this reviewed slice only advances `retrieve relevant material`; it does not claim broader engine-surface completion or alternate retrieval modes beyond the FTS-only excerpt lookup contract.
- `src/qual/retrieval/service.py` rebuilds excerpt query snapshots from the canonical nested query payload when present, clears mirrored query fields when that canonical snapshot is absent, and avoids rewriting the encrypted FTS database on read-only lookup paths.
- `src/qual/engine/retrieval/payload.py` preserves `excerpt_provenance_fingerprints` in normalized retrieval manifests so result fingerprints stay stable for audit and promotion consumers.
- The packet refresh is metadata-only and does not change the reviewed implementation range above.

## Reviewed Scope Boundary

- Reviewed implementation range: `d9542206f6fd14db37d1ddf5efd76f941d32314b..b8ae6c7a0e73d9d3ec5e1024ceb1c34d232e46c6`
- Cumulative non-metadata files in that range:
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- Metadata-only packet-refresh files in this resubmission:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`
- Locked stale packet copies not refreshed in place:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

## Canonical Demo-Path Step Advanced

- `retrieve relevant material`
- Canonical demo-path step advanced: `retrieve relevant material`; excerpt lookup now fails closed to canonical FTS hits only, keeping retrieval provenance deterministic for downstream basket promotion.

## Tasks Completed

1. Refreshed the handoff packet against the actual branch tip `b8ae6c7a0e73d9d3ec5e1024ceb1c34d232e46c6`.
2. Added the explicit canonical demo-path line requested by review and kept the claim scoped to the FTS-only excerpt lookup contract.
3. Refreshed gate evidence against `b8ae6c7a0e73d9d3ec5e1024ceb1c34d232e46c6`.
4. Produced a metadata-only reviewer-fix packet refresh for re-review.

## Files Changed

- Cumulative non-metadata files in `d9542206f6fd14db37d1ddf5efd76f941d32314b..b8ae6c7a0e73d9d3ec5e1024ceb1c34d232e46c6`:
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- Metadata-only packet-refresh files in this resubmission:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- Gate rerun date: `2026-04-23`
- Gate rerun target: `b8ae6c7a0e73d9d3ec5e1024ceb1c34d232e46c6`
- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The packet now states the canonical demo-path step explicitly in a single handoff line, using the reviewer-requested `retrieve relevant material` wording.
2. The scope statement stays narrow to the FTS-only excerpt lookup contract and its deterministic downstream provenance behavior.
3. The authoritative writable handoff artifacts have been regenerated on the actual branch tip for re-review.

## Risks / Blockers

- Risk: `MEDIUM`
- Residual risk: the cumulative reviewed range includes a later retrieval read-path hardening change in `src/qual/retrieval/service.py`; the canonical demo-path claim above remains intentionally narrower than the full implementation range.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md: Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`
- Canonical demo-path step advanced: `retrieve relevant material`; excerpt lookup now fails closed to canonical FTS hits only, keeping retrieval provenance deterministic for downstream basket promotion.

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits in this packet refresh commit: `NO`
- Cumulative reviewed implementation files remain in the retrieval lane paths above.
- `.codex` packet copies remain locked in this sandbox, so the root packet artifacts are authoritative for this pass.
