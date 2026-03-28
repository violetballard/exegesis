# Lane Kickoff: feat-commands

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: Keep the feat-commands handoff metadata synchronized with the code-bearing branch delta that hardens command lookup, exports, and diff_preview output contracts for CLI-first operator use.

### Priority outcomes
1. Keep command contracts deterministic and smoke-testable.
2. Keep the diff_preview fingerprint tied to the exact emitted payload.
3. Keep the handoff metadata truthful about the real branch delta and approved shared tests.

### Guardrails
- Stay in lane-owned command paths except for explicitly approved shared tests.
- Keep review packets synchronized with the real branch delta.
- Do not introduce new web-facing surfaces.
- Keep work aligned to the current MVP: engine, FTS retrieval, A2UI, patch/export flow.
