# Exegesis Architecture Guardrails

This file is the canonical architecture boundary for the staged MVP migration.

Detailed structure notes live in `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/docs/PROJECT_STRUCTURE.md`.

## Top-level boundaries

- `engine/`
  - Canonical engine/runtime code.
  - Owns app state, storage adapters, retrieval, workflow actions, patches, audit, and engine-facing APIs.

- `shared/`
  - Canonical shared contracts, shared models, shared object/type definitions, and shared utilities.
  - Must stay UI-agnostic.

- `client-textual/`
  - The future Textual MVP client surface.
  - Exists as scaffold only until the UI lanes are enabled.

- `src/qual/`
  - Compatibility surface during migration.
  - Existing CLI/runtime imports stay here until entrypoints, tests, and packet tooling fully converge on canonical packages.

## Dependency direction

Allowed direction only:
- `client-textual -> engine`
- `client-textual -> shared`
- `engine -> shared`
- `src/qual compatibility shims -> engine|shared`

Disallowed direction:
- `engine -> client-textual`
- `shared -> client-textual`
- `shared -> src/qual/ui rendering`
- `engine -> UI widget code`

## Migration rules

- Canonical packages live under:
  - `engine/src/exegesis_engine`
  - `shared/src/exegesis_shared`
  - `client-textual/src/exegesis_textual`
- Root package shims (`exegesis_engine`, `exegesis_shared`, `exegesis_textual`) exist only to make those packages importable before packaging/install hooks are introduced.
- `src/main.py` and `src/qual/*` remain compatibility entrypoints until the migration is complete.
- Prefer forwarding old modules to canonical packages rather than keeping parallel implementations.

## Engine boundary

Engine owns:
- project/document/workflow/basket/inspector state models
- project/document open/save flows
- retrieval/search orchestration
- plan/draft/revise/apply-reject workflows
- persistence and audit hooks
- provider/runtime policy

Engine must not own:
- Textual widgets
- layout rendering
- client-only shortcuts or pane presentation logic

## Shared boundary

Shared owns:
- A2UI card/action contracts
- selection models
- shared object types

Shared must not own:
- terminal rendering adapters
- Textual rendering
- CLI-only presentation logic

## Client boundary

The future Textual client will own:
- shell layout
- panes and focus model
- workflow pane rendering
- command palette and shortcut bar
- inspector rendering

The Textual client must consume engine/shared contracts rather than reimplementing engine semantics.
