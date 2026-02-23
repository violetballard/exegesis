# Integration Runbook

See `ROADMAP.md` for milestone status and sprint cadence.
See `ARCHITECTURE.md` for module boundaries and dependency guardrails.
See `PRODUCT_VISION.md` for non-negotiable product goals.

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
- Roadmap item(s) affected (from `ROADMAP.md`)
- Vision capability affected (from `PRODUCT_VISION.md`)
- Routing/provider impact note (if model routing or provider configuration is touched)
- Proposed `README.md` patch text (optional)

## Lane-Specific Review Gate: `codex/feat-commands*`

Reject handoff unless ALL conditions are met:

- Includes a completed AGENTS.md handoff packet.
- Scope remains in lane-owned paths from `THREAD_OWNERSHIP.md` OR includes explicit approval note for shared/integrator-locked edits.
- Reports passing results for:
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
- Maps change to roadmap + product vision items per required handoff fields above.

If any condition is missing, integrator response must be `REJECT FOR INTEGRATION` with missing items listed.

## Lane-Specific Review Gate: `codex/feat-webconsole-ui`

Reject handoff unless ALL conditions are met:

- Includes a completed AGENTS.md handoff packet.
- Explicitly states kickoff budget/limits compliance.
- Scope stays within UI-owned paths from `THREAD_OWNERSHIP.md`:
  - `src/qual/webconsole/render/**`
  - `src/qual/webconsole/templates/**`
  - `src/qual/webconsole/static/**`
- Reports passing results for:
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
- Maps change to roadmap + product vision items per required handoff fields above.

If any condition is missing, integrator response must be `REJECT FOR INTEGRATION` with missing items listed.

## Lane-Specific Review Gate: `codex/feat-webconsole-core`

Reject handoff unless ALL conditions are met:

- Includes a completed AGENTS.md handoff packet.
- Uses High-Risk kickoff limits OR documents approved exception:
  - `4 tasks`
  - `30m`
  - `<=8 files`
  - `<=300 net LOC`
- Reports passing results for:
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
- Maps change to roadmap + product vision items per required handoff fields above.

If any condition is missing, integrator response must be `REJECT FOR INTEGRATION` with missing items listed.

## Lane-Specific Review Gate: `codex/feat-ux-flow*`

Reject handoff unless ALL conditions are met:

- Includes a completed AGENTS.md handoff packet.
- Stays within kickoff budget/limits (or documents approved exception).
- Preserves architecture dependency direction per `ARCHITECTURE.md`.
- Reports passing results for:
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
- Maps change to roadmap + product vision items per required handoff fields above.

If any condition is missing, integrator response must be `REJECT FOR INTEGRATION` with missing items listed.

## Lane-Specific Review Gate: `codex/feat-context-storage*`

Reject handoff unless ALL conditions are met:

- Includes a completed AGENTS.md handoff packet.
- Stays within kickoff budget/limits (or documents approved exception).
- Keeps storage/context ownership boundaries intact per `THREAD_OWNERSHIP.md` and `ARCHITECTURE.md`.
- Reports passing results for:
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
- Maps change to roadmap + product vision items per required handoff fields above.

If any condition is missing, integrator response must be `REJECT FOR INTEGRATION` with missing items listed.
