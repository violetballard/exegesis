---
name: daemon.start
description: "Start the event-driven coordinator daemon and immediately verify the pipeline dashboard state."
---

Run from repo root:
- `python packet_garden/tools/launchd_ctl.py start all`
- `python packet_garden/tools/launchd_ctl.py status all`
- `python packet_garden/tools/daemon_ctl.py status`
- `python packet_garden/tools/remote_monitor_ctl.py status`
- `python packet_garden/tools/status.py`
- `python packet_garden/tools/daemon_monitor.py`
- `ps -axo pid,etime,command | rg "codex exec|opencode run|claude -p|packet_garden/tools/agents_coordinator.py" || true`
- `for f in $(ls -1t .codex/feature_runner/logs/*.log 2>/dev/null | head -n 3); do echo "FILE:$f"; tail -n 20 "$f"; done`
- `tail -n 50 .codex/packet_coordinator/daemon.log 2>/dev/null || true`

Access path selection:
- If this session is local to the development machine and `daemon_ctl.py` exists, start with the direct local command above.
- If this session is remote over VPN and local scripts are unavailable, use `python packet_garden/tools/remote_monitor_client.py start`.
- After remote start, use `python packet_garden/tools/remote_monitor_client.py status` or `full` for the sanitized verification snapshot.
- Do not use remote monitor as the default when direct local scripts are available.
- Local `remote_monitor_ctl.py status` only checks the phone/VPN monitor process. Launchd owns local daemon, monitor, and shell startup.

CLI-first note:
- assume the operator launched Codex CLI with `codex --oss --local-provider lmstudio -m gpt-oss-20b -C /Users/doctor-violet/projects/exegesis`
- do not rely on app automations; use the Python scripts above as the source of control

Then print:
- whether launchd loaded/runs daemon, monitor, and shell
- whether the remote monitor is running, with PID and log path
- daemon PID
- daemon log path
- the full queue truth from `status.py`
- the current `active_blocker` and heartbeat from `daemon_monitor.py`
- whether the queue is idle, active, or blocked
- whether reviewer and integrator sessions are present
- any important live-log lines that explain the current state

Restart note:
- After relocation to `/Users/doctor-violet/projects/exegesis`, launchd owns daemon, remote monitor, and shell startup. Use `launchd_ctl.py start/status all` after a reboot if any service does not come back cleanly.
