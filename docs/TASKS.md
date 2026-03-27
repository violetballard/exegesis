# Exegesis MVP Tasks

This file expands the canonical roadmap and lane mapping while the Textual lanes are disabled.

## Active now

### `feat-commands`
- keep `src/main.py` and the CLI surface stable during package migration
- preserve bootstrap, diff-preview, basket, and terminal command compatibility
- keep canonical imports available without breaking `src/qual/*`

### `feat-context-storage`
- land canonical state models and storage adapters under `engine/src/exegesis_engine`
- keep basket/document/session persistence deterministic
- preserve current `src/qual/context/*` and `src/qual/storage/*` flows through shims or wrappers

### `feat-retrieval-fts`
- keep the FTS-first retrieval path authoritative
- expose retrieval through the canonical engine contract
- keep structured results suitable for workflow cards and basket promotion

### `feat-a2ui-contract`
- move card/action contracts and selection types into `shared/src/exegesis_shared`
- keep terminal/CLI rendering outside the shared package
- preserve `src/qual/ui/a2ui.py` as a compatibility layer while the migration settles

### `feat-engine-runs`
- expose the canonical app service surface
- keep plan/draft/revise/apply/reject reachable through the engine contract
- preserve engine-first dependency direction during the migration

## Defined but disabled

### `feat-console-shell`
Own later:
- `client-textual/src/exegesis_textual/app/**`
- `client-textual/src/exegesis_textual/layout/**`
- `client-textual/src/exegesis_textual/panes/**`
- `client-textual/src/exegesis_textual/commands/**`
- `client-textual/src/exegesis_textual/shortcuts/**`
- `client-textual/src/exegesis_textual/inspectors/**`
- `client-textual/src/exegesis_textual/theme/**`

### `feat-console-workflow`
Own later:
- `client-textual/src/exegesis_textual/workflow/**`
- `client-textual/src/exegesis_textual/cards/**`
- `client-textual/src/exegesis_textual/events/**`

## Explicitly not now
- Textual dependency installation
- Textual widget implementation
- tabs, live preview, collaboration, sync, drag-and-drop
- native workstation shell work
