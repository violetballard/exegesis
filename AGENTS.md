# Agent Operating Guide

This file defines how long feature threads should run before review/integration handoff.

Template selection rule: use `Thread Kickoff Template` by default, and use `High-Risk Thread Kickoff Template` whenever shared/integrator-locked files or provider/routing/core entrypoints are likely to be touched.

## Recommended Thread Size

- Default: `8 tasks` per feature thread.
- Low-risk lanes: up to `8 tasks` by default; up to `10` only under `Timeline Sprint Mode` rules below.
- High-risk work: cap at `4 tasks` when touching shared or integrator-locked files.

Why not 10 by default:
- At this repo's current size, 10-task batches increase conflict and rework risk at integration.
- 8-task batches improve throughput while keeping review scope manageable.

## Timeline Sprint Mode (Temporary)

Active window: now through `2026-08-15` (RC freeze window).

- During this window:
  - default remains `8`
  - low-risk threads may run at `10` only if ALL are true:
    - changes stay in lane-owned paths only
    - no shared/integrator-locked file edits
    - previous `2` handoffs from that lane were accepted without rework
    - all local gates are green before handoff
- After `2026-08-15`, revert low-risk cap to `8` unless integrator re-authorizes.

## Task Definition

A task is one meaningful, testable unit (not a tiny edit), for example:
- add one command flag + validation + tests
- implement one retrieval path + tests
- add one UI interaction flow + tests

Do not split tasks into trivial subtasks to inflate counts.

## Autonomy Window

A thread may continue without passoff until it hits one of these:
- Task budget reached (`8` default, `10` sprint low-risk, `4` high-risk)
- Time budget reached (`45 minutes` active coding)
- Size budget exceeded:
  - more than `12 files` changed, or
  - more than `500` net LOC changed

## Mandatory Stop Triggers

Immediate handoff to review/integration if any trigger fires:
- Editing integrator-locked files listed in `THREAD_OWNERSHIP.md`
- Editing shared-by-approval files without explicit approval
- Test/lint/typecheck failure not resolved after `2` focused fix attempts
- Scope check failure (`make scope-check`) that cannot be resolved cleanly

## Required Checkpoints (Short Status, Not Full Handoff)

Post a short update at these points:
- plan complete
- first green local tests
- before first edit to any risky/shared file
- final "ready for handoff" state

## Handoff Readiness

Before passoff, thread must provide:
- branch name
- tasks completed (numbered)
- files changed
- commands run and outcomes
- remaining risks or blockers

And run:
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`

Use full required handoff fields from `INTEGRATION.md`.

## Quick Start Defaults

Use these unless the integrator overrides:
- `TASK_BUDGET=8`
- `TIME_BUDGET_MIN=45`
- `MAX_FILES_CHANGED=12`
- `MAX_NET_LOC=500`
- `MAX_FIX_ATTEMPTS=2`

## Thread Kickoff Template

Copy/paste this at thread start and fill it in:

```md
## Thread Kickoff

- Branch: `codex/feat-<name>`
- Lane/owned paths: `<from THREAD_OWNERSHIP.md>`
- Scope goal: `<1-2 sentence outcome>`

### Budget
- Task budget: `8` (set `10` only in Timeline Sprint Mode for low-risk owned-path work, `4` for high-risk/shared work)
- Time budget: `45m`
- Size limits: `<=12 files`, `<=500 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 8 by default)
1. `<task 1: meaningful + testable>`
2. `<task 2>`
3. `<task 3>`
4. `<task 4>`
5. `<task 5>`
6. `<task 6>`
7. `<task 7>`
8. `<task 8>`

### Stop Triggers
- integrator-locked/shared-by-approval edits needed
- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)
- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

### Handoff Packet
- branch name
- tasks completed (numbered)
- files changed
- commands run + outcomes
- risks/blockers
- all required fields from `INTEGRATION.md`
```

## High-Risk Thread Kickoff Template

Use this variant when shared/integrator-locked files are likely, or when routing/provider/core app entrypoints are in scope.

```md
## Thread Kickoff (High-Risk)

- Branch: `codex/feat-<name>`
- Lane/owned paths: `<from THREAD_OWNERSHIP.md>`
- Scope goal: `<1-2 sentence outcome>`
- Risk reason: `<why this is high-risk>`

### Budget
- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)
1. `<task 1: meaningful + testable>`
2. `<task 2>`
3. `<task 3>`
4. `<task 4>`

### Early Review Triggers
- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers
- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)
- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

### Handoff Packet
- branch name
- tasks completed (numbered)
- files changed
- commands run + outcomes
- risks/blockers
- all required fields from `INTEGRATION.md`
```

## Thread Kickoff - feat-webconsole-ui (2026-03-04)

- Branch: `codex/feat-webconsole-ui`
- Lane/owned paths: `src/qual/webconsole/**`
- Scope goal: Deliver keyboard-first reconnect and auto-retry controls in the SSE terminal so operators can recover streams without grabbing the mouse, and surface those shortcuts inline so they are discoverable.

### Budget
- Task budget: `8` (this thread uses 3 tasks)
- Time budget: `45m` (planned work fits inside one 30-35m block)
- Size limits: `<=12 files`, `<=500` net LOC (expected: 3 files / ~45 LOC)
- Max fix attempts per failing gate: `2`

### Planned Tasks
1. Add an `Alt+R` keyboard shortcut that triggers the reconnect action, respects disabled states, and resets retry metadata.
2. Add an `Alt+A` shortcut that toggles auto-retry, syncs the button label, and keeps retry timers consistent with manual overrides.
3. Surface shortcut hints plus focus-stable styling in the terminal template/CSS so operators immediately see and can trust the new affordances.

### Stop Triggers
- integrator-locked/shared-by-approval edits needed
- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence
- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Thread Handoff - feat-webconsole-ui (2026-03-04)

- Branch: `codex/feat-webconsole-ui`
- Scope completed: Terminal stream reconnect controls now expose Alt+R (manual reconnect) and Alt+A (auto-retry toggle) shortcuts plus inline hints so the keyboard-only workflow matches mouse controls.
- Kickoff limits observed: Stayed within the default `feat-webconsole-ui` lane gate (`<=8` tasks / `<=45m` / `<=12` files / `<=500` net LOC / max `2` fix attempts) by shipping 3 tasks across 3 files (~45 LOC) in ~35m, so reviewers can tick the compliance box called out in `INTEGRATION.md`.
- Roadmap item(s): Milestone 5 - A2UI Presentation Layer (terminal/web-console usability slice).
- Product vision capability: #4 Operator-first control surface and #5 Agent-to-UI protocol (shortcut parity keeps console state in sync across clients).

### Tasks Completed
1. Wire the Alt+R keyboard listener to the reconnect action, including disabled-state guarding and retry counter reset logic in `webconsole.js`.
2. Wire the Alt+A listener so the auto-retry toggle updates UI state, button copy, and underlying retry timers in `webconsole.js`.
3. Expose shortcut hints and monospace styling in `terminal.html`/`webconsole.css` so operators discover the new controls directly in the panel header.

### Files Changed
- `src/qual/webconsole/static/webconsole.css`
- `src/qual/webconsole/static/webconsole.js`
- `src/qual/webconsole/templates/terminal.html`

### Commands Run
- `make scope-check` - PASS (2026-03-04)
- `./quality-format.sh --check` - PASS (2026-03-04)
- `./quality-lint.sh` - PASS (2026-03-04) *(trimmed trailing whitespace in `feat-webconsole-ui-fix.patch` to satisfy lint)*
- `./quality-test.sh` - PASS (2026-03-04)
- `./typecheck-test.sh` - PASS (2026-03-04)
- `make ci` - PASS (2026-03-04)

### Risks / Blockers
- None; reconnect controls remain scoped to owned webconsole paths and reuse existing SSE helpers.
