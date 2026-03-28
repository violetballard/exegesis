# Lane Kickoff: feat-commands

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: Harden `diff_preview` output contracts so the emitted diff payload, summary-only mode, and SHA-256 fingerprint stay deterministic and verifiable for CLI-first operator use.

### Priority outcomes
1. Keep the emitted diff payload and reported fingerprint derived from the same exact text.
2. Keep summary-only mode verifiable in both text and JSON output shapes.
3. Keep the handoff metadata truthful about the actual code/test delta and approved shared test coverage.

### Guardrails
- Stay in lane-owned command paths except for explicitly approved shared tests.
- Keep review packets synchronized with the real branch delta.
- Do not introduce new web-facing surfaces.
- Keep work aligned to the current MVP: engine, FTS retrieval, A2UI, patch/export flow.
