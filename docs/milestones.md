# Exegesis MVP Milestones

This file expands the canonical roadmap in `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/ROADMAP.md`.

## Milestone 1: Standing shell

Outcome:
- A 5-pane Textual shell stands as a stable mockup baseline in Textual/browser, but it is not yet wired to live engine state or actions. The implementation lanes remain disabled until the engine contract is stable enough to consume.

Deliverables:
- standing shell mockup baseline
- 3-column shell layout definition
- Project / Document / Workflow / Context Basket / Inspector pane boundaries
- Focus model and shortcut bar plan
- Command palette scaffold plan

Status:
- Standing (mockup only; not engine-wired)
- Lane state: disabled for product-real integration (`feat-console-shell`, `feat-console-workflow`)

## Milestone 2: Core pane interactions

Outcome:
- The Textual shell stops being static once the UI lanes are activated.

Deliverables:
- project item listing and open flow
- document edit/save flow
- basket add/remove/select/clear
- inspector follows selection
- workflow pane accepts commands and renders selectable cards

Status:
- Planned
- Lane state: disabled until engine contract is ready

## Milestone 3: Real workflow loop

Outcome:
- The repo exposes a complete engine-side contract for retrieve -> basket -> plan -> revise -> patch -> document.

Active engine ownership:
- `feat-retrieval-fts`: retrieval/search
- `feat-engine-runs`: plan, draft, revise, apply/reject flows
- `feat-context-storage`: persistent basket/document/session state
- `feat-a2ui-contract`: shared card/action contracts
- `feat-commands`: CLI compatibility while the package/layout migration is underway

Status:
- In progress

## Milestone 4: Dogfooding readiness

Outcome:
- The engine contract and the future Textual client surface are stable enough for real writing sessions.

Deliverables:
- persistence for document/basket/session state
- save-to-project workflow output paths
- readable, durable workflow cards
- keyboard-first interaction plan carried through the client
- minimal audit/proposal logging

Status:
- Split work: active in engine lanes now, deferred in disabled UI lanes

## Milestone 5: YC demo readiness

Outcome:
- One clean, reproducible demo path exists for retrieve -> basket -> plan -> revise -> apply.

Deliverables:
- demo project
- repeatable retrieval and basket build
- repeatable plan and revision scenario
- stable pane labels and core actions
- no broken states on the recorded flow

Status:
- Planned
- Owned as cross-lane/integrator work, not a dedicated feature lane

Current operating rule:
- Until this milestone is standing, all active engine work should be evaluated against one canonical demo path:
  - open project/document
  - retrieve relevant material
  - promote or gather context into the basket
  - produce a plan or revision
  - preview and apply or reject a patch
  - persist updated document/session state
  - continue working
- Code churn, contract cleanup, or infra work do not count toward this milestone unless they directly unblock or harden that specific path.
