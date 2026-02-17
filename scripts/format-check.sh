#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

log "quality-format.sh --check"
"$ROOT_DIR/quality-format.sh" --check
