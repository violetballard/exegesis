# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `0da8dda9`
- Reviewed commit(s):
  - `0da8dda9` (`feat(commands): expose CLI route catalog`)

## Scope goal
- Keep the CLI command surface deterministic and smoke-testable by exposing the canonical route catalog, route summary, and smoke-surface metadata for the engine-first MVP loop.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_commands_catalog.py`

## Scope completed
- Added `route_catalog` to `CommandCliRouteContract` in `src/qual/commands/catalog.py` so the CLI route contract now carries the ordered route entries alongside parser tokens, canonical names, route summary, lookup surface, and flow surface tokens.
- Validated the new route-catalog and smoke-surface fields against the canonical helpers so `command_cli_route_contract()` stays deterministic and rejects drift.
- Extended `tests/unit/test_commands_catalog.py` with focused assertions for the route catalog, lookup surface, flow surface tokens, and the contract equality against `command_mvp_cli_route_contract()`.
- Regenerated this packet so the handoff summary, ownership note, and roadmap/vision mapping match the actual branch delta.

## Kickoff budget/limits compliance
- High-risk shared-file handoff: task budget `4`, time budget `30m`.
- The submitted branch stays within lane-owned command code plus the approved `tests/unit/test_commands_catalog.py` shared test exception.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_commands_catalog.py`.

## Tasks completed (numbered)
1. Added `route_catalog` to the CLI route contract and validated it against `command_cli_route_catalog()`.
2. Added deterministic `lookup_surface` and `flow_surface_tokens` coverage to the CLI route contract.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for the route catalog and smoke-surface fields.
4. Regenerated the packet so the review evidence matches the actual submitted diff and approved shared-file note.

## Files changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Commands run and outcomes
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers
- Risk: `MEDIUM`
- Blockers: none

## Required handoff fields
### Scope completed

- CLI command routing now exposes a deterministic route catalog and smoke-surface metadata for the engine-first MVP CLI compatibility layer.

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` - preserve CLI compatibility and migration-safe entrypoints while the command catalog now exposes deterministic route-catalog metadata for the CLI smoke surface.

### Vision capability affected

- `Canonical engine contract` - CLI compatibility remains stable while the command surface exposes deterministic route metadata for operator use.

### Routing/provider impact note

- None. This change only affects local command routing metadata and focused command-catalog test coverage.

### Proposed README patch text

- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Approved shared-file exception covers `tests/unit/test_commands_catalog.py`.
