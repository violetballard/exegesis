# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `932f2320`

## Scope goal
- Tighten the command surface for the engine-first MVP so flow-step labels resolve to the current command specs without changing the existing manifest shape.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Added internal flow-step fallback lookup so `command_spec()` and `canonical_command()` accept the MVP flow vocabulary for `project-open`, `retrieval`, `patch-review`, and `export-handoff`.
- Kept the published command manifest and surface contract stable for existing consumers.
- Stayed inside the lane-owned command package for the code change.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The branch delta for this turn is 1 code file plus this handoff packet update.

## Tasks completed (numbered)
1. Added flow-step fallback lookup to the command catalog.
2. Verified the command catalog unit tests and repo quality gates.
3. Regenerated the handoff packet with the current branch tip and blocker note.

## Files changed for this turn
- `src/qual/commands/catalog.py`
- `THREAD_PACKET.md`

## Commands run and outcomes
- `python -m unittest tests.unit.test_commands_catalog`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: FAIL
- `SCOPE_ALLOW_SHARED=1 make ci`: PASS

## Risks / blockers
- Risk: `LOW`
- Blocker: default `make ci` fails scope-check because the current `codex/feat-commands` branch history still includes pre-existing disallowed changes in `tests/unit/test_commands_catalog.py`.
- Note: no new shared/integrator-locked edits were introduced in this turn.

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: command-surface hardening for the CLI-first MVP flow.
- Milestone 5 - A2UI Presentation Layer: supports the CLI-driven bootstrap/retrieval/patch-review/export handoff path.

### Vision capability affected
- Capability 4 - Operator-first control surface: the CLI command surface now resolves the flow-step vocabulary used by the MVP demo flow.
- Capability 5 - Agent-to-UI protocol (`A2UI`): the command surface stays aligned with the CLI-first path that will consume structured A2UI outputs.

### Routing/provider impact note
- None. This change only affects local command lookup behavior in `src/qual/commands/**`.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `NO`
