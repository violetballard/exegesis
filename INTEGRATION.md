# Integration Runbook

See `ROADMAP.md` for milestone status and sprint cadence.

## Ownership

- `README.md` is integrator-owned.
- Contributor lanes must not edit `README.md`.
- Contributor lanes include proposed README diff text in handoff notes if documentation changes are needed.

## Merge Order

1. `codex/quality-baseline`
2. `codex/infra-devex`
3. feature lanes

## Required Gate Before Merge

- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`

## Required Handoff Fields

- Branch name
- Scope completed
- Files changed
- Commands run with results
- Risks/blockers
- Proposed `README.md` patch text (optional)
