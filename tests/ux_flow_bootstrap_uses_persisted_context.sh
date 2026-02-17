#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT_DIR"

PROJECT="ux-flow-persisted-context"

python3 -m src.main context-basket clear >/dev/null
python3 -m src.main context-basket add "ctx-1" >/dev/null
python3 -m src.main context-basket add "ctx-2" >/dev/null

output=$(python3 -m src.main bootstrap --project "$PROJECT")

printf "%s" "$output" | grep -q "project: $PROJECT"
printf "%s" "$output" | grep -q "context_items: 2"

python3 -m src.main context-basket clear >/dev/null

echo "ux flow persisted context bootstrap passed"
