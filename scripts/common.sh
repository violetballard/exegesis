#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${QUAL_ROOT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT_DIR"

log() {
  printf '[devex] %s\n' "$*"
}

have() {
  command -v "$1" >/dev/null 2>&1
}

require_cmd() {
  local cmd="$1"
  if ! have "$cmd"; then
    log "required command '$cmd' is missing"
    exit 1
  fi
}
