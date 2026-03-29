# Lane Kickoff: feat-commands

- Branch: `codex/feat-commands`
- Head commit: `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50`
- Lane/owned paths: `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_diff_preview.py`
- Scope goal: Harden `diff_preview` output contracts so the emitted diff payload, JSON label metadata, summary-only mode, and SHA-256 fingerprint stay deterministic and verifiable for CLI-first operator use.

### Priority outcomes
1. Keep the emitted diff payload and reported fingerprint derived from the same exact text.
2. Keep JSON label metadata truthful when file headers are suppressed.
3. Keep summary-only mode verifiable in both text and JSON output shapes.
4. Keep the handoff metadata truthful about the actual code/test delta and approved shared test coverage.
5. Keep the scope gate aligned with the approved shared-test exception.

### Guardrails
- Stay in lane-owned command paths except for explicitly approved shared tests.
- Keep review packets synchronized with the real branch delta.
- Do not introduce new web-facing surfaces.
- Keep work aligned to the current MVP: engine, FTS retrieval, A2UI, patch/export flow.
