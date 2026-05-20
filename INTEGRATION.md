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

## AGENTS Budget Enforcement (All Lanes)

Integrator must enforce `AGENTS.md` thread budgets exactly:

- Default budget: `8 tasks`
- High-risk budget: `4 tasks`
- Sprint low-risk budget: `10 tasks` only when ALL are true:
  - current date is on or before `2026-08-15`
  - lane is low-risk and stays in lane-owned paths
  - no shared/integrator-locked file edits
  - previous two handoffs from that lane were accepted without rework
  - all local gates are green before handoff

If a handoff claims `10 tasks` and any condition is missing, integrator must reject with `REJECT FOR INTEGRATION` and cite the failed sprint-mode condition.

## Reviewer Prompt (Sprint-Mode Aware)

Use this as the reviewer thread prompt:

```md
Enforce `/Users/doctor-violet/projects/exegesis/AGENTS.md` and `/Users/doctor-violet/projects/exegesis/INTEGRATION.md` exactly.

Reject by default unless all checks pass.

Budget checks (required):
- Default: max 8 tasks.
- High-risk: max 4 tasks.
- 10-task handoff allowed only if sprint-mode conditions are all satisfied:
  1) date <= 2026-08-15
  2) low-risk lane-owned paths only
  3) no shared/integrator-locked edits
  4) prior two lane handoffs accepted without rework
  5) all local gates green before handoff

If any budget condition fails, output `REJECT FOR INTEGRATION` with missing conditions.
```

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

## Lane-Specific Review Gate: `codex/feat-retrieval-fts*`

Reject handoff unless ALL conditions are met:

- Includes a completed AGENTS.md handoff packet.
- Keeps retrieval scope FTS-first for the MVP and does not reintroduce PageIndex/embeddings as required paths.
- Reports passing results for:
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
- Maps change to roadmap + product vision items per required handoff fields above.

If any condition is missing, integrator response must be `REJECT FOR INTEGRATION` with missing items listed.

## Lane-Specific Review Gate: `codex/feat-a2ui-contract*`

Reject handoff unless ALL conditions are met:

- Includes a completed AGENTS.md handoff packet.
- Preserves CLI rendering fallback for all A2UI changes.
- Keeps action handling typed/allowlisted and engine-authoritative.
- Reports passing results for:
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
- Maps change to roadmap + product vision items per required handoff fields above.

If any condition is missing, integrator response must be `REJECT FOR INTEGRATION` with missing items listed.

## Lane-Specific Review Gate: `codex/feat-engine-runs*`

Reject handoff unless ALL conditions are met:

- Includes a completed AGENTS.md handoff packet.
- Preserves architecture dependency direction per `ARCHITECTURE.md`.
- Reports passing results for:
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
- Maps change to roadmap + product vision items per required handoff fields above.

If any condition is missing, integrator response must be `REJECT FOR INTEGRATION` with missing items listed.

## Deferred Lanes

- `codex/feat-console-shell`
- `codex/feat-console-workflow`

These lanes are defined but disabled right now. Do not promote new work from them unless they are explicitly re-enabled in the router config, roadmap, and package/dependency plan.

## Retired Planning Targets

- `codex/feat-console`
- `codex/feat-ux-flow`

These legacy lanes are superseded by the staged `engine / client-textual / shared` split and should not be restarted.

## Lane-Specific Review Gate: `codex/feat-console-shell*`

Reject handoff unless ALL conditions are met:

- Includes a completed AGENTS.md handoff packet.
- The lane was explicitly enabled before work started.
- Keeps Textual shell work inside lane-owned `client-textual` paths.
- Reports passing results for:
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
- Maps change to roadmap + product vision items per required handoff fields above.

If any condition is missing, integrator response must be `REJECT FOR INTEGRATION` with missing items listed.

## Lane-Specific Review Gate: `codex/feat-console-workflow*`

Reject handoff unless ALL conditions are met:

- Includes a completed AGENTS.md handoff packet.
- The lane was explicitly enabled before work started.
- Keeps Textual workflow/card work inside lane-owned `client-textual` paths.
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
