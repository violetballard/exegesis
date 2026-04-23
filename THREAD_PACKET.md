# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: regenerate the `feat-commands` handoff so re-review is explicitly pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, while completing the missing high-risk AGENTS packet fields and the required Milestone 3 demo-path mapping.
- Risk reason: the reviewed slice changes command-contract behavior in `src/qual/commands/catalog.py` and uses shared regression coverage in `tests/unit/test_commands_catalog.py`, so the handoff must be treated as high-risk shared-file work.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Rebuild the handoff around the reviewer-pinned implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. Add the missing high-risk template fields and checkpoint evidence required by `AGENTS.md`.
3. Add an explicit canonical demo-path mapping for the deterministic command-contract change.
4. Re-run `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Early Review Triggers

- Before first edit to any shared or integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing or config behavior.

### Stop Triggers

- Unresolved test, lint, or typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (Short Updates)

- Plan complete: the handoff was narrowed back to the reviewer-pinned implementation slice at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- First green tests: recorded in the rerun block below after refreshing this packet.
- Before risky/shared file edit: this fixer edits only `THREAD.md` and `THREAD_PACKET.md`; no new implementation files are touched.
- Ready for handoff: the packet now includes the completed high-risk template, the explicit demo-path statement, and fresh gate results for this metadata refresh.

## Review Basis

- Re-review scope is pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` exactly, per reviewer instruction.
- Reviewed implementation files at that commit:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- This fixer commit refreshes handoff metadata only:
  - `THREAD.md`
  - `THREAD_PACKET.md`
- No additional implementation change is claimed for this resubmission.

## Scope Completed

- Locked the CLI contract to the command catalog by making `command_cli_contract()` verify that the canonical-name sequence implied by the parser-facing lookup table matches `command_names()` exactly.
- Added a deterministic failure when parser-surface canonical ordering drifts away from the catalog, raising `ValueError("Command CLI canonical names are inconsistent")` instead of silently accepting a stale CLI contract.
- Added regression coverage that proves the happy path still matches the catalog order and that drift is rejected explicitly.

## Plan Alignment

- Exact canonical demo-path step made more real directly: step 2 `retrieve relevant material`.
- Immediate dependent step kept trustworthy: step 3 `preview and apply or reject a patch`.
- Out of scope: this handoff does not claim new step 1 `open project/document` workflow coverage.
- Why this is not second-order work:
  - the Milestone 3 CLI loop currently depends on deterministic parser-to-catalog routing while Textual is disabled.
  - commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` hardens that live operator surface by proving the CLI lookup contract cannot silently drift away from the canonical command catalog.
  - that directly matters to step 2 because the retrieval entrypoint must keep resolving to the intended canonical command under smoke coverage.
  - it also keeps the immediate follow-on step 3 trustworthy because the same CLI contract continues to describe the parser-facing `diff-preview` route deterministically, even though this commit does not change step 3 behavior directly.

## Reviewer Fix Closure

- Required fix 1 satisfied: this is now a completed high-risk AGENTS handoff, including `Risk reason`, `Planned Tasks`, `Early Review Triggers`, `Stop Triggers`, and `Checkpoint Cadence`.
- Required fix 2 satisfied: the packet now states exactly which Milestone 3 CLI-loop steps the deterministic command-contract change advances and why that work is part of the active MVP loop rather than generic cleanup.
- Required fix 3 satisfied: re-review scope is pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this resubmission does not expand the reviewed implementation slice.

## Canonical Demo-Path Mapping

- Primary step advanced directly: step 2 `retrieve relevant material`.
  - reason: the retrieval CLI route depends on the parser-facing lookup table staying in lockstep with the canonical command catalog; otherwise smoke coverage can exercise the wrong canonical command without failing.
- Immediate dependent step preserved: step 3 `preview and apply or reject a patch`.
  - reason: the same parser-facing CLI contract also covers `diff-preview`, so deterministic catalog alignment keeps the next review step trustworthy after retrieval.
- Explicit AGENTS mapping statement:
  - this deterministic command-contract change makes step 2 more real directly because it guards the live retrieval CLI entrypoint against silent parser/catalog drift.
  - it makes step 3 more real only as the immediate follow-on route that relies on that same trusted CLI contract.
  - it is not second-order work because Milestone 3 requires the CLI fallback path to remain executable and smoke-testable while the UI surface is still disabled.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Added a command-contract consistency check in `src/qual/commands/catalog.py` so parser-facing canonical names must match the canonical command catalog order exactly.
2. Added regression coverage in `tests/unit/test_commands_catalog.py` for the matching contract case and for explicit rejection of catalog drift.
3. Regenerated the handoff as a completed high-risk AGENTS packet.
4. Re-ran the required scope and quality gates for this metadata refresh.

### Files Changed

- Reviewed implementation scope pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata-only changes in this fixer commit:
  - `THREAD.md`
  - `THREAD_PACKET.md`

### Commands Run and Outcomes

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

### Risks / Blockers

- Risk: `HIGH`
- Remaining risk:
  - the reviewed slice still includes shared-file regression coverage in `tests/unit/test_commands_catalog.py`, so the handoff remains high-risk even though no new shared implementation is added in this fixer pass.
  - this resubmission is intentionally review-scope-limited to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; later branch history is not part of the requested re-review.
- Blockers: none

## Required Handoff Fields

### Canonical demo-path step advanced

- Primary step advanced directly: step 2 `retrieve relevant material`
- Immediate dependent follow-on preserved: step 3 `preview and apply or reject a patch`
- Scope note: no new step 1 `open project/document` workflow coverage is claimed
- Exact AGENTS mapping statement: this work makes step 2 more real directly by preventing silent parser/catalog drift on the retrieval CLI route, and it keeps step 3 trustworthy as the immediate dependent parser route that uses the same deterministic command contract.
- Milestone 3 exit-criterion tie: this keeps the active CLI fallback loop executable and smoke-testable while UI work remains disabled.

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 3 (`Real workflow loop`): preserve CLI compatibility while the engine-first MVP loop is still exercised through command routes.
- Active MVP focus: `feat-commands` remains one of the current active implementation lanes for the CLI-first push.

### Vision capability affected

- `PRODUCT_VISION.md` operator-first control surface: CLI remains a first-class surface for development and reliability.
- Narrow capability mapping: this change hardens the deterministic CLI contract for the existing retrieval and immediate review path; it does not claim broader UI or workflow-surface progress.

### Routing / Provider Impact Note

- None.

### Proposed `README.md` Patch Text

- None.

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Ownership detail:
  - lane-owned reviewed implementation: `src/qual/commands/catalog.py`
  - shared reviewed test coverage: `tests/unit/test_commands_catalog.py`
  - metadata refreshed for handoff accuracy only: `THREAD.md`, `THREAD_PACKET.md`
