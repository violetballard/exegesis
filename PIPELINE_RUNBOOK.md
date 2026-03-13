# Pipeline Runbook

This file is the operator-facing reference for the packet pipeline, daemon dashboard, and lane reset rules.

## Canonical Commands

- Filesystem truth: `python codex_packet_handoff/tools/status.py`
- Rich dashboard: `python codex_packet_handoff/tools/daemon_monitor.py`
- Start daemon: `python codex_packet_handoff/tools/daemon_ctl.py start`
- Stop daemon: `python codex_packet_handoff/tools/daemon_ctl.py stop`

## How To Read Status

`status.py` is the source of truth for queue state:
- `pending_feature`: feature packets waiting for reviewer
- `reviewer_notes`: active review notes waiting on feature advancement
- `approved_for_integrator`: approved packets waiting for integrator

Lane states:
- `idle`: no active packet in that lane
- `waiting_feature_update`: reviewer note exists and the lane branch has not advanced since review
- `ready_for_reemit`: reviewer note exists and the lane branch advanced; planner should emit a fresh feature packet

`daemon_monitor.py` adds runtime context:
- daemon running/stopped state
- reviewer and integrator live queues
- per-lane reviewer status
- latest fixer log summary for each lane
- backlog bottleneck classification

If `status.py` and `daemon_monitor.py` disagree, trust `status.py` for queue truth and use `daemon_monitor.py` for runtime diagnostics.

## Reset Rule

If a review/fixer cycle becomes stale:
1. Stop the daemon.
2. Archive active reviewer/feature/integrator packets out of inbox/outbox.
3. Clear planner/router transient state.
4. Keep lane heads as checkpoints, but do not re-emit packets from stale SHAs.
5. Resume only after a lane branch advances with fresh scoped work.

## Current Reset Baseline

As of `2026-03-13`:
- all five March 5 reviewer-note loops were archived as stale generation 1
- planner/router transient state was cleared
- lane metadata was rewritten for fresh current-main restarts
- no lane currently has an active packet

Current lane posture:
- `feat-commands`: restart from current main
- `feat-context-storage`: restart from current main
- `feat-ux-flow`: restart from current main
- `feat-webconsole-core`: restart from current main, high-risk template
- `feat-webconsole-ui`: restart from current main

## Required Docs For Reviewers And Fixers

These documents are the minimum context set for Codex CLI and automation:
- `AGENTS.md`
- `INTEGRATION.md`
- `THREAD_OWNERSHIP.md`
- `ROADMAP.md`
- `PRODUCT_VISION.md`
- `ARCHITECTURE.md`
- `PIPELINE_RUNBOOK.md`
