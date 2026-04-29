# Exegesis MVP Roadmap

This file is the canonical milestone tracker for the staged Exegesis MVP migration.

Detailed milestone breakdown lives in `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/docs/milestones.md`.
Detailed lane/task mapping lives in `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/docs/TASKS.md`.

## Product target

The Textual writing client is the MVP product target.

Current engine work is the enabling path for that client, not a separate product roadmap.
The CLI remains first-class while Textual stays scaffolded and disabled.

## Milestone 1: Standing shell

Status: standing (mockup only)

Scope:
- define the 5-pane Textual shell
- lock focus model and keyboard shortcuts
- define shortcut bar and command palette scaffold
- stand up the shell as a believable writing-environment mockup
- keep UI lanes disabled for engine integration until the engine contract is ready

Exit criteria:
- shell boundaries are documented and scaffolded
- the shell stands in Textual/browser as a stable mockup baseline
- the shell is explicitly not yet wired to live engine state/actions
- pane ownership is clear
- UI lanes remain disabled until explicitly activated

## Milestone 2: Core pane interactions

Status: planned

Scope:
- define project/document/workflow/basket/inspector interactions
- define the selection model and inspector-follow-selection rule
- define command palette coverage for the MVP loop

Exit criteria:
- pane interaction contract is documented
- engine contract exposes the state/actions those panes will need

## Milestone 3: Real workflow loop

Status: in progress

Scope:
- expose canonical engine state models
- keep retrieval/search FTS-first and structured
- expose plan/draft/revise/apply-reject through the canonical app service
- preserve CLI compatibility while the package/layout migration lands
- move A2UI contracts into `shared` while keeping renderers outside `shared`

Lane mapping:
- `feat-retrieval-fts`: retrieval/search
- `feat-engine-runs`: plan/draft/revise/apply-reject workflow actions
- `feat-context-storage`: persistent basket/document/session state
- `feat-a2ui-contract`: shared card/action contracts and selection models
- `feat-commands`: CLI compatibility and migration-safe entrypoints

Exit criteria:
- engine can persist project/document/basket/session state
- retrieval returns structured results suitable for basket promotion
- plan/draft/revise/apply-reject flows operate through the canonical app service
- CLI can still execute the MVP loop while Textual remains disabled

## Milestone 4: Dogfooding readiness

Status: planned

Scope:
- finish persistence and audit hooks needed for real writing sessions
- keep command palette/useful workflow actions mapped in the engine contract now
- reserve UI polish and keyboard-first validation for the disabled Textual lanes later

Exit criteria:
- engine state survives repeated sessions
- workflow artifacts are stable enough to support real writing use
- the future client surface is unblocked by engine contract gaps

## Milestone 5: YC demo readiness

Status: planned

Scope:
- create one reproducible demo flow for retrieve -> basket -> plan -> revise -> apply
- keep this as cross-lane/integrator work rather than a dedicated feature lane

Exit criteria:
- one clean 60-180 second demo path exists
- the app reads as a writing environment rather than a terminal trick

Current operational narrowing:
- Treat the canonical closure target as one engine-first demo path:
  - open project/document
  - retrieve relevant material
  - promote or gather context into the basket
  - produce a plan or revision
  - preview and apply or reject a patch
  - persist the updated document/session state
  - continue working
- Active lane work should be judged against whether it directly advances that path.
- Improvements that do not make that path more real are second-order and should wait until the demo loop stands.

## Active now
- `feat-commands`
- `feat-context-storage`
- `feat-retrieval-fts`
- `feat-a2ui-contract`
- `feat-engine-runs`

## Defined but disabled
- `feat-console-shell`
- `feat-console-workflow`

## Retired planning targets
- `feat-ux-flow`
- `feat-console`

These legacy lanes are superseded by the staged engine/client/shared split and should not be restarted.
