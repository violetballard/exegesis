# Remote Daemon Monitoring And Control Spec

## Summary

The remote monitor is an internal development-infrastructure service for checking and controlling the `qual` daemon from this Codex conversation when the main development machine is reached over split-tunnel VPN. It is not a product sidecar, not a browser dashboard, and not a remote git interface.

The service supports:

- direct local Python/script use on the development machine
- one explicitly configured VPN bind address for home access through the remote monitor
- authenticated status reads
- authenticated daemon lifecycle controls
- no feature-branch commit, staging, push, PR, or arbitrary shell execution

## Boundaries

The remote monitor owns:

- sanitized daemon and pipeline status snapshots
- authenticated HTTP endpoints for status and limited control
- a small CLI client for remote Codex/home use
- a launch helper for running the monitor itself
- config and token loading from untracked local state

The daemon/control plane owns:

- actual planner/router/fixer/integrator execution
- worker launch and process cleanup
- pause and kick behavior through `.codex/packet_coordinator` state files

Non-goals:

- no HTML dashboard
- no local office LAN browser access
- no replacement for direct local Python scripts when Codex is running on the development machine
- no remote commit/stage/push/PR path
- no packet body, prompt, raw log, env var, or workspace file serving
- no public network exposure
- no replacement for the product localhost sidecar

## Access Path Selection

The operator workflow has two access paths:

1. Local development-machine access
   - Use the existing real-time local Python scripts directly:
     - `daemon_ctl.py`
     - `status.py`
     - `daemon_monitor.py`
     - targeted local coordinator/router/planner scripts when appropriate
   - This remains the richest and most authoritative workflow for office-machine use.
   - The remote monitor should not be used merely because it is available on loopback.
2. Remote VPN access
   - Use `remote_monitor_client.py` with `QUAL_MONITOR_URL` and `QUAL_MONITOR_TOKEN`.
   - This path is only for home/Codex access over the split-tunnel VPN or for a thin remote operator shell.
   - Remote controls are intentionally limited to status, start, stop, pause, resume, and kick.

Skills and operator runbooks should choose the path this way:

1. If this Codex session has the `qual` repo mounted locally and `codex_packet_handoff/tools/daemon_ctl.py` exists, use direct local scripts.
2. If local scripts are unavailable, but `QUAL_MONITOR_URL` and `QUAL_MONITOR_TOKEN` are set, use the remote monitor client.
3. If neither path is available, report that daemon state cannot be verified from the current session.

This keeps the remote pathway narrow while preserving the local operator experience we already rely on.

## Network Model

Allowed binds:

- `127.0.0.1` for local use on the office development machine
- a specific VPN interface/IP for split-tunnel access from home

Forbidden binds:

- `0.0.0.0`
- public interfaces
- broad LAN exposure

Every remote request is checked against configured CIDR allowlist. Loopback is always allowed. VPN access must be explicitly configured in `.codex/remote_monitor/config.json`.

## Authentication

All endpoints except `/healthz` require:

```text
Authorization: Bearer <token>
```

Token source order:

1. environment variable named by `token_env`, default `QUAL_MONITOR_TOKEN`
2. token file, default `.codex/remote_monitor/token`

The token must stay out of git. On macOS, storing or provisioning it from Keychain is preferred; a chmod-600 token file is the fallback.

## Endpoints

Read endpoints:

- `GET /healthz`
  - unauthenticated liveness only
  - returns no daemon state
- `GET /api/status/summary`
  - authenticated compact status for chat use
- `GET /api/status/text`
  - authenticated compact text status for iOS Shortcuts and thin phone use
- `GET /api/status`
  - authenticated sanitized status snapshot

Control endpoints:

- `POST /api/control/start`
  - runs `daemon_ctl.py start`
- `POST /api/control/stop`
  - runs `daemon_ctl.py stop`
  - may terminate daemon workers the same way local stop does
- `POST /api/control/pause`
  - writes `.codex/packet_coordinator/pause.json`
  - daemon stops launching new planner/router/feature work
  - active workers are not killed
- `POST /api/control/resume`
  - removes pause flag
  - writes a kick request so the daemon reconciles promptly
- `POST /api/control/kick`
  - writes `.codex/packet_coordinator/kick.json`
  - daemon consumes it on the next loop and records the request

Control request body:

```json
{
  "operator": "codex-remote",
  "reason": "brief reason"
}
```

Control response includes:

- `action_id`
- action name
- operator
- timestamp
- result code/output
- refreshed status summary

## Snapshot Contents

Status snapshots may include:

- daemon running state
- pause state
- runtime mode
- cloud availability
- local/cloud active job counts
- queue totals
- lane states and counts
- active blocker
- memory pressure summary
- tracked git cleanliness
- process kind counts and PIDs/RSS only

Snapshots must not include:

- raw logs
- prompt text
- packet bodies
- API keys or tokens
- environment variables
- full process command lines
- full workspace paths
- arbitrary file contents

## Pause And Kick Semantics

Pause is a first-class daemon state:

- stored at `.codex/packet_coordinator/pause.json`
- visible in remote status snapshots
- prevents new coordinator work cycles from launching planner/router/feature work
- does not kill active workers

Resume:

- removes the pause file
- records a kick request
- allows the next daemon loop to resume normal scheduling

Kick:

- records a bounded request for the daemon to wake/reconcile
- does not bypass the coordinator lease
- does not duplicate active jobs
- does not run git mutation commands

## Local Files

Tracked files:

- `docs/remote_monitoring/iphone_shortcuts.md`
- `REMOTE_MONITORING_SPEC.md`
- `codex_packet_handoff/config/remote_monitor.example.json`
- `codex_packet_handoff/tools/remote_monitor_snapshot.py`
- `codex_packet_handoff/tools/remote_monitor_server.py`
- `codex_packet_handoff/tools/remote_monitor_client.py`
- `codex_packet_handoff/tools/remote_monitor_ctl.py`

Untracked runtime files:

- `.codex/remote_monitor/config.json`
- `.codex/remote_monitor/token`
- `.codex/remote_monitor/server.pid`
- `.codex/remote_monitor/server.log`
- `.codex/packet_coordinator/pause.json`
- `.codex/packet_coordinator/kick.json`

## Phone Shortcuts

The simplest mobile operator surface is a folder of iOS Shortcuts that call the authenticated remote monitor endpoints over VPN. Keep these shortcuts limited to status, start, stop, pause, resume, and kick. The paste-ready recipes live in `docs/remote_monitoring/iphone_shortcuts.md`.

## Operator Commands

Local monitor process:

```sh
python codex_packet_handoff/tools/remote_monitor_ctl.py start
python codex_packet_handoff/tools/remote_monitor_ctl.py status
python codex_packet_handoff/tools/remote_monitor_ctl.py stop
```

One-time local setup:

```sh
python codex_packet_handoff/tools/remote_monitor_ctl.py init \
  --host 127.0.0.1 \
  --allowed-cidr 100.64.0.0/10
```

For phone use, replace `--host` with the specific VPN interface address or VPN DNS name that resolves to it. Never bind to `0.0.0.0`.

Remote/local client:

```sh
QUAL_MONITOR_URL=http://127.0.0.1:8765 \
QUAL_MONITOR_TOKEN=<token> \
python codex_packet_handoff/tools/remote_monitor_client.py status
```

Phone-readable text status:

```sh
QUAL_MONITOR_URL=http://127.0.0.1:8765 \
QUAL_MONITOR_TOKEN=<token> \
python codex_packet_handoff/tools/remote_monitor_client.py text
```

Access selection check:

```sh
test -f codex_packet_handoff/tools/daemon_ctl.py && \
  python codex_packet_handoff/tools/daemon_ctl.py status
```

If the local check works, prefer the local scripts. If it fails in a VPN/home context, use `remote_monitor_client.py`.

Control examples:

```sh
python codex_packet_handoff/tools/remote_monitor_client.py pause --reason "leaving machine idle"
python codex_packet_handoff/tools/remote_monitor_client.py resume --reason "back online"
python codex_packet_handoff/tools/remote_monitor_client.py kick --reason "unstick queue"
```

## Test Plan

- Auth rejects missing, bad, and malformed bearer tokens.
- VPN allowlist rejects non-loopback, non-allowed remote addresses.
- `/healthz` works without auth and exposes no sensitive state.
- Status snapshots redact secrets, paths, raw logs, prompts, env vars, and full command lines.
- Hung `daemon_monitor.py` cannot hang status generation.
- `start` invokes only `daemon_ctl.py start`.
- `stop` invokes only `daemon_ctl.py stop`.
- `pause` prevents new work cycles while preserving active workers.
- `resume` clears pause and writes a kick request.
- `kick` writes a wake request without direct git mutation.
- Control requests are serialized.
- No route can stage, commit, push, edit packets, or run arbitrary shell commands.
