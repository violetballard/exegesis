## Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Final HEAD SHA: `a5b0a247f2bf97ee233a8a458230a1bdda0b9dc4`
- Reviewed implementation commit(s):
  - `a5b0a247f2bf97ee233a8a458230a1bdda0b9dc4`
- Docs-only alignment commit(s):
  - `da122acb7f5454db56b5df39186b50ac0857e14a`
  - `da334f66ea8030060b04b15e878aa7840c6c8c5a`

## Scope goal

Add grouped command smoke tokens to the command catalog so the public and MVP surface contracts expose deterministic grouped flow-surface projections for CLI smoke checks.

## Scope completed

- Added `command_flow_surface_tokens` and `command_mvp_flow_surface_tokens` exports in `src/qual/commands/__init__.py` so grouped smoke-token projections are part of the public command API.
- Extended `src/qual/commands/catalog.py` with grouped flow-surface token projections and surface-contract wiring so `CommandSurfaceContract.flow_surface_tokens` stays aligned with the MVP/demo smoke path.
- Added focused unit coverage in `tests/unit/test_commands_catalog.py` for grouped surface-token ordering, MVP/public contract alignment, and flow-surface token exposure.
- Regenerated the handoff packet so the branch summary, file list, and ownership mapping match the actual `a5b0a247` command-surface delta.

## Files changed

### Implementation files changed

- `src/qual/commands/__init__.py` (lane-owned)
- `src/qual/commands/catalog.py` (lane-owned)
- `tests/unit/test_commands_catalog.py` (approved shared test; whitelisted in `scripts/scope-check.sh`)

### Docs-only alignment files changed

- `THREAD_PACKET.md` (handoff artifact)

## Tasks completed

1. Exported grouped flow-surface token helpers from `src/qual/commands/__init__.py`.
2. Wired grouped flow-surface token projections into `src/qual/commands/catalog.py` and exposed them through the command surface contract.
3. Added regression coverage for grouped command smoke tokens and contract alignment in `tests/unit/test_commands_catalog.py`.
4. Regenerated the handoff packet so the feature summary matches the actual reviewed command-surface commit.

## Commands run and outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Risk: `LOW`
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 1: Bootstrap Flow Stabilization` - command-surface hardening for the CLI-first command surface.
- `Milestone 2: Test Hardening` - focused grouped-smoke regression coverage for the catalog test path.

### Vision capability affected

- `Operator-first control surface` - CLI remains a first-class surface, and command contracts stay deterministic for operator-driven flows.

### Routing/provider impact note

- None. This change only affects local command-surface token projections, contract bundling, and focused command-catalog test coverage.

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES` (approved shared test only)
- Approved shared-file exception: `tests/unit/test_commands_catalog.py` (explicitly approved for `codex/feat-commands`; whitelisted in `scripts/scope-check.sh`)
