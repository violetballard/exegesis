# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py`, plus focused regressions in `tests/unit/test_commands_catalog.py`; this slice locks `command_cli_contract()` to the canonical catalog surface and rejects parser drift.
- Scope clarification: this is command-contract hardening only, not new command behavior, persistence or auditability work, or a new workflow capability.
- Canonical demo-path step advanced: the Milestone 3 CLI-first control surface for `open project/document -> retrieve relevant material -> preview and apply or reject a patch`.
- Canonical MVP flow advanced: `open project/document -> retrieve relevant material -> preview and apply or reject a patch` for the manual CLI smoke flow, via `bootstrap`/`project-open` for open, `context-basket` for retrieval staging, and `diff-preview`/`review-patch` for patch preview.
- Explicit re-review statement: this `feat-commands` slice is not internal contract cleanup for its own sake; it protects the Milestone 3 CLI-first operator path by making `command_cli_contract()` fail fast when parser/catalog drift would otherwise silently break the command surface used for `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch` while Textual remains disabled.
- Demo-path sentence: this change makes the `open project/document -> retrieve relevant material -> preview and apply or reject a patch` loop more real for the CLI-first MVP path because the concrete parser-backed command entrypoints an operator runs now fail fast if parser drift changes the canonical catalog contract.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI contract from the canonical catalog, so an operator could attempt the `open project/document -> retrieve relevant material -> preview and apply or reject a patch` loop through a command surface that no longer matched the expected contract.
- Reviewed implementation commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Reviewed implementation files: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Required Gates

- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
