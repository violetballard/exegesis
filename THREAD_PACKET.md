## Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Final HEAD SHA: `7f4de16e3141dfd24e942ef3e47325d65962a279`
- Scope goal: Add a deterministic CLI flow smoke contract so parser tokens, canonical command names, and normalized MVP flow steps stay explicit for CLI-first operator use.

## Scope completed

- Added `CommandCliFlowEntry` and `CommandCliFlowContract` plus `command_cli_flow_contract()` and `command_cli_flow_lookup_table()` in `src/qual/commands/catalog.py`.
- Exported the new CLI-flow contract symbols from `src/qual/commands/__init__.py`.
- Added focused unit coverage in `tests/unit/test_commands_catalog.py` that pins parser tokens, canonical command names, and MVP flow-step mapping together.
- Approved the shared-file exception for `tests/unit/test_commands_catalog.py` so the lane can add the required contract coverage.

## Files changed

- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `tests/unit/test_commands_catalog.py`

## Tasks completed

1. Added a deterministic CLI-to-flow contract for the MVP smoke path.
2. Exported the new contract helpers from the command package.
3. Added unit tests for the new contract and lookup table.
4. Recorded the explicit shared-file approval for `tests/unit/test_commands_catalog.py`.

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

### Shared-file approval note

- Approved shared-file exception for `tests/unit/test_commands_catalog.py` to add focused CLI-flow contract coverage.

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
- `Milestone 2: Test Hardening`

### Vision capability affected

- `Operator-first control surface`

### Routing/provider impact note

- None. This change only affects local command-surface lookup contracts and parser-surface validation.
