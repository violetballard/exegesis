# Agent Operating Guide

This file defines how long feature threads should run before review/integration handoff.

Template selection rule: use `Thread Kickoff Template` by default, and use `High-Risk Thread Kickoff Template` whenever shared/integrator-locked files or provider/routing/core entrypoints are likely to be touched.

## Recommended Thread Size

- Default: `6 tasks` per feature thread.
- Low-risk lanes: up to `8 tasks` if changes stay inside owned paths from `THREAD_OWNERSHIP.md`.
- High-risk work: cap at `4 tasks` when touching shared or integrator-locked files.

Why not 10 by default:
- At this repo's current size, 10-task batches increase conflict and rework risk at integration.
- 6-task batches are large enough to reduce babysitting but small enough to keep review fast.

## Task Definition

A task is one meaningful, testable unit (not a tiny edit), for example:
- add one command flag + validation + tests
- implement one retrieval path + tests
- add one UI interaction flow + tests

Do not split tasks into trivial subtasks to inflate counts.

## Autonomy Window

A thread may continue without passoff until it hits one of these:
- Task budget reached (`6` default, `8` low-risk, `4` high-risk)
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
- `TASK_BUDGET=6`
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
- Task budget: `6` (set `8` only for low-risk owned-path work, `4` for high-risk/shared work)
- Time budget: `45m`
- Size limits: `<=12 files`, `<=500 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 6 by default)
1. `<task 1: meaningful + testable>`
2. `<task 2>`
3. `<task 3>`
4. `<task 4>`
5. `<task 5>`
6. `<task 6>`

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
