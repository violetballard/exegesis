---
name: daemon.monitor
description: "Show the full live pipeline dashboard: daemon state, queue truth, reviewer/integrator status, lane summaries, and manual feature-session activity."
---

Run from repo root:
- `python codex_packet_handoff/tools/daemon_ctl.py status`
- `python codex_packet_handoff/tools/status.py`
- `python codex_packet_handoff/tools/daemon_monitor.py`
- `python codex_packet_handoff/tools/remote_monitor_ctl.py status`
- `ps -axo pid,etime,command | rg "codex exec|codex_packet_handoff/tools/agents_coordinator.py" || true`
- `for f in $(ls -1t .codex/feature_runner/logs/*.log 2>/dev/null | head -n 5); do echo "FILE:$f"; tail -n 30 "$f"; done`
- `for f in $(ls -1t .codex/packet_router/logs/*.log 2>/dev/null | head -n 5); do echo "FILE:$f"; tail -n 40 "$f"; done`
- `tail -n 80 .codex/packet_coordinator/daemon.log 2>/dev/null || true`

Access path selection:
- If this session is on the development machine and local scripts exist, use the direct Python/script workflow above.
- If this session is remote over VPN and local scripts are unavailable, use `python codex_packet_handoff/tools/remote_monitor_client.py full` with `QUAL_MONITOR_URL` and `QUAL_MONITOR_TOKEN`.
- Remote monitor access is narrower by design: it gives sanitized status and control, not raw logs or arbitrary commands.
- Prefer local direct scripts whenever possible; use remote monitor only for VPN/home access.
- Local `remote_monitor_ctl.py status` is a process-health check only. Do not replace local daemon/status scripts with `remote_monitor_client.py` when the repo is mounted.

CLI-first note:
- assume the operator launched Codex CLI with `codex --oss --local-provider lmstudio -m gpt-oss-20b -C /Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual`
- use the Python scripts above; do not infer daemon state from chat history alone
- when the controller is local `gpt-oss-20b`, print the full script-derived status first, then layer in the live-log evidence

If daemon is not running, also run:
- `python codex_packet_handoff/tools/daemon_ctl.py status`

Then summarize all of these together:
- local remote monitor process running/stopped state, PID, and phone/VPN availability
- daemon running/stopped state from `daemon_ctl.py status`
- filesystem truth per lane from `status.py`
- daemon running/stopped state
- backlog bottleneck and `active_blocker` from `daemon_monitor.py`
- reviewer lane state for all five lanes
- reviewer thread ids and integrator thread id
- latest live discussion summary for reviewer, integrator, and each feature lane
- whether manual feature sessions are running outside daemon
- the newest relevant lines from packet-router logs and daemon log, clearly marked as corroborating evidence or stale noise
- whether the system is actively progressing, idle, or blocked

Reading order:
1. Treat `daemon_ctl.py status` + `status.py` as authoritative control-plane truth.
2. Check `remote_monitor_ctl.py status` only as a local process-health check for phone/VPN availability.
3. In `daemon_monitor.py`, read `BACKLOG.active_blocker` and heartbeat before reading any log tail.
4. Treat packet-router logs and daemon-log tail as secondary diagnostic evidence only.
5. If daemon-log tail mentions `scope-check` but queue truth shows no pending scope-related blocker, label it as stale historical noise and do not escalate it as the live cause.
6. When reporting status, include both the full script status and the live-log highlights the way an operator would want to see them in a local CLI session.

Reference:
- `PIPELINE_RUNBOOK.md`
- `ROADMAP.md`
- `PRODUCT_VISION.md`
- `ARCHITECTURE.md`
