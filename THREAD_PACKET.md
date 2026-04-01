# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Final HEAD SHA: `dad3916fb8a835069fe8ef5e0a1a6c68fcd3798e`
- Reviewed implementation commit(s):
  - `f9bd51f8a85491a4343738167674adc23cc3fd47` (`Add CLI route contract helper`)
  - `dba3e806550069307b52c9d2a34268decfb3ee28` (`feat(commands): expose cli route catalog`)
  - `dad3916fb8a835069fe8ef5e0a1a6c68fcd3798e` (`Strengthen command CLI entrypoint contract`)

## Scope goal
- Harden the `feat-commands` CLI surface so the command catalog, CLI entrypoints, and smoke-route metadata stay deterministic and compatible with the canonical engine contract.

## Scope completed
- Added deterministic route-catalog helpers and wired the CLI route summary to the same ordered route catalog used by the command surface.
- Exported the new route helpers from `src/qual/commands/__init__.py` so the CLI compatibility surface can import them directly.
- Tightened `_CLI_ENTRYPOINTS` so each accepted CLI token must resolve through `COMMAND_SPECS`, keeping the parser surface catalog-backed and deterministic.
- Added focused unit coverage in `tests/unit/test_commands_catalog.py` for catalog-backed CLI lookup, route-summary parity, and rejection of unknown CLI entrypoints.
- Regenerated this handoff packet so the branch summary, file list, and required handoff fields match the submitted `feat-commands` state.

## Files changed

### Implementation files changed

- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`

### Shared-by-approval files changed

- `tests/unit/test_commands_catalog.py` (shared-by-approval only)

### Docs-only alignment files changed

- `THREAD_PACKET.md` (handoff artifact)

## Tasks completed

1. Added the deterministic route-catalog helpers used by the CLI route summary.
2. Exported the new route helpers from the command package surface.
3. Hardened CLI entrypoints so accepted tokens resolve through the command catalog.
4. Added focused tests for catalog-backed lookup, route parity, and unknown-entrypoint rejection.
5. Regenerated the handoff packet to match the branch tip and actual file list.

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

- Hardened the `feat-commands` CLI surface so the parser entrypoints, route catalog, and smoke-flow metadata stay deterministic and align with the canonical engine contract.

### Roadmap item(s) affected

- `Milestone 2: Core pane interactions` - the stable command surface is part of the command-palette coverage the MVP loop needs.
- `Milestone 3: Real workflow loop` - CLI compatibility and migration-safe entrypoints stay stable while the canonical engine contract lands.

### Vision capability affected

- `3. Canonical engine contract` - CLI compatibility remains stable while the command surface resolves through the canonical catalog.
- `5. Keyboard-first client behavior` - the deterministic command surface is a prerequisite for future command-palette and shortcut flows.

### Routing/provider impact note

- None. This change only affects local command-surface route and entrypoint metadata; no routing/provider files change.

### Proposed README patch text

- None

### Ownership / approval note

- Shared/integrator-locked edits: `YES`. `tests/unit/test_commands_catalog.py` is shared-by-approval only and is included for focused CLI-entrypoint coverage.
