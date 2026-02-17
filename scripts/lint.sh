#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

log "quality-lint.sh"
"$ROOT_DIR/quality-lint.sh"
