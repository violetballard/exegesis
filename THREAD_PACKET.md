# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix refresh`
- Current branch tip before this packet refresh commit: `4387c7277d8d983012d970312a6bcc14f6fb571d`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet traceability note: re-review this lane against the narrowed implementation range above. Later branch commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, including substantive retrieval commits and metadata-only packet refreshes, remain outside this reviewed implementation range unless the handoff is explicitly regenerated to widen scope.
- Canonical demo-path step advanced: `retrieve relevant material`
- Reviewer-required plan-alignment statement: This change makes the canonical demo-path step `retrieve relevant material` more real because the public engine-facing `fetch_excerpt` surface now rehydrates shortlisted excerpt IDs only through the authoritative SQLite FTS path, so the engine loop cannot promote or reuse a PageIndex-only excerpt that lacks canonical retrieval evidence before downstream context gathering moves it into the basket.
- Canonical excerpt lookup contract note: `fetch_excerpt` is the canonical engine-facing excerpt lookup surface consumed downstream through the retrieval facade and engine excerpt tool wrapper, not just an internal consistency hardening point.
- Approved shared regression exception: `tests/unit/test_unified_retrieval.py` remains the only shared-by-approval regression surface in the reviewed implementation range.
- Packet authority note: the writable re-review artifacts for this fixer pass are `THREAD_PACKET.md` and `docs/gate_passed.txt`. The tracked `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` mirrors remain stale because this worktree rejects writes to `.codex/*` with `operation not permitted`.

## Scope Goal

- Refresh the reviewer-facing handoff metadata so it truthfully stays shared/high-risk under the 4-task cap, states the canonical demo-path step explicitly, and keeps the reviewed implementation range narrowed to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: correct reviewer-facing packet traceability without widening the reviewed retrieval implementation beyond the approved FTS-only excerpt slice.
- Risk reason: the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so this handoff is shared/high-risk work under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Regenerate the kickoff and handoff metadata so every writable artifact classifies this work as shared/high-risk under the 4-task cap.
2. Keep the reviewed implementation head fixed at `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and the reviewed implementation range fixed at `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
3. Add the required canonical demo-path statement naming `retrieve relevant material`.
4. Re-run the required local gates after the metadata refresh and record results without broadening scope.

## Scope Completed

- Kept excerpt lookup on the canonical engine-facing FTS-only path so PageIndex-only excerpt IDs fail closed instead of slipping into downstream workflow reuse without authoritative retrieval evidence.
- Kept the reviewed implementation scope narrowed to `src/qual/retrieval/service.py` and `tests/unit/test_unified_retrieval.py` in `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Added the explicit handoff statement that this slice advances `retrieve relevant material`.
- Left later branch commits outside this re-review packet.

## Reviewed Scope Boundary

- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation files:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Metadata-only packet refresh files in this commit:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Tasks Completed

1. Regenerated the writable handoff packet and gate summary so they classify this work as shared/high-risk under the 4-task cap.
2. Narrowed the reviewed implementation head and range back to `adfa8cdadd43747ffbcb612e4151e262b13e52ca` and `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
3. Added the explicit canonical demo-path statement naming `retrieve relevant material` and tied it to the FTS-only `fetch_excerpt` contract.
4. Re-ran the required gate suite on top of this metadata-only packet refresh and recorded results against the corrected range.

## Files Changed

- Reviewed implementation files in `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Metadata-only packet refresh files in this commit:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Validation Refresh Note

- Re-ran the full required gate suite on `2026-04-24` after the reviewer-required packet alignment refresh.
- This packet remains metadata-only and keeps the reviewed implementation range anchored to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Latest verification refresh for this metadata-only fixer handoff completed at `2026-04-24T01:41:31 PDT`.

## Reviewer Fix Closure

1. The writable packet and gate summary now classify this work as shared/high-risk under the 4-task cap.
2. The handoff explicitly states the canonical demo-path step `retrieve relevant material`.
3. The refreshed packet keeps the reviewed implementation range narrowed to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
4. Remaining blocker: the worktree refuses writes to `.codex/*`, so the kickoff artifact and lane-meta mirror could not be updated in place.

## Risks / Blockers

- Risk: `HIGH`
- Blockers: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are not writable in this worktree and still contain stale metadata.

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`: authoritative FTS-first retrieval feeding the engine loop

### Canonical demo-path step advanced

- `retrieve relevant material`
- This change makes the `retrieve relevant material` step more real because the public engine-facing `fetch_excerpt` surface now rehydrates shortlisted excerpt IDs only through the authoritative SQLite FTS path, so the engine loop cannot promote or reuse a PageIndex-only excerpt before downstream context gathering moves it into the basket.
- `src/qual/retrieval/__init__.py::fetch_excerpt`, its engine re-export in `src/qual/engine/retrieval/__init__.py`, and the engine excerpt tool wrapper are the canonical downstream excerpt lookup surface for this MVP path; the service-level change is a public contract tightening, not only internal consistency hardening.

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Approved shared regression coverage remains limited to `tests/unit/test_unified_retrieval.py`.
