# Codex Notes

## Repo state
- The Textual MVP is now the product target.
- Textual is not an active dependency yet.
- UI lanes are defined but disabled.
- Current work remains engine-first while the canonical package/layout migration lands.

## Canonical package roots
- `exegesis_engine` -> `engine/src/exegesis_engine`
- `exegesis_shared` -> `shared/src/exegesis_shared`
- `exegesis_textual` -> `client-textual/src/exegesis_textual`

## Compatibility rule
- Keep `src/main.py` and `src/qual/*` working until the CLI, tests, and packet tooling no longer depend on them.
- Prefer forwarding old modules to canonical packages instead of maintaining two divergent implementations.

## UI activation rule
Do not add the Textual dependency or begin `feat-console-shell` / `feat-console-workflow` implementation until those lanes are explicitly enabled.
