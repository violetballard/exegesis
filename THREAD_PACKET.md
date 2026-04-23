# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix cumulative handoff refresh`
- Current submitted tip before this packet refresh commit: `edd5380ab2aafe6dc83c6d4d6b2222b1256f20a2`
- Reviewed implementation head: `edd5380ab2aafe6dc83c6d4d6b2222b1256f20a2`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..edd5380ab2aafe6dc83c6d4d6b2222b1256f20a2`
- Packet traceability note: this packet is regenerated against the actual current implementation tip. It no longer claims that post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval commits are metadata-only.
- Canonical demo-path step advanced: `retrieve relevant material`

## Scope Goal

- Hand off the real cumulative FTS-first retrieval branch scope on the actual current tip while keeping the roadmap claim tied to the Milestone 3 retrieval step `retrieve relevant material`.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: finish the FTS-first retrieval MVP handoff on the truthful current tip, including the retrieval implementation added after `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- Risk reason: the cumulative branch range touches approved shared regression coverage plus packet/handoff support files outside the lane-owned paths, so the handoff is shared/high-risk work.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Rebuild the handoff packet around the actual current tip `edd5380ab2aafe6dc83c6d4d6b2222b1256f20a2`.
2. Update the reviewed range, scope summary, and file list to include the post-`adfa8cda` retrieval implementation commits.
3. Keep kickoff and final handoff metadata consistently marked shared/high-risk.
4. Re-run the required gates and commit the reviewer-fix packet refresh.

### Checkpoint Status

- `plan complete`: the handoff now targets the actual current tip instead of an earlier narrowed metadata-only story.
- `first green tests`: recorded after rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on the actual current tip plus this packet refresh.
- `before risky/shared file edit`: this pass updates shared handoff metadata files only.
- `ready for handoff`: the reviewed range, files changed, gate evidence, and roadmap wording all point at the same actual current tip.

## Scope Completed

- SQLite FTS remains the authoritative retrieval path across the cumulative reviewed range.
- `src/qual/retrieval/service.py` now carries deterministic excerpt lookup, query snapshot, provenance, basket-promotion, and sparse backfill behavior through the actual current tip, including the post-`adfa8cda` fixes `b8ae6c7a0e73d9d3ec5e1024ceb1c34d232e46c6`, `ced0bcaf3d5446d549b04d1bc24593eda8850266`, `0bf3263dbcc96d1b94cb890c27bfd4a2375ba61d`, `59752724035b5d241e51b3d3f89248947f22c7e1`, and `edd5380ab2aafe6dc83c6d4d6b2222b1256f20a2`.
- Retrieval payloads, provenance bundles, source/context bundles, and basket-promotion snapshots are normalized into stable, auditable structures through `src/qual/retrieval/service.py`, `src/qual/engine/retrieval/payload.py`, and the engine retrieval strategy/export files.
- Engine-facing retrieval exports now expose the canonical helpers while compatibility shims remain fail-closed and outside routing-critical paths.
- Shared regression coverage in `tests/unit/test_unified_retrieval.py` and packet/handoff support coverage in `tests/unit/test_packet_planner.py` now exercise the cumulative branch scope reflected by this packet.

## Reviewed Scope Boundary

- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..edd5380ab2aafe6dc83c6d4d6b2222b1256f20a2`
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

## Tasks Completed

1. Hardened the FTS-first retrieval contract so excerpts, hit strategies, query snapshots, and sparse backfills stay deterministic and auditable through the actual branch tip.
2. Extended canonical provenance, source/context bundles, and basket-promotion payloads so downstream engine flows can consume stable retrieval state.
3. Exposed and aligned canonical retrieval helpers through the engine retrieval facade while keeping compatibility shims fail-closed.
4. Regenerated packet/handoff traceability and shared regression coverage so re-review can evaluate the truthful cumulative branch scope.

## Files Changed

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

## Commands Run With Results

- Gate rerun date: `2026-04-23`
- Gate rerun target: actual current tip `edd5380ab2aafe6dc83c6d4d6b2222b1256f20a2` plus this reviewer-fix packet refresh
- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The handoff packet is regenerated against the actual current implementation tip rather than an earlier narrowed slice.
2. The reviewed range, scope summary, and files changed now include the post-`adfa8cda` retrieval implementation commits.
3. The writable handoff artifacts now classify this work as shared/high-risk against the truthful cumulative reviewed range.
4. The roadmap mapping remains tied to the Milestone 3 step `retrieve relevant material`, but that mapping is now attached to the truthful cumulative reviewed range.

## Risks / Blockers

- Risk: `HIGH`
- Residual risk: the cumulative reviewed range is well beyond the nominal AGENTS size budget for high-risk work, so review should pay attention to breadth and integration risk rather than assuming a narrow slice.
- Blockers: the worktree denies writes to `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` with `EPERM`, so this fixer commit can only refresh the writable handoff artifacts `THREAD_PACKET.md` and `docs/gate_passed.txt`.

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md: Milestone 3: Real workflow loop`
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

- Shared or integrator-locked edits in the cumulative reviewed range: `YES`
- Approved shared regression coverage remains in `tests/unit/test_unified_retrieval.py`.
- Packet/handoff support files in the cumulative reviewed range include `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py`.
- The `.codex` kickoff and lane-meta mirrors remain stale in this fixer commit because the worktree rejected writes to those paths with `EPERM`.
