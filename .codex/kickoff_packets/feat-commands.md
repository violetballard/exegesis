# Lane Kickoff: feat-commands

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: Harden command catalog and diff_preview output contracts so labeled/text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

### Priority outcomes
1. Keep command-surface projections deterministic and canonical.
2. Make diff_preview output verifiable in both text and JSON modes.
3. Preserve a truthful lane record for the next implementation pass.

### Guardrails
- Stay in lane-owned command paths for future implementation work.
- Shared test coverage is approved by integrator for `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`.
- Keep review packets synchronized with the real branch delta.
- Keep work aligned to the current MVP: engine, FTS retrieval, A2UI, patch/export flow.
- Do not introduce new web-facing surfaces.
