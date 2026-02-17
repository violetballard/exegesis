#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

log "quality-test.sh"
"$ROOT_DIR/quality-test.sh"
