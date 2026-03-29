## Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Final HEAD SHA: `15103c92584694742e044ade321fab83b67a9478`
- Reviewed implementation commit(s):
  - `22ce0e2023cf2bfa03fb5cfc2ba035cf8e92e8c3`
  - `15103c92584694742e044ade321fab83b67a9478`
- Docs-only alignment commit(s):
  - `07ae98b19e44d7b30c8ee490295cd91577ae0f7b`

## Scope goal

Expose an explicit `command_mvp_surface_contract` alias on the `feat-commands` command surface while keeping the CLI-compatible command catalog and contract projections stable.

## Scope completed

- Added `command_mvp_surface_contract` in `src/qual/commands/catalog.py` and re-exported it from `src/qual/commands/__init__.py` so the MVP surface has an explicit importable alias.
- Routed `command_mvp_flow_contract` and `command_surface_contract` through the new alias so the public surface contract stays a single shared object.
- Added focused command-catalog regression coverage in `tests/unit/test_commands_catalog.py` to verify the new alias stays aligned with the public surface contract and MVP flow contract.
- Regenerated the handoff packet from the actual `codex/feat-commands` tip and aligned scope-check policy with the approved `tests/unit/test_commands_catalog.py` shared test, while keeping the docs/policy alignment files separate from the 3-file implementation delta.

## Files changed

### Implementation files changed

- `src/qual/commands/__init__.py` (lane-owned)
- `src/qual/commands/catalog.py` (lane-owned)
- `tests/unit/test_commands_catalog.py` (approved shared file)

### Docs/policy alignment files changed

- `scripts/scope-check.sh` (policy-support edit for the approved shared test)
- `THREAD_PACKET.md` (handoff artifact)

## Tasks completed

1. Added the explicit `command_mvp_surface_contract` alias and exported it from the public command package.
2. Unified the public surface-contract helpers through the new alias so MVP and public entrypoints stay identical.
3. Added focused catalog coverage for the alias and contract alignment.
4. Regenerated the handoff packet and scope-check policy so the submitted branch matches the actual diff, passes scope checking, and keeps docs/policy alignment separate from the implementation delta.

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

- `MVP Focus Through 2026-05-04: feat-commands` - active lane for CLI-compatible command-surface hardening.

### Vision capability affected

- Capability 4 - Operator-first control surface: CLI remains a first-class surface, and engine contracts stay stable for CLI-first automation and future `Exegesis Console` consumption.

### Routing/provider impact note

- None. This change only affects local command-surface aliases, command-contract verification, and the approved scope-check policy for the shared test.

## Approved exception note

- Approved shared-file exception for `tests/unit/test_commands_catalog.py`.

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES` (approved shared test only)
- Approved shared-file exception: `tests/unit/test_commands_catalog.py`
- Policy-support edit: `scripts/scope-check.sh` permits the approved `tests/unit/test_commands_catalog.py` shared test during `make scope-check`.
