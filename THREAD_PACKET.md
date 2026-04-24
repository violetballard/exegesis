# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `metadata-only reviewer-fix refresh`
- Current branch tip before this packet refresh commit: `9bf6354eb5be984115d621aee698b172c9d498bd`
- Reviewed implementation head: `e8a8717b138f7d3551cd89bc3dc68071d5dad5f3`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..e8a8717b138f7d3551cd89bc3dc68071d5dad5f3`
- Shared-file approval basis: `tests/unit/test_unified_retrieval.py` is the only non-owned regression surface cited for this lane and remains the approved shared-by-approval exception under `THREAD_OWNERSHIP.md`.
- Canonical demo-path step advanced: `retrieve relevant material`
- Canonical demo-path statement: This branch advances `retrieve relevant material` by requiring excerpt lookup to resolve through the canonical SQLite FTS path and by keeping failed excerpt lookup audit payloads aligned with that FTS-only contract. This hardens the Milestone 3 retrieval surface used immediately before basket promotion and later workflow steps; it does not claim new basket-promotion wiring in this reviewed slice.

## Scope Goal

- Keep this handoff limited to Milestone 3's `retrieve relevant material` step by documenting the FTS-only excerpt fail-closed contract, the follow-up audit-shape fixes that preserve that contract, and the required gate rerun for the current metadata refresh.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: hand off the truthful cumulative retrieval implementation through `e8a8717b` and keep this refresh limited to metadata artifacts.
- Risk reason: the branch includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the handoff is summarized under the 4-task high-risk cap.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Re-anchor the packet set to the actual current pre-refresh branch tip `9bf6354e` and the latest runtime commit `e8a8717b`.
2. State explicitly that this work advances `retrieve relevant material` by hardening the canonical FTS excerpt contract and its failed-lookup audit shape before basket promotion.
3. Tighten scope language so the packet claims preserved contract alignment, not new downstream workflow integration.
4. Rerun and report `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` for this metadata refresh.

### Checkpoint Status

- `plan complete`: the packet set is re-anchored to `9bf6354e` and `e8a8717b`.
- `first green tests`: recorded after rerunning the required gate stack for this refresh.
- `before risky/shared file edit`: the branch still relies on approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the writable reviewer-facing packet files in this worktree agree on the same branch tip, reviewed implementation head, reviewed implementation range, and canonical demo-path statement.

## Scope Completed

- Kept SQLite FTS authoritative for excerpt lookup by removing the PageIndex fallback from `fetch_excerpt`, so PageIndex-only excerpt IDs fail closed instead of resolving through a non-canonical path.
- Preserved the same FTS-first contract in the failed excerpt lookup audit payload by enriching and aligning the audit shape in `src/qual/retrieval/service.py`.
- Kept roadmap and vision mapping limited to Milestone 3 FTS-first retrieval and retrieval-first context handling. This reviewed slice hardens the retrieval surface used before basket promotion; it does not itself add new basket-promotion or later workflow wiring.

## Reviewed Scope Boundary

- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..e8a8717b138f7d3551cd89bc3dc68071d5dad5f3`
- Runtime files touched in the latest reviewed implementation commits:
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- Metadata-only commit after the reviewed implementation head and before this fixer refresh:
- `9bf6354e` -> `THREAD_PACKET.md`, `docs/gate_passed.txt`
- Metadata-only refresh files in this fixer slice:
- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Tasks Completed

1. Kept the `retrieve relevant material` entrypoint FTS-first and fail-closed by removing the PageIndex fallback from `fetch_excerpt`.
2. Added approved shared regression coverage proving PageIndex-only excerpt IDs raise `KeyError`.
3. Mirrored the canonical source-strategy signal into retrieval payloads so downstream consumers see the same FTS-first provenance contract.
4. Enriched and aligned failed excerpt lookup audit payloads so the audit surface stays consistent with the FTS-only excerpt contract.

## Canonical Step Task Mapping

- Task 1 advances `retrieve relevant material` by keeping excerpt lookup on the canonical SQLite FTS path before basket promotion can consume the result.
- Task 2 advances `retrieve relevant material` by proving PageIndex-only excerpt IDs fail closed, so the retrieval surface stays auditable.
- Task 3 advances `retrieve relevant material` by preserving the FTS-first provenance signal in retrieval payloads without broadening scope to later workflow steps.
- Task 4 advances `retrieve relevant material` by keeping failed lookup audit payloads aligned with the same canonical excerpt contract.

## Files Changed

- Reviewed implementation files in `d7fd5d200358287fa42a18d39e2b277463b9b69f..e8a8717b138f7d3551cd89bc3dc68071d5dad5f3` include:
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

1. The packet now states explicitly that this slice advances the canonical demo-path step `retrieve relevant material`.
2. That statement is tied to the actual runtime work: FTS-only excerpt lookup, shared `KeyError` regression coverage, source-strategy mirroring, and failed lookup audit-shape alignment.
3. The scope language is tightened to preserved contract alignment before basket promotion, rather than claiming new downstream workflow integration.
4. The authoritative writable handoff artifacts are re-anchored to the actual current metadata-only branch tip `9bf6354e` and the latest runtime commit `e8a8717b`.

## Risks / Blockers

- Remaining risks: the `.codex` packet mirrors are read-only in this worktree and could not be refreshed, so they remain stale relative to `THREAD_PACKET.md`; later metadata-only refresh commits can also reintroduce drift if only one writable artifact is updated.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`
- The reviewed runtime slice preserves deterministic FTS excerpt lookup and audit behavior on the retrieval surface used before basket promotion.

### Vision capability affected

- `2. Retrieval-first context handling`
- `6. Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Shared-file approval basis remains limited to `tests/unit/test_unified_retrieval.py` under the `THREAD_OWNERSHIP.md` shared-file exception mechanism.
- No provider or routing surfaces are part of the reviewed runtime changes in this latest slice.
