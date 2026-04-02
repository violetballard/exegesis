# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Final HEAD SHA: `dad3916fb8a835069fe8ef5e0a1a6c68fcd3798e`
- Reviewed implementation commit(s):
  - `dad3916fb8a835069fe8ef5e0a1a6c68fcd3798e` (`Strengthen command CLI entrypoint contract`)

## Scope goal
- Harden the `feat-commands` CLI surface so accepted entrypoints stay catalog-backed and deterministic for CLI-first operator use.

## Scope completed
- Tightened `_CLI_ENTRYPOINTS` so each accepted CLI token must resolve through `COMMAND_SPECS`, keeping the parser surface catalog-backed and deterministic.
- Added focused unit coverage in `tests/unit/test_commands_catalog.py` for catalog-backed CLI lookup and rejection of unknown CLI entrypoints.
- Regenerated this handoff packet so the branch summary, file list, and required handoff fields match the submitted `feat-commands` state.

## Files changed

### Implementation files changed

- `src/qual/commands/catalog.py`

### Shared-by-approval files changed

- `tests/unit/test_commands_catalog.py` (shared-by-approval only)

### Docs-only alignment files changed

- `THREAD_PACKET.md` (handoff artifact)

## Tasks completed

1. Hardened CLI entrypoints so accepted tokens resolve through the command catalog.
2. Added focused tests for catalog-backed lookup and unknown-entrypoint rejection.
3. Regenerated the handoff packet to match the reviewed command-contract delta.

## Commands run and outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Risk: LOW
- Blockers: none

## Required handoff fields

### Scope completed

- Hardened the `feat-commands` CLI surface so parser entrypoints stay deterministic and align with the canonical engine contract.

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` - CLI compatibility and migration-safe entrypoints stay stable while the canonical engine contract lands.

### Vision capability affected

- `3. Canonical engine contract` - CLI compatibility remains stable while the command surface resolves through the canonical catalog.

### Routing/provider impact note

- None. This change only affects local command-surface route and entrypoint metadata; no routing/provider files change.

### Proposed README patch text

- None

### Ownership / approval note

- Shared/integrator-locked edits: `YES`.
- Explicit approval covers `tests/unit/test_commands_catalog.py`, which is shared-by-approval only and is included for focused CLI-entrypoint coverage.
