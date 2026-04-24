# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py`, plus focused regressions in `tests/unit/test_commands_catalog.py`; this slice locks `command_cli_contract()` to the canonical catalog surface and rejects parser drift.
- Scope clarification: this is command-contract hardening only, not new command behavior, persistence or auditability work, or a new workflow capability.
- Canonical demo-path step advanced: the Milestone 3 CLI-first `open project/document` control surface that keeps the operator in the manual MVP loop while Textual remains disabled.
- Canonical MVP flow context: `open project/document -> retrieve relevant material -> preview and apply or reject a patch` for the manual CLI smoke flow, with this slice specifically hardening the parser-backed command surface that starts and preserves that operator path.
- Explicit re-review statement: this `feat-commands` slice is not internal contract cleanup for its own sake; it is in-plan Milestone 3 CLI-first hardening because `command_cli_contract()` now fails fast when parser/catalog drift would otherwise silently break the operator-facing CLI surface that the `open project/document` entry step and the rest of the manual MVP loop depend on while Textual remains disabled.
- Demo-path sentence: this change makes the CLI-first MVP path more real by ensuring the concrete parser-backed command entrypoints an operator uses to open project or document state cannot silently drift away from the canonical catalog before the rest of the loop runs.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI contract from the canonical catalog, so an operator could start the manual MVP loop through an `open project/document` surface that no longer matched the expected contract.
- Reviewed implementation commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Reviewed implementation files: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Required Gates

- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
