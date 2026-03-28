# Lane Kickoff: feat-commands

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: Restore the `feat-commands` scope policy so the approved shared `tests/unit/test_diff_preview.py` regression is allowed through the gate.

### Priority outcomes
1. Keep the scope-check policy aligned with the approved shared regression.
2. Keep the handoff metadata truthful about the actual submitted scope.
3. Keep the lane from widening beyond the approved `feat-commands` surface.

### Guardrails
- Stay in lane-owned command paths except for explicitly approved shared tests.
- Keep review packets synchronized with the real branch delta.
- Do not introduce new web-facing surfaces.
- Keep work aligned to the current MVP: engine, FTS retrieval, A2UI, patch/export flow.
