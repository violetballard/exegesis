#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

log "starting CI entrypoint"
"$ROOT_DIR/scripts/setup.sh"
"$ROOT_DIR/scripts/format-check.sh"
"$ROOT_DIR/scripts/lint.sh"
"$ROOT_DIR/scripts/build.sh"
"$ROOT_DIR/typecheck-test.sh"
"$ROOT_DIR/scripts/test.sh"
log "CI entrypoint completed"
