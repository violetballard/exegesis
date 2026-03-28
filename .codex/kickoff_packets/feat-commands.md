# Lane Kickoff: feat-commands

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: Tighten `diff_preview` output contracts so labeled/text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

### Priority outcomes
1. Keep diff-preview contracts deterministic and easy to smoke-test.
2. Make diff-preview fingerprints verify the exact emitted payload.
3. Preserve compatibility with future `Exegesis Console` consumption through engine/A2UI contracts.

### Guardrails
- Stay in lane-owned command paths unless shared-file approval is explicit.
- Keep test coverage limited to the diff-preview command-contract surface.
- Keep work aligned to the current MVP: engine, FTS retrieval, A2UI, patch/export flow.
- Do not introduce new web-facing surfaces.
