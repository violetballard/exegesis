#!/bin/zsh
set -euo pipefail

REPO_ROOT="/Users/doctor-violet/projects/exegesis"
cd "$REPO_ROOT"
exec /usr/bin/python3 "$REPO_ROOT/codex_packet_handoff/tools/daemon_ctl.py" launchd-run
