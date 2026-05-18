---
name: daemon.stop
description: "Stop the event-driven coordinator daemon and clear stale pidfile."
---

Run from repo root:
- `python packet_garden/tools/launchd_ctl.py stop daemon`

Access path selection:
- If this session is local to the development machine and `daemon_ctl.py` exists, stop with the direct local command above.
- If this session is remote over VPN and local scripts are unavailable, use `python packet_garden/tools/remote_monitor_client.py stop`.
- Remote stop uses the same daemon stop semantics as local stop, but no arbitrary remote commands are allowed.
- Use `python packet_garden/tools/launchd_ctl.py stop all` only when the user explicitly wants the daemon, phone/VPN monitor, and shell stopped together.

Then verify:
- `python packet_garden/tools/launchd_ctl.py status all`
- `python packet_garden/tools/daemon_ctl.py status`
- Remote verification fallback: `python packet_garden/tools/remote_monitor_client.py status`

CLI-first note:
- run this from a Codex CLI session launched with `codex --oss --local-provider lmstudio -m gpt-oss-20b -C /Users/doctor-violet/projects/exegesis`
