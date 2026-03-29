# Lane Kickoff: feat-commands

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: Tighten the command surface for the engine-first MVP so the CLI can reliably drive the A2UI demo flow: project open/bootstrap, retrieval invocation, patch review, and export handoff.

### Priority outcomes
1. Keep command contracts deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with future `Exegesis Console` consumption through engine/A2UI contracts.

### Guardrails
- Stay in lane-owned command paths unless shared-file approval is explicit.
- Keep work aligned to the current MVP: engine, FTS retrieval, A2UI, patch/export flow.
- Do not introduce new web-facing surfaces.
