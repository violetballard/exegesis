# Project Structure

## Staged migration rule

The repo is moving toward a three-surface structure without breaking the current CLI or packet automation:
- `engine/`
- `client-textual/`
- `shared/`
- `docs/`

During the migration:
- canonical packages live under `engine/src/exegesis_engine`, `shared/src/exegesis_shared`, and `client-textual/src/exegesis_textual`
- root package shims (`exegesis_engine`, `exegesis_shared`, `exegesis_textual`) make those imports work before packaging/install hooks are added
- `src/qual/*` remains as the compatibility surface until the pipeline, tests, and entrypoints fully converge

## Current to target mapping

### Current compatibility surface
- `src/qual/commands/**`
- `src/qual/context/**`
- `src/qual/storage/**`
- `src/qual/retrieval/**`
- `src/qual/engine/**`
- `src/qual/ui/**`

### Canonical target surface
- `engine/src/exegesis_engine/api/**`
- `engine/src/exegesis_engine/state/**`
- `engine/src/exegesis_engine/storage/**`
- `engine/src/exegesis_engine/retrieval/**`
- `engine/src/exegesis_engine/workflow/**`
- `engine/src/exegesis_engine/patches/**`
- `engine/src/exegesis_engine/audit/**`
- `shared/src/exegesis_shared/contracts/**`
- `shared/src/exegesis_shared/models/**`
- `shared/src/exegesis_shared/types/**`
- `client-textual/src/exegesis_textual/**`

## Dependency rule
- client packages may depend on engine/shared
- shared packages must stay UI-agnostic
- engine packages must not depend on client code
