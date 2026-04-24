# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `6c8d54c79eb9c0da811069e97603664468067d22`
- Packet refresh role: `reviewer-fix handoff regeneration`
- Packet refresh basis: `align the handoff packet to the actual implementation at the branch tip after reviewer scope objections`
- Packet refresh parent commit: `6c8d54c79eb9c0da811069e97603664468067d22`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: harden the `feat-commands` demo-path command resolution so the CLI-first MVP surface keeps routing terminal apply/reject/persist/export requests onto the canonical engine contract while Textual remains disabled.
- Risk reason: the reviewed slice touches the shared command-catalog contract plus one approved shared-test file outside lane-owned paths.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (Completed)

1. Reconfirm the actual implementation under review at branch tip commit `6c8d54c79eb9c0da811069e97603664468067d22`.
2. Regenerate the handoff packet so the scope, risks, and reviewed files match that implementation.
3. State the exact canonical demo-path step this slice advances using roadmap language directly.
4. Re-run the required local gates for the reviewed slice.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- The reviewed implementation basis is `6c8d54c79eb9c0da811069e97603664468067d22` (`Harden demo terminal command canonicalization`).
- This packet requests review of the real branch-tip implementation, not the earlier `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` command-catalog slice.
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata-only handoff file:
  - `THREAD_PACKET.md`

## Scope Completed

- Added canonical terminal-message mapping in `src/qual/commands/catalog.py` so `terminal_tool_orchestration` requests normalize apply/reject synonyms onto the canonical `apply-patch` and `reject-patch` demo commands.
- Added canonical terminal-message mapping for `terminal_synthesis_request` requests so persist/export synonyms normalize onto canonical `persist` and `export-handoff` demo commands.
- Wired `canonical_demo_command_argv()` and `canonical_mvp_command_argv()` through the terminal-message resolver so terminal-originated argv stays deterministic and aligned with the canonical demo loop.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for case-insensitive terminal message normalization across apply/reject and persist/export flows.
- Regenerated the handoff packet so the scope, commit, risk, and demo-path mapping now match the actual implementation being proposed for merge.

## Canonical Demo-Path Mapping

- Canonical demo-path steps advanced: `apply-patch`, `reject-patch`, `persist`, and `export-handoff` in the current CLI-first MVP path (`project-open -> retrieval -> patch-review -> apply-patch/reject-patch -> persist -> export-handoff`).
- Direct plan-alignment statement: this slice makes the canonical post-`patch-review` terminal path more real by ensuring terminal-originated apply/reject/persist/export requests still collapse onto the reviewed Milestone 3 engine-first command contract while Textual remains disabled.
- Concrete unblocker removed: terminal requests no longer depend on ad hoc message spelling or casing to reach the canonical patch-accept, patch-reject, persist-and-continue, and handoff-export commands.
- Scope guard: this remains narrow `feat-commands` contract hardening for the engine-first CLI/operator loop; it does not claim broader workflow, UI, Textual, or A2UI progress.

## Approved Exception Note

- Approved shared-test exception: `tests/unit/test_commands_catalog.py`
- Approved by: the lane `reviewer` role, as recorded in archived approval packet `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/packets/lanes/feat-commands/archive/R__APPROVED__codex-feat-commands__96f57e262da909d58a61cbdf4aa162aac8f16196__20260424T005429Z.md`.
- Approval source: archived reviewer approval packet `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/packets/lanes/feat-commands/archive/R__APPROVED__codex-feat-commands__96f57e262da909d58a61cbdf4aa162aac8f16196__20260424T005429Z.md`, plus canonical lane metadata `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/lane_meta/feat-commands.json`; both describe `tests/unit/test_commands_catalog.py` as the only approved non-owned implementation path in this narrowed handoff.
- Approval scope limit: this exception applies only to the focused regression coverage needed to prove deterministic terminal canonicalization for the `6c8d54c79eb9c0da811069e97603664468067d22` command-catalog slice.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Added deterministic terminal-message canonicalization for apply/reject requests in the command catalog.
2. Added deterministic terminal-message canonicalization for persist/export requests in the command catalog.
3. Added regression coverage for case-insensitive terminal argv normalization in `tests/unit/test_commands_catalog.py`.
4. Regenerated the handoff packet so it matches the actual reviewed implementation scope, canonical demo-path mapping, and risk level.

### Files Changed

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD_PACKET.md`

### Commands Run and Outcomes

- `make scope-check`: `PASSED`
- `./quality-format.sh --check`: `PASSED`
- `./quality-lint.sh`: `PASSED`
- `./quality-test.sh`: `PASSED`
- `./typecheck-test.sh`: `PASSED`
- `make ci`: `PASSED`

### Risks / Blockers

- Risks:
  - terminal-message aliases now cover the reviewed Milestone 3 apply/reject/persist/export path, but future terminal operations will still need explicit canonicalization coverage before they should be treated as contract-stable.
  - this slice is broader than the earlier `command_cli_contract()` hardening because it changes command-resolution behavior, so regressions would affect real terminal routing rather than only contract validation.
- Blockers:
  - none

## Required Handoff Fields

### Roadmap item(s) affected

- `feat-commands`: this slice hardens the CLI compatibility surface for the active engine-first MVP loop by keeping terminal apply/reject/persist/export requests on canonical command names.
- `ROADMAP.md` Milestone 3 requirement: `CLI can still execute the MVP loop while Textual remains disabled`; this change directly protects the downstream `patch -> export` segment of that loop by normalizing terminal requests onto canonical command tokens instead of allowing message spelling drift to alter operator behavior.
- Current operational narrowing: this work advances the canonical closure target after `patch-review` by keeping `apply-patch`/`reject-patch`, `persist`, and `export-handoff` reachable through the engine-first CLI path.

### Vision capability affected

- `PRODUCT_VISION.md` canonical engine contract: terminal-originated CLI requests now resolve onto one clean engine-facing action surface for patch acceptance, patch rejection, persistence, and handoff export.
- `PRODUCT_VISION.md` writing-centered workflow continuity: the post-review operator path stays deterministic enough to continue after patch review, persist work, and export or hand off without depending on presentation-specific terminal message phrasing.

### Routing / Provider Impact Note

- None. This change only affects local command resolution and focused command-catalog test coverage.

### Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Approved shared-test exception: `tests/unit/test_commands_catalog.py`
- Approved by: the lane `reviewer` role, recorded in archived approval packet `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/packets/lanes/feat-commands/archive/R__APPROVED__codex-feat-commands__96f57e262da909d58a61cbdf4aa162aac8f16196__20260424T005429Z.md`
- Approval source: archived reviewer approval packet `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/packets/lanes/feat-commands/archive/R__APPROVED__codex-feat-commands__96f57e262da909d58a61cbdf4aa162aac8f16196__20260424T005429Z.md`; canonical lane metadata record `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/lane_meta/feat-commands.json`
- Approval record detail: `Approved shared-test exception for tests/unit/test_commands_catalog.py. It is the only non-owned implementation path in this handoff.`
