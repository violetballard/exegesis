# Lane Kickoff: feat-commands

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: Tighten the command surface for the CLI-first operator flow so command lookup helpers, diff-preview output, and emitted fingerprints stay deterministic and verifiable.

### Priority outcomes
1. Keep command contracts deterministic and easy to smoke-test.
2. Make diff-preview fingerprints verify the exact emitted payload.
3. Preserve compatibility with future `Exegesis Console` consumption through engine/A2UI contracts.

### Guardrails
- Stay in lane-owned command paths unless shared-file approval is explicit.
- Keep any shared test coverage limited to the approved command-contract surface.
- Keep work aligned to the current MVP: engine, FTS retrieval, A2UI, patch/export flow.
- Do not introduce new web-facing surfaces.
