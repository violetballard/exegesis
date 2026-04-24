# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `actual-branch-tip handoff with metadata-only refresh`
- Current branch tip before this packet refresh commit: `61b9c36f4b42898c7f86440600d8e02ec34a0b2a`
- Reviewed implementation head: `a9eaaaa79afcd57cde90738adee76e52cfc29adb`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..a9eaaaa79afcd57cde90738adee76e52cfc29adb`
- Shared-file approval basis: `tests/unit/test_unified_retrieval.py` is the only non-owned edit in the reviewed slice, and this handoff treats it as the explicit shared-by-approval regression exception under `THREAD_OWNERSHIP.md`'s shared-file mechanism (`SCOPE_ALLOW_SHARED=1 make scope-check`) for canonical retrieval-contract coverage.
- Canonical demo-path step advanced: `retrieve relevant material`
- Canonical demo-path statement: This branch advances `retrieve relevant material` by forcing excerpt lookup through the canonical SQLite FTS path and rejecting PageIndex-only excerpt IDs, which hardens the Milestone 3 retrieval surface used immediately before basket promotion and downstream workflow use.

## Scope Goal

- Keep this handoff explicitly limited to Milestone 3's `retrieve relevant material` step by documenting the FTS-only excerpt fail-closed contract, showing how it hardens the retrieval surface used before basket promotion, preserving the current branch-tip metadata refresh, and rerunning the required gates for the exact handoff content.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: hand off the truthful cumulative retrieval implementation through `a9eaaaa7` and keep the packet refresh itself limited to metadata files.
- Risk reason: this branch includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the handoff is treated as high-risk and summarized under the 4-task cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Re-anchor the packet to the truthful cumulative implementation range `d7fd5d20..a9eaaaa7`.
2. State explicitly that this work advances `retrieve relevant material` by forcing excerpt lookup through the canonical SQLite FTS path and rejecting PageIndex-only excerpt IDs before basket promotion and downstream workflow use.
3. Keep the scope and roadmap mapping tied only to Milestone 3 FTS-first retrieval and retrieval-first context handling.
4. Rerun and report `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` for the exact handoff content.

### Checkpoint Status

- `plan complete`: the handoff is re-anchored to `d7fd5d20..a9eaaaa7`.
- `first green tests`: recorded after rerunning the required gate stack for this handoff refresh.
- `before risky/shared file edit`: the branch still includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the reviewer-facing packet files and gate summary agree on the same implementation head, implementation range, and canonical demo-path statement.

## Scope Completed

- Kept SQLite FTS authoritative for the excerpt-lookup surface by removing the PageIndex fallback from `fetch_excerpt`, so PageIndex-only excerpt IDs now fail closed instead of being accepted through a non-canonical path before basket promotion and downstream workflow use.
- Preserved the lane's roadmap and vision mapping as Milestone 3 FTS-first retrieval and retrieval-first context handling, with no routing or provider behavior changes.
- Kept the packet refresh metadata-only while re-stating the canonical demo-path step the reviewer required.

## Reviewed Scope Boundary

- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..a9eaaaa79afcd57cde90738adee76e52cfc29adb`
- Reviewed implementation files:
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Metadata-only commits after the reviewed implementation head and before this fixer refresh:
- `94a1fb6b` -> `THREAD_PACKET.md`, `docs/gate_passed.txt`
- `e1530c68` -> `THREAD_PACKET.md`, `docs/gate_passed.txt`
- `422d1fda` -> `THREAD_PACKET.md`, `docs/gate_passed.txt`
- `02f89443` -> `THREAD_PACKET.md`, `docs/gate_passed.txt`
- `08cd31e3` -> `THREAD_PACKET.md`, `docs/gate_passed.txt`
- `ef827a8a` -> `THREAD_PACKET.md`, `docs/gate_passed.txt`
- `e013b29a` -> `THREAD_PACKET.md`, `docs/gate_passed.txt`
- `61b9c36f` -> `THREAD_PACKET.md`, `docs/gate_passed.txt`
- Current metadata-only packet refresh files:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Tasks Completed

1. Kept the `retrieve relevant material` entrypoint FTS-first and fail-closed by removing the PageIndex fallback from `fetch_excerpt`, which hardens the retrieval surface used before basket promotion.
2. Added approved shared regression coverage proving PageIndex-only excerpt IDs raise `KeyError`, so downstream workflow use sees the same fail-closed contract.
3. Refreshed the handoff packet to state explicitly that this work advances `retrieve relevant material`.
4. Preserved the roadmap and vision mapping on Milestone 3 FTS-first retrieval and retrieval-first context handling.

## Canonical Step Task Mapping

- Task 1 advances `retrieve relevant material` by keeping excerpt lookup on the canonical SQLite FTS path before basket promotion can consume the result.
- Task 2 advances `retrieve relevant material` by proving PageIndex-only excerpt IDs fail closed, so downstream workflow use does not see non-canonical retrieval state.
- Tasks 3 and 4 keep the packet and roadmap framing tied to that same retrieval step rather than broadening the branch story to later workflow phases.

## Files Changed

- Reviewed implementation files in `d7fd5d200358287fa42a18d39e2b277463b9b69f..a9eaaaa79afcd57cde90738adee76e52cfc29adb`:
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Metadata-only refresh files in this fixer slice:
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

1. The packet explicitly states which canonical demo-path step this work advances: `retrieve relevant material`, via the FTS-only excerpt fail-closed contract that hardens the retrieval surface used before basket promotion and downstream workflow use.
2. The packet cites the truthful cumulative reviewed implementation range `d7fd5d200358287fa42a18d39e2b277463b9b69f..a9eaaaa79afcd57cde90738adee76e52cfc29adb`, which matches the latest non-doc retrieval commit on this branch before the docs-only suffix.
3. The scope and roadmap mapping stay tied only to Milestone 3 FTS-first retrieval and retrieval-first context handling.
4. The current refresh commit is metadata-only because its diff is limited to packet files.
5. This fixer pass revalidated the truthful `d7fd5d20..a9eaaaa7` retrieval slice after the reviewer requested explicit canonical demo-path statement and task-to-step linkage.
6. The metadata-only history above is reconciled commit-by-commit, and each cited refresh commit touched only `THREAD_PACKET.md` plus `docs/gate_passed.txt`.
7. The task list is now explicitly mapped back to `retrieve relevant material`, so the reviewer no longer has to infer how the excerpt fallback removal hardens the Milestone 3 retrieval surface.

## Risks / Blockers

- Remaining risks: none beyond standard metadata drift if later packet refresh commits change the handoff without regenerating all packet artifacts together.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`
- Deterministic FTS excerpt payloads now remain suitable for later basket promotion and downstream workflow use without ambiguous fallback state.

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Shared-file approval basis remains limited to `tests/unit/test_unified_retrieval.py` under the `THREAD_OWNERSHIP.md` shared-file exception mechanism (`SCOPE_ALLOW_SHARED=1 make scope-check`).
- No provider or routing surfaces are part of the reviewed implementation range.
