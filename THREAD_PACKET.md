# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `actual-branch-tip handoff with metadata-only refresh`
- Current branch tip before this packet refresh commit: `422d1fdabf53f56e70a26eb00fce31a15bc189f7`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Canonical demo-path step advanced: `retrieve relevant material`
- Canonical demo-path statement: This branch advances `retrieve relevant material` by forcing excerpt lookup through the canonical SQLite FTS path and rejecting PageIndex-only excerpt IDs so downstream basket-promotion inputs stay deterministic and auditable.

## Scope Goal

- Keep this handoff explicitly limited to Milestone 3's `retrieve relevant material` step by documenting the FTS-only excerpt fail-closed contract, preserving the current branch-tip metadata refresh, and rerunning the required gates for the exact handoff content.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: hand off the reviewer-approved narrowed runtime implementation through `adfa8cda` and keep the packet refresh itself limited to metadata files.
- Risk reason: this branch includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the handoff is treated as high-risk and summarized under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Re-anchor the packet to the reviewer-approved narrowed implementation range `d7fd5d20..adfa8cda`.
2. State explicitly that this work advances `retrieve relevant material` by forcing excerpt lookup through the canonical SQLite FTS path and rejecting PageIndex-only excerpt IDs.
3. Keep the scope and roadmap mapping tied only to Milestone 3 FTS-first retrieval and retrieval-first context handling.
4. Rerun and report `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` for the exact handoff content.

### Checkpoint Status

- `plan complete`: the handoff is re-anchored to `d7fd5d20..adfa8cda`.
- `first green tests`: recorded after rerunning the required gate stack for this handoff refresh.
- `before risky/shared file edit`: the branch still includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the reviewer-facing packet files and gate summary agree on the same implementation head, implementation range, and canonical demo-path statement.

## Scope Completed

- Kept SQLite FTS authoritative for the excerpt-lookup surface by removing the PageIndex fallback from `fetch_excerpt`, so PageIndex-only excerpt IDs now fail closed instead of being accepted through a non-canonical path.
- Preserved the lane's roadmap and vision mapping as Milestone 3 FTS-first retrieval and retrieval-first context handling, with no routing or provider behavior changes.
- Kept the packet refresh metadata-only while re-stating the canonical demo-path step the reviewer required.

## Reviewed Scope Boundary

- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation files:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Metadata-only commits after the reviewed implementation head and before this fixer refresh:
- `31b91107`
- `94a1fb6b`
- `e1530c68`
- `422d1fda`
- Current metadata-only packet refresh files:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Tasks Completed

1. Kept the excerpt-lookup entrypoint FTS-first and fail-closed by removing the PageIndex fallback from `fetch_excerpt`.
2. Added approved shared regression coverage proving PageIndex-only excerpt IDs raise `KeyError`.
3. Refreshed the handoff packet to state explicitly that this work advances `retrieve relevant material`.
4. Preserved the roadmap and vision mapping on Milestone 3 FTS-first retrieval and retrieval-first context handling.

## Files Changed

- Reviewed implementation files in `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`:
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Metadata-only refresh files in this fixer slice:
- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands Run With Results

- `make scope-check`: `PASS` (`no policy for branch 'codex/feat-retrieval-fts'; skipping`)
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The packet explicitly states which canonical demo-path step this work advances: `retrieve relevant material`.
2. The packet keeps the reviewed implementation range narrowed to `d7fd5d200358287fa42a18d39e2b277463b9b69f..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
3. The scope and roadmap mapping stay tied only to Milestone 3 FTS-first retrieval and retrieval-first context handling.
4. The current refresh commit is metadata-only because its diff is limited to packet files.
5. This fixer pass revalidated the reviewer-approved narrowed slice `d7fd5d20..adfa8cda` after the reviewer requested an explicit canonical demo-path statement and scope tightening.

## Risks / Blockers

- Remaining risks: none beyond standard metadata drift if later packet refresh commits change the handoff without regenerating all packet artifacts together.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`
- Deterministic FTS excerpt payloads now remain suitable for later basket promotion without ambiguous fallback state.

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
- No provider or routing surfaces are part of the reviewed implementation range.
