# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: command-catalog contract hardening plus one shared regression for alias-level parser drift
- Canonical demo-path step advanced: `preview and apply or reject a patch`
- Explicit re-review statement: the current branch tip is the review target, and the `diff-preview` patch-review CLI surface now fails fast if alias-level parser drift changes the `diff` token while canonical command names still appear stable.
- Latest verification rerun: `2026-04-24T11:50:50Z`

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Required Gates

- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_mutated_diff_alias_with_stable_canonical_names`
- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
