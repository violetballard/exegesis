# Pipeline Runbook

This file is the operator-facing reference for the packet pipeline, daemon dashboard, and lane reset rules.

## Canonical Commands

- Filesystem truth: `python codex_packet_handoff/tools/status.py`
- Rich dashboard: `python codex_packet_handoff/tools/daemon_monitor.py`
- Start daemon: `python codex_packet_handoff/tools/daemon_ctl.py start`
- Stop daemon: `python codex_packet_handoff/tools/daemon_ctl.py stop`
- Process view: `ps -axo pid,etime,command | rg "codex exec|codex_packet_handoff/tools/agents_coordinator.py" || true`
- Manual feature logs: `ls -1t .codex/feature_runner/logs/*.log | head`

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

Manual feature sessions are separate from the daemon:
- feature lanes may also be running as direct Codex CLI sessions outside the daemon
- inspect them with the process view and `.codex/feature_runner/logs/`
- if queue state is idle but feature sessions are active, the pipeline is waiting for new commits rather than stuck

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

## Managed Sessions

Control-plane managed Codex sessions:
- one reviewer session per lane
- one integrator session

Feature work may run in either of two modes:
- daemon-triggered reviewer/fixer/integrator flow
- manual feature-lane Codex sessions launched from kickoff packets

When reporting status, include both the control-plane view and any manual feature-session activity.

## Required Docs For Reviewers And Fixers

These documents are the minimum context set for Codex CLI and automation:
- `AGENTS.md`
- `INTEGRATION.md`
- `THREAD_OWNERSHIP.md`
- `ROADMAP.md`
- `PRODUCT_VISION.md`
- `ARCHITECTURE.md`
- `PIPELINE_RUNBOOK.md`
