#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"

cd "${REPO_ROOT}"

have_rg() {
  command -v rg >/dev/null 2>&1
}

print_heading() {
  printf '\n=== %s ===\n' "$1"
}

print_process_view() {
  if have_rg; then
    ps -axo pid,etime,command | rg 'codex exec|opencode run|codex_packet_handoff/tools/agents_coordinator.py' || true
  else
    ps -axo pid,etime,command | grep -E 'codex exec|opencode run|codex_packet_handoff/tools/agents_coordinator.py' || true
  fi
}

print_latest_logs() {
  local pattern="$1"
  local count="$2"
  local lines="$3"
  local file
  local files=()

  if ! compgen -G "${pattern}" >/dev/null; then
    echo "(none)"
    return
  fi

  while IFS= read -r file; do
    files+=("${file}")
  done < <(ls -1t ${pattern} 2>/dev/null | head -n "${count}")

  for file in "${files[@]}"; do
    echo "FILE:${file}"
    tail -n "${lines}" "${file}" || true
  done
}

print_heading "DAEMON STATUS"
"${PYTHON_BIN}" codex_packet_handoff/tools/daemon_ctl.py status

print_heading "PIPELINE STATUS"
"${PYTHON_BIN}" codex_packet_handoff/tools/status.py

print_heading "DAEMON MONITOR"
"${PYTHON_BIN}" codex_packet_handoff/tools/daemon_monitor.py

print_heading "PROCESS VIEW"
print_process_view

print_heading "FEATURE RUNNER LOGS"
print_latest_logs ".codex/feature_runner/logs/*.log" 5 20

print_heading "PACKET ROUTER LOGS"
print_latest_logs ".codex/packet_router/logs/*.log" 5 40

print_heading "DAEMON LOG TAIL"
tail -n 80 .codex/packet_coordinator/daemon.log 2>/dev/null || true
