#!/usr/bin/env sh
set -eu

ROOT_DIR=${QUAL_ROOT_DIR:-$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)}
cd "$ROOT_DIR"

if [ -f tsconfig.json ]; then
  if command -v npx >/dev/null 2>&1; then
    echo "[typecheck] running TypeScript compiler"
    npx tsc --noEmit
    exit 0
  fi
  echo "[typecheck] tsconfig.json exists but npx is unavailable"
  exit 1
fi

if [ -d src ]; then
  if command -v python3 >/dev/null 2>&1; then
    echo "[typecheck] compiling Python sources in src/"
    python3 -m compileall -q src
    exit 0
  fi
  echo "[typecheck] src/ exists but python3 is unavailable"
  exit 1
fi

echo "[typecheck] skipped: no tsconfig.json or src/ directory found"
