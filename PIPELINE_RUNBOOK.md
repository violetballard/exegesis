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
- runtime mode and cloud retry state

Manual feature sessions are separate from the daemon:
- feature lanes may also be running as direct Codex CLI sessions outside the daemon
- inspect them with the process view and `.codex/feature_runner/logs/`
- if queue state is idle but feature sessions are active, the pipeline is waiting for new commits rather than stuck

If `status.py` and `daemon_monitor.py` disagree, trust `status.py` for queue truth and use `daemon_monitor.py` for runtime diagnostics.

Operator reading order:
1. Read `status.py` totals and lane states first.
2. Read `daemon_monitor.py` and look at `BACKLOG.active_blocker` before any lane conversation or daemon-log tail.
3. Treat `DAEMON LOG TAIL` as secondary diagnostic context only.
4. If daemon-log tail mentions `scope-check` but queue truth does not show a current scope-related blocker, label it as stale historical noise.

## CLI-First Runtime Mode

The orchestrator can run cloud-first and fall back to local Codex CLI when quota/rate limits hit.

Config lives in `.codex/packet_router/config.json`.

Legacy keys still work:
- `model` / `codex_cmd`: cloud-primary launcher
- `fallback_codex_cmd`: local fallback executable, usually `codex`
- `fallback_codex_args`: extra fallback launcher flags
- `fallback_model`: optional local model id
- `fallback_model_args`: extra args passed after `-m <model>`

Preferred setup uses named launcher profiles:
- `profiles.<name>`:
  - `codex_cmd`
  - `codex_args`
  - `model`
  - `model_args`
- `role_profiles`:
  - `orchestrator`
  - `cloud_probe`
  - `feature_cloud` / `feature_local`
  - `reviewer_cloud` / `reviewer_local`
  - `integrator_cloud` / `integrator_local`
  - `fixer_cloud` / `fixer_local`

Recommended local fallback:
- prefer a local CLI profile via `fallback_codex_args`, for example `["-p", "gpt-oss-120b-lms"]`
- this is the most reliable option when your machine already has a working local provider profile in `~/.codex/config.toml`
- if you prefer `--oss`, leave `fallback_model` empty unless you know your CLI/provider expects a specific local model id

Recommended role split:
- `orchestrator`: smaller local profile for supervision
- `worker_cloud`: cloud coding/review/integration model
- `worker_local`: larger local coding/review/integration model for quota windows

Current project config uses:
- `profiles.orchestrator` -> `codex -p gpt-oss-20b-lms`
- `profiles.worker_cloud` -> `codex exec -m gpt-5.4`
- `profiles.worker_local` -> `codex -p gpt-oss-120b-lms`

Note:
- the coordinator itself is deterministic Python, not an LLM thread
- the role profiles control the Codex sessions it launches for feature/reviewer/fixer/integrator work

Why leave `fallback_model` empty:
- when `--oss` is active, the CLI/provider can select its configured local model
- forcing a model id here can break fallback on accounts that do not accept that id

Useful commands:
- inspect runtime mode: `python codex_packet_handoff/tools/runtime_mode_ctl.py status`
- force local mode now: `python codex_packet_handoff/tools/runtime_mode_ctl.py local_fallback --reason "manual switch"`
- switch back to cloud: `python codex_packet_handoff/tools/runtime_mode_ctl.py cloud_primary --reason "manual switch"`
- launch feature lanes using current runtime mode: `python codex_packet_handoff/tools/launch_feature_lanes.py`

## CLI Runbook

Launch your operator session from Codex CLI on the local orchestrator profile:
- `codex -p gpt-oss-20b-lms -C /Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual`

### Normal Day

Use this when cloud quota is available and you want workers to use cloud by default:
1. `python codex_packet_handoff/tools/runtime_mode_ctl.py cloud_primary --reason "normal day"`
2. `python codex_packet_handoff/tools/daemon_ctl.py start`
3. `python codex_packet_handoff/tools/daemon_monitor.py`
4. If you want to seed feature work manually from kickoff packets:
   `python codex_packet_handoff/tools/launch_feature_lanes.py`

Behavior:
- your interactive Codex CLI stays on local `gpt-oss-20b`
- cloud worker launches use `gpt-5.4`
- if quota text or rate-limit text appears, router flips to `local_fallback`

### Quota Exhausted

Use this when cloud quota is gone and you want to keep feeding the pipeline locally:
1. `python codex_packet_handoff/tools/runtime_mode_ctl.py local_fallback --reason "quota exhausted"`
2. `python codex_packet_handoff/tools/daemon_ctl.py start`
3. `python codex_packet_handoff/tools/daemon_monitor.py`
4. If you need fresh local feature sessions:
   `python codex_packet_handoff/tools/launch_feature_lanes.py`

Behavior:
- orchestrator remains local `gpt-oss-20b`
- local worker launches use `gpt-oss-120b`
- router will keep probing cloud after cooldown and can switch back automatically

### Quick Checks

- queue truth: `python codex_packet_handoff/tools/status.py`
- full dashboard: `python codex_packet_handoff/tools/daemon_monitor.py`
- planner only: `python codex_packet_handoff/tools/planner.py`
- router once: `python codex_packet_handoff/tools/router.py`
- one coordinator drain cycle: `python codex_packet_handoff/tools/agents_coordinator.py --once`

Quota safeguard:
- reviewer, fixer, and integrator outputs are scanned for quota/rate-limit text
- if quota text is detected, router flips to `local_fallback` and records `last_quota_reason`
- this applies even when the tool returned plain text instead of raising an exception

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
- `feat-retrieval-fts`: start from current main
- `feat-a2ui-contract`: start from current main
- `feat-engine-runs`: start from current main

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
