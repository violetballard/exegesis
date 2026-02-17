#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

log "verifying required local commands"
require_cmd bash
require_cmd sh
require_cmd python3
require_cmd rg
require_cmd perl
require_cmd find
require_cmd tail

log "setup complete"
