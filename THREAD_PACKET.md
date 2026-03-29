## Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Final HEAD SHA: `7f4de16e3141dfd24e942ef3e47325d65962a279`
- Scope goal: Tighten the CLI command surface so the parser contract and CLI-to-flow mapping are deterministic for the current MVP demo route.

## Scope completed

- Added `CommandCliFlowEntry` and `CommandCliFlowContract` plus `command_cli_flow_contract()` and `command_cli_flow_lookup_table()` in `src/qual/commands/catalog.py`.
- Exported the new CLI-flow contract symbols from `src/qual/commands/__init__.py`.
- Added unit coverage that pins the parser token, canonical command, and MVP flow-step mapping together in `tests/unit/test_commands_catalog.py`.

## Files changed

- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `tests/unit/test_commands_catalog.py`

## Tasks completed

1. Added a deterministic CLI-to-flow contract for the MVP smoke path.
2. Exported the new contract helpers from the command package.
3. Added unit tests for the new contract and lookup table.

## Commands run and outcomes

- `python -m unittest tests.unit.test_commands_catalog` PASS
- `make scope-check` PASS
- `./quality-format.sh --check` PASS
- `./quality-lint.sh` PASS
- `./quality-test.sh` PASS
- `./typecheck-test.sh` PASS
- `make ci` PASS

## Risks / blockers

- Risk: LOW
- Blockers: none

## Required handoff fields

### Scope completed

- Tightened the command surface with an explicit CLI-to-flow mapping for the current MVP smoke path.

### Files changed

- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `tests/unit/test_commands_catalog.py`

### Commands run with results

- `python -m unittest tests.unit.test_commands_catalog` PASS
- `make scope-check` PASS
- `./quality-format.sh --check` PASS
- `./quality-lint.sh` PASS
- `./quality-test.sh` PASS
- `./typecheck-test.sh` PASS
- `make ci` PASS

### Risks/blockers

- Low risk and no blockers.

### Roadmap item(s) affected

- `Milestone 1: Bootstrap Flow Stabilization`
- `Milestone 5: A2UI Presentation Layer`

### Vision capability affected

- `Operator-first control surface`

### Routing/provider impact note

- None. This change only affects local command-surface lookup contracts and parser-surface validation.
