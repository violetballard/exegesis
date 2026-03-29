## Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Final HEAD SHA: `15103c92584694742e044ade321fab83b67a9478`
- Reviewed implementation commit(s):
  - `15103c92584694742e044ade321fab83b67a9478`

## Scope goal

Expose an explicit `command_mvp_surface_contract` alias on the `feat-commands` command surface while keeping the CLI-compatible command catalog and contract projections stable.

## Scope completed

- Added `command_mvp_surface_contract` in `src/qual/commands/catalog.py` and re-exported it from `src/qual/commands/__init__.py` so the MVP surface has an explicit importable alias.
- Routed `command_mvp_flow_contract` and `command_surface_contract` through the new alias so the public surface contract stays a single shared object.
- Added focused command-catalog regression coverage in `tests/unit/test_commands_catalog.py` to verify the new alias stays aligned with the public surface contract and MVP flow contract.
- Regenerated the handoff packet from the actual `main..codex/feat-commands` delta and aligned scope-check policy with the approved `tests/unit/test_commands_catalog.py` shared test.

## Files changed

- `src/qual/commands/__init__.py` (lane-owned)
- `src/qual/commands/catalog.py` (lane-owned)
- `tests/unit/test_commands_catalog.py` (approved shared file)
- `scripts/scope-check.sh` (policy-support edit for the approved shared test)
- `THREAD_PACKET.md` (handoff artifact)

## Tasks completed

1. Added the explicit `command_mvp_surface_contract` alias and exported it from the public command package.
2. Unified the public surface-contract helpers through the new alias so MVP and public entrypoints stay identical.
3. Added focused catalog coverage for the alias and contract alignment.
4. Regenerated the handoff packet and scope-check policy so the submitted branch matches the actual diff and passes scope checking.

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

- `feat-commands` - CLI compatibility and migration-safe entrypoints, specifically the `command_mvp_surface_contract` alias and its command-catalog contract alignment.

### Vision capability affected

- Capability 4 - Operator-first control surface: the engine-facing command surface now exposes an explicit MVP contract alias while keeping CLI-compatible exports stable and deterministic for CLI-first automation.

### Routing/provider impact note

- None. This change only affects local command-surface aliases, command-contract verification, and the approved scope-check policy for the shared test.

## Approved exception note

- Approved shared-file exception for `tests/unit/test_commands_catalog.py`.

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Approved shared-file exception: `tests/unit/test_commands_catalog.py`
- Policy-support edit: `scripts/scope-check.sh` permits the approved `tests/unit/test_commands_catalog.py` shared test during `make scope-check`.
