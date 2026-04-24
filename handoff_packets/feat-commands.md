# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the CLI contract reuses the canonical `command_names()` ordering and raises if the parser-backed catalog surface drifts, plus focused regression coverage for canonical-order alignment and drift rejection in `tests/unit/test_commands_catalog.py`.
- Canonical demo-path step advanced: the Milestone 3 CLI-first `open project/document` control surface that keeps the operator in the manual MVP loop while Textual remains disabled.
- Canonical MVP flow context: `open project/document -> retrieve relevant material -> preview and apply or reject a patch` for the manual CLI smoke flow, with this slice specifically hardening the parser-backed command surface that starts and preserves that operator path.
- Canonical MVP flow mapping sentence: this `feat-commands` slice is not internal contract cleanup for its own sake; it is in-plan Milestone 3 CLI-first hardening because `command_cli_contract()` now fails fast when parser/catalog drift would otherwise silently break the operator-facing CLI surface that the `open project/document` entry step and the rest of the manual MVP loop depend on while Textual remains disabled.
- Demo-path sentence: this change makes the CLI-first MVP path more real by ensuring the concrete parser-backed command entrypoints an operator uses to open project or document state cannot silently drift away from the canonical catalog before the rest of the loop runs.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI surface from the catalog while leaving the contract seemingly valid, so an operator could start the manual MVP loop through an `open project/document` surface that had drifted away from the canonical catalog.
- Traceability note: reviewed implementation commit is `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, and its implementation scope is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; this follow-up commit refreshes handoff metadata only.

## Tasks Completed
1. Hardened `command_cli_contract()` so it validates canonical command names against `command_names()` and raises on parser/catalog drift instead of trusting derived lookup order.
2. Preserved canonical CLI contract ordering by returning the validated catalog-order tuple directly.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and parser/catalog drift rejection.

## Packet Refresh Notes
- This handoff now names the exact canonical demo-path step advanced, states why the work is in-plan for Milestone 3 instead of second-order cleanup, and keeps the approval basis pinned to reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` plus its two implementation files only.

## Files Changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Commands Run With Results
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed

## Risks / Blockers
- Risks: future command-surface edits still need to preserve the parser/catalog lock so the CLI contract for `open project/document -> retrieve relevant material -> preview and apply or reject a patch` stays deterministic.
- Scope clarification: this is command-contract hardening only; it does not add new command behavior, new persistence or auditability mechanisms, or a new workflow capability.
- Blockers: none.

## Roadmap Item(s) Affected
- `ROADMAP.md` Milestone 3 `Real workflow loop` because this is a narrow `feat-commands` command-catalog hardening slice that keeps the manual CLI smoke flow `open project/document -> retrieve relevant material -> preview and apply or reject a patch` stable while Textual remains disabled.
- `ROADMAP.md` Milestone 3 exit criterion `CLI can still execute the MVP loop while Textual remains disabled` because this is why the work is in-plan rather than second-order cleanup: it prevents silent parser/catalog drift from breaking the operator-facing CLI control surface the MVP loop depends on.

## Vision Capability Affected
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract` because the active CLI operator surface now rejects parser/catalog drift before it can silently change the command contract the operator relies on for `open project/document -> retrieve relevant material -> preview and apply or reject a patch`.

## Routing / Provider Impact Note
- None. This change does not touch routing or provider configuration.

## Scope / Ownership Note
- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Focused regression path: `tests/unit/test_commands_catalog.py`
- Approval/source note: the reviewed implementation claim is pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and only the two implementation files it touched: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`
- Integrator-locked edits: none
- Branch-tip scope note: the implementation under review is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and this handoff file are metadata only.
