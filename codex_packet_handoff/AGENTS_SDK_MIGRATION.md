# Agents SDK Migration Plan (Codex MCP)

## Goal

Replace the current script-driven planner/router loop with an Agents SDK coordinator that keeps the same lane semantics:

- feature handoff packets
- reviewer verdicts
- required fixes routed back to feature lanes
- integrator merge flow

## Non-Goals

- No behavior change to lane ownership policy.
- No bypass of filesystem permissions. Automation still needs writable workspace access.
- No immediate removal of existing scripts until parity is verified.

## Current Components To Preserve

- `codex_packet_handoff/tools/planner.py`
- `codex_packet_handoff/tools/router.py`
- `codex_packet_handoff/tools/status.py`
- packet filesystem contracts under `.codex/packets/lanes/*`
- planner state under `.codex/packet_planner/state.json`
- router state under `.codex/packet_router/state.json`

## Target Architecture

1. `CoordinatorAgent`
- Runs on automation cadence.
- Calls planner/reviewer/fixer/integrator agents in sequence.
- Owns run summary and retry policy.

2. `PlannerAgent`
- Reads branch heads + planner state.
- Emits `F__*.md` packets when lane has advanced and gates pass.

3. `ReviewerAgent` (read-only)
- Consumes `F__*.md`.
- Produces `R__APPROVED__*.md` or `R__CHANGES__*.md`.

4. `FixerAgent` (workspace-write)
- Consumes reviewer changes packets.
- Applies required fixes on lane branch worktree.
- Commits and advances lane head.

5. `IntegratorAgent` (workspace-write)
- Consumes approved packets.
- Runs merge order and required post-merge gates.

6. MCP tools
- Codex MCP server for code actions and filesystem work.
- Optional Docs MCP for deterministic doc lookups during orchestration logic.

## Rollout Phases

## Phase 0: Permissions + Runtime Baseline

1. Keep automation at:
- `execution_environment = "workspace"`
- `cwds = ["/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual"]`

2. Verify runner can write:
- `.codex/packets`
- `.codex/packet_planner`
- `.codex/packet_router`

Acceptance:
- A one-tick run can create/update all above paths without permission errors.

## Phase 1: Coordinator Wrapper Around Existing Scripts

1. Add `codex_packet_handoff/tools/agents_coordinator.py`.
2. In this phase, coordinator calls existing `planner.py` and `router.py` as subprocess tools.
3. Emit a single structured summary per tick.

Acceptance:
- Same outputs as current automation tick for equal inputs.

## Phase 2: Replace Router Decisions With Reviewer/Fixer/Integrator Agents

1. Implement agent roles:
- reviewer (read-only)
- fixer (workspace-write)
- integrator (workspace-write)

2. Keep existing packet files as the source of truth.
3. Preserve reviewer-backlog handback behavior and cursor semantics.

Acceptance:
- Re-review loop works end-to-end across all five lanes without manual intervention.

## Phase 3: Replace Planner Logic With PlannerAgent

1. Move planner gating logic into PlannerAgent.
2. Preserve lane-meta validation/defaulting, scope-check, and required gates.
3. Keep packet naming/format stable.

Acceptance:
- Planner emits identical packet shape and state transitions as current planner script.

## Phase 4: Decommission Legacy Scripts

1. Freeze old scripts for one release.
2. Switch automation prompt to coordinator-only command.
3. Keep `status.py` as independent observer.

Acceptance:
- One full 50-minute cycle with zero regressions in packet flow.

## State + Contracts

Required invariant:

- Status truth remains filesystem-first.
- `status.py` must continue to classify:
  - `pending_review`
  - `waiting_feature_update`
  - `ready_for_reemit`
  - `ready_for_integrator`

Packet contract invariant:

- Do not change `F__`, `R__CHANGES__`, `R__APPROVED__` filename conventions during migration.

## Risks

1. Agent deadlocks on long MCP calls.
- Mitigation: keep detached fixer fallback path.

2. Reviewer empty output.
- Mitigation: keep recovery path that reconstructs actionable prompt from archived feature packet.

3. Cursor drift skipping packets.
- Mitigation: preserve fixed `list_new` behavior when last-seen packet is archived.

4. Hidden automation state mismatch (TOML vs DB).
- Mitigation: coordinator startup check logs current automation status and next run.

## Cutover Checklist

1. One-cycle dry run:
- planner emits expected packets
- reviewer produces non-empty verdicts
- fixer advances at least one lane
- planner re-emits for advanced lane

2. One-cycle live run:
- all lanes enter valid state transitions
- no permission errors
- no skipped packets

3. Post-cutover:
- status report remains accurate
- automation visible as `ACTIVE`

## Recommended Automation Prompt (Coordinator Cutover)

Use this once coordinator is implemented:

`Run the agents coordinator for one full 50-minute cycle using workspace mode. Enforce planner/reviewer/fixer/integrator handoff rules, keep packet/state compatibility with existing lane files, and output a single end-of-cycle summary with emissions, reviews, fixer advances, and integration results.`

