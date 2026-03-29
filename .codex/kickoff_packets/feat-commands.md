# Lane Kickoff: feat-commands

- Branch: `codex/feat-commands`
- Head commit: `cf6e4984d3d0f154d2be69c58f582868c9549585`
- Lane/owned paths: `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- Scope goal: Keep the `feat-commands` handoff aligned with the command-catalog, canonical mapping, and diff-preview CLI contract work already present on the branch, plus the two explicitly approved shared tests.

### Priority outcomes
1. Keep the handoff truthful about the owned command paths, canonical command mapping, and approved shared tests.
2. Keep the shared-test approvals explicit.
3. Keep the lane from widening beyond the approved `feat-commands` surface while preserving the CLI-first command-catalog, canonical mapping, and diff-preview contract scope.

### Guardrails
- Stay in lane-owned command paths except for explicitly approved shared tests, which make the handoff high-risk.
- Keep review packets synchronized with the real branch delta.
- Do not introduce new web-facing surfaces.
- Keep work aligned to the current MVP: engine, FTS retrieval, A2UI, patch/export flow.
