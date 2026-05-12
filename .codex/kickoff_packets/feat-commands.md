# Lane Kickoff: feat-commands

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: Tighten the command surface for the engine-first MVP so the CLI can reliably drive the A2UI demo flow: project open/bootstrap, retrieval invocation, patch review, and export handoff.

### Priority outcomes
1. Keep command contracts deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with future `Exegesis Console` consumption through engine/A2UI contracts.

### Definition of done
- Core engine actions are reachable through stable commands.
- Command behavior is deterministic and smoke-testable.
- Compatibility shims keep old command surfaces working where required.
- Command handlers stay thin and delegate real behavior to engine code.

### Milestone 3 closure focus
- Canonical demo-path step advanced by this lane:
  - open project/document
  - retrieve relevant material
  - preview and apply or reject a patch
  - persist and continue through a stable CLI surface
- Optimize for a trusted command surface for the demo loop, not broader CLI polish.
- If a command path already covers the canonical flow, prefer closing review cleanly over adding more command surface.

### Current intervention guidance
1. Keep command handlers thin and focused on the canonical demo path only.
2. Prefer deterministic command contracts and smoke-testable behavior over extra flags or UX tweaks.
3. Do not broaden scope beyond the commands needed to open, retrieve, revise/apply, and persist.
4. Handoff should name which demo-path commands are now stable enough to trust in the Milestone 3 loop.

### Do not spend time on
- Fancy CLI UX that does not support the MVP loop.
- New command flags that do not help open, retrieve, basket, revise, patch, or save.
- Embedding engine behavior directly in command handlers.

### Guardrails
- Stay in lane-owned command paths unless shared-file approval is explicit.
- Keep work aligned to the current MVP: engine, FTS retrieval, A2UI, patch/export flow.
- Do not introduce new web-facing surfaces.
