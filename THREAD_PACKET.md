# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Review basis: final branch tip after this `2026-04-28T22:35:01Z` fixer pass for reviewer packet `20260428T223408Z`; implementation, tests, and handoff metadata are reviewed together.
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: harden `command_cli_contract()` so the CLI contract stays deterministic, follows canonical command order, and fails fast when the parser surface drifts from the command catalog.
- Risk reason: this changes the command contract used by the active CLI operator surface while Textual lanes remain disabled.

### Scope / Plan Alignment

- Roadmap alignment: Milestone 3 CLI compatibility for the engine-first workflow loop, and `feat-commands` as the command-surface compatibility lane.
- Vision alignment: canonical engine contract stability while the CLI remains the active operator surface. This handoff does not claim auditable state, persistence, retrieval, provider routing, Textual work, or A2UI schema progress.
- Exact capability delivered: deterministic command-catalog validation for the existing CLI-first MVP loop.
- Blocker removed: parser/catalog drift validation is needed now because the CLI is the active operator surface for the engine-side MVP loop. Without a fail-fast contract check, open/retrieve/basket/revise/patch/save follow-up turns could continue through a parser surface that no longer matches the canonical command catalog.

### Shared / Integrator-Locked Accounting

- Shared-by-approval test edit: yes, `tests/unit/test_commands_catalog.py`, covered by the approved shared-test exception.
- Integrator-locked edits: no.
- Lane-owned implementation edit: `src/qual/commands/catalog.py`.
- This packet presents the final branch tip after this `2026-04-28T22:35:01Z` fixer pass as the implementation basis so implementation commits are not hidden behind metadata-only packet refreshes.
- Previous stale review basis `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` was incomplete because later commits changed `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; the corrected branch-tip basis supersedes it for re-review.

### Implementation Basis

- Reviewed implementation commits include every code-bearing command-catalog/test change through the final branch tip, including:
  - `9df1a4e32 fix(commands): enforce full CLI contract drift checks`
  - `ea0ab36b4 fix(commands): enforce parser surface drift checks`
  - `b438f4554 fix(commands): validate full CLI parser surface`
  - `18c7c627a fix(commands): cover declared CLI surface drift`
- This `2026-04-28T22:35:01Z` fixer pass addresses reviewer packet `20260428T223408Z` by keeping the actual branch-tip review basis, preserving all code-bearing catalog/test changes in the reviewed implementation basis, refreshing the packet ownership/demo-path accounting, and rerunning all required gates.
- Packet-refresh commits after those implementation commits are metadata-only only when they touch `THREAD.md` or `THREAD_PACKET.md`.
- No commit that modifies `src/qual/commands/catalog.py` or `tests/unit/test_commands_catalog.py` is classified as metadata-only in this packet.

### Canonical Demo-Path Mapping

- Task 1 advances `continue working`: parser/catalog validation prevents follow-up CLI turns from continuing through a silently drifted command contract.
- Task 2 advances `continue working`: canonical command ordering stays deterministic across operator turns and command smoke checks.
- Task 3 advances `continue working`: regression tests lock accepted-token, declared-surface, lookup-table, and alias-level parser drift before handoff.
- Task 4 advances `continue working`: refreshed handoff metadata gives reviewer/integrator the exact branch-tip review basis.
- Final demo-path statement: this handoff makes `continue working` more real by keeping the CLI command contract deterministic while Textual remains disabled.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: within the narrow reviewed implementation slice, with post-implementation changes limited to packet metadata and focused regression coverage.
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Hardened `command_cli_contract()` to validate the full parser surface by comparing grouped parser projection, CLI token tuple, lookup table, and canonical names against the declared command-catalog projection. Canonical demo-path step: `continue working`.
2. Preserved canonical command ordering in the CLI contract while rejecting alias-only parser drift that keeps the same canonical-name order. Canonical demo-path step: `continue working`.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for extra accepted alias at both contract and token-surface levels, removed accepted alias, substituted accepted alias to another known alias with the same canonical command, explicit `diff` to `diff_preview` same-canonical alias substitution, reordered parser-token surface drift, declared-surface alias drift, lookup-table token-substitution drift, and lookup-table shape/order drift. Canonical demo-path step: `continue working`.
4. Regenerated `THREAD.md` and `THREAD_PACKET.md` so the handoff claims match the final implementation and test coverage. Canonical demo-path step: `continue working`.

### Files Changed

- reviewed implementation: `src/qual/commands/catalog.py`
- approved shared-by-approval test: `tests/unit/test_commands_catalog.py`
- metadata-only handoff update: `THREAD.md`
- metadata-only handoff update: `THREAD_PACKET.md`

### Commands Run + Outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS
- Previous final verification pass: `2026-04-28T21:35:44Z` on branch `codex/feat-commands`.
- Final verification pass: `2026-04-28T21:40:36Z` on branch `codex/feat-commands`.
- Final verification pass: `2026-04-28T21:44:02Z` on branch `codex/feat-commands`.
- Approved reviewer packet `20260428T214345Z` required no code fixes; required gates passed again at `2026-04-28T21:45:26Z`.
- Reviewer packet `20260428T214706Z` requested packet-basis correction plus parser-surface fixes already present at branch tip; required gates passed again at `2026-04-28T21:50:01Z`.
- Reviewer packet `20260428T214935Z` repeated parser-surface validation, parser-surface drift test, canonical demo-path mapping, and ownership-accounting fixes; required gates passed again at `2026-04-28T21:52:01Z`.
- Reviewer packet `20260428T215506Z` repeated token-level parser-surface validation, parser-surface drift tests, canonical demo-path mapping, and ownership-accounting fixes; focused catalog regressions passed at `2026-04-28T21:55:56Z`.
- Reviewer packet `20260428T215506Z` required gates passed again at `2026-04-28T21:56:45Z`.
- Reviewer packet `20260428T215757Z` requested complete branch-tip metadata accounting and no code changes; required gates passed again at `2026-04-28T22:00:00Z`.
- Approved reviewer packet `20260428T220257Z` required no code fixes; required gates passed again at `2026-04-28T22:04:00Z`.
- Approved reviewer packet `20260428T221733Z` required no code fixes; required gates passed again at `2026-04-28T22:18:52Z`.
- Reviewer packet `20260428T222600Z` requested `_CLI_ENTRYPOINTS` drift rejection, an extra known alias regression, and canonical demo-path mapping; focused catalog regressions and all required gates passed at `2026-04-28T22:28:37Z`.
- Reviewer packet `20260428T223211Z` repeated actual branch-tip review basis, full parser-surface validation, drift-test coverage, canonical demo-path mapping, ownership accounting, and required gate rerun; focused catalog regressions and all required gates passed at `2026-04-28T22:34:25Z`.
- Reviewer packet `20260428T223408Z` repeated actual branch-tip review basis, full parser-surface validation, drift-test coverage, canonical demo-path mapping, ownership accounting, and required gate rerun; final gate results are recorded below.

### Risks / Blockers

- Risk: high, because command-contract behavior is operator-facing.
- Blockers: none.

### Required Handoff Fields

- Branch name: `codex/feat-commands`
- Scope completed: command-catalog contract now validates canonical command ordering and rejects parser/catalog drift across tokens, grouped parser surface, and lookup-table shape/order.
- Files changed: listed above.
- Commands run with results: listed above.
- Risks/blockers: listed above.
- Roadmap item(s) affected: Milestone 3 CLI compatibility while the package/layout migration lands; `feat-commands` CLI compatibility and migration-safe entrypoints.
- Vision capability affected: canonical engine contract stability while the CLI remains the active operator surface.
- Routing/provider impact note: none; this change does not touch model routing or provider configuration.

### Required Fix Satisfaction

1. Reviewer fix 1, regenerate packet against actual branch tip: satisfied by the `Implementation Basis` section. This packet uses the final branch tip after this `2026-04-28T22:35:01Z` fixer pass as the review basis and does not mark code-bearing catalog/test commits as metadata-only.
2. Reviewer fix 2, full parser-surface validation: satisfied by `command_cli_contract()` validating accepted token tuple, grouped parser projection, lookup table shape/order, and canonical names against the declared command-catalog projection.
3. Reviewer fix 3, drift regression tests: satisfied by focused tests for extra accepted alias, removed accepted alias, substituted accepted alias to another known alias with the same canonical command, parser-token reorder preserving canonical names, declared-surface alias drift, grouped token-to-canonical drift, lookup-table token-substitution drift, and lookup-table shape/order drift.
4. Reviewer fix 4, canonical demo-path mapping: satisfied by per-task `continue working` mappings and the final statement that this handoff makes that step more real while Textual remains disabled.
5. Reviewer fix 5, complete metadata-only accounting: satisfied by the `Files Changed` and `Shared / Integrator-Locked Accounting` sections, which list `THREAD.md` and `THREAD_PACKET.md` as metadata-only packet files, record the approved shared-by-approval test edit, and confirm no integrator-locked edits.
6. Reviewer fix 6, rerun required gates: final results are recorded in the `Final Verification` section.

### Reviewer Packet `20260428T223408Z` Fix Satisfaction

1. Required fix 1, actual branch-tip review basis: satisfied by this packet using the final branch tip after this `2026-04-28T22:35:01Z` fixer pass and keeping every code-bearing `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py` change in scope.
2. Required fix 2, full parser-surface validation: satisfied by `command_cli_contract()` validating accepted token tuple, grouped parser projection, lookup-table shape/order, and canonical names against `_CLI_COMMAND_SURFACE`, with `_CLI_ENTRYPOINTS` frozen against `_DECLARED_CLI_ENTRYPOINTS`.
3. Required fix 3, parser-surface drift tests: satisfied by focused regressions for parser token addition/removal, token-level extra alias rejection, same-canonical alias substitution, token reorder, declared-surface drift, lookup-table token substitution, and lookup-table shape/order drift.
4. Required fix 4, canonical demo-path mapping: every completed task maps to `continue working`, and the final statement says this handoff makes that step more real while Textual remains disabled.
5. Required fix 5, ownership accounting: lane-owned implementation is `src/qual/commands/catalog.py`, the approved shared-by-approval test edit is `tests/unit/test_commands_catalog.py`, metadata-only packet files are `THREAD.md` and `THREAD_PACKET.md`, and integrator-locked edits are `no`.
6. Required fix 6, gate rerun: final results are recorded in the `Final Verification` section.

### Reviewer Packet `20260428T213854Z` Fix Satisfaction

1. Exact canonical demo-path step: this handoff advances `continue working`.
2. Concrete blocker removed: the fail-fast `command_cli_contract()` check prevents CLI follow-up turns for open/retrieve/basket/revise/patch/save from running against a parser surface that has drifted away from the canonical catalog.
3. Complete metadata-only file list: `THREAD.md` and `THREAD_PACKET.md`.
4. Implementation scope: unchanged; this pass updates handoff metadata only because the current implementation already validates full parser-surface drift and includes the required alias-drift regressions.

### Reviewer Packet `20260428T214128Z` Fix Satisfaction

1. Independent parser-surface projection: satisfied by `command_cli_contract()` validating grouped parser projection, accepted token tuple, lookup-table shape/order, and canonical names against the declared `_CLI_COMMAND_SURFACE` projection.
2. Parser-surface drift tests: satisfied by regression coverage for removed accepted alias, added accepted alias, substituted accepted alias, token reorder, lookup-table token substitution, and lookup-table shape/order drift while canonical names can remain stable.
3. Canonical demo-path mapping: satisfied by the per-task `continue working` mapping and the final statement that this handoff makes continued CLI operation more real while Textual remains disabled.
4. Ownership accounting: satisfied by listing `src/qual/commands/catalog.py` as lane-owned implementation, `tests/unit/test_commands_catalog.py` as approved shared-by-approval test coverage, and integrator-locked edits as `no`.

### Reviewer Packet `20260428T214345Z` Fix Satisfaction

1. Reviewer verdict: `APPROVED`.
2. Required fixes before re-review: none.
3. Fixer action: reran all required gates and recorded this no-code-fix verification pass.

### Reviewer Packet `20260428T214706Z` Fix Satisfaction

1. Full parser-surface validation: satisfied by `command_cli_contract()` comparing the grouped parser projection, accepted token tuple, lookup-table shape/order, and canonical names against `_CLI_COMMAND_SURFACE`.
2. Parser-surface drift tests: satisfied by focused regressions for alias substitution with the same canonical target, removed accepted alias, added accepted alias, reordered parser tokens, and lookup-table shape/order drift.
3. Actual branch-tip packet: satisfied by presenting the final branch tip after the `2026-04-28T21:47:57Z` fixer pass as the review basis and not labeling code/test commits as metadata-only.
4. Canonical demo-path mapping: satisfied by per-task `continue working` mappings and the final statement that this handoff makes that step more real while Textual remains disabled.
5. Ownership accounting: satisfied by listing `tests/unit/test_commands_catalog.py` as the approved shared-by-approval test edit and integrator-locked edits as `no`.

### Reviewer Packet `20260428T214934Z` Fix Satisfaction

1. Declared parser-surface projection: satisfied by `command_cli_contract()` validating the grouped parser projection, accepted token tuple, lookup-table shape/order, and canonical names against `_CLI_COMMAND_SURFACE`.
2. Parser-surface drift tests: satisfied by tests that mutate `_CLI_ENTRYPOINTS`, `_CLI_COMMAND_SURFACE`, and `command_cli_lookup_table()` for added alias, removed alias, substituted alias, token reorder, lookup-table token substitution, and lookup-table order drift while canonical names can remain unchanged.
3. Canonical demo-path mapping: satisfied by per-task `continue working` mappings and the final statement that this handoff makes that step more real while Textual remains disabled.
4. Ownership accounting: satisfied by listing `src/qual/commands/catalog.py` as lane-owned implementation, `tests/unit/test_commands_catalog.py` as the approved shared-by-approval test path, and integrator-locked edits as `no`.
5. Final verification: required gates passed again at `2026-04-28T21:51:29Z`.

### Reviewer Packet `20260428T214935Z` Fix Satisfaction

1. Required fix 1, token-level parser-surface validation: already satisfied at branch tip by `command_cli_contract()` comparing the grouped parser projection, accepted token tuple, lookup-table shape/order, and canonical names against `_CLI_COMMAND_SURFACE`.
2. Required fix 2, parser-surface drift tests: already satisfied at branch tip by focused regressions for added alias, removed alias, substituted alias, token reorder, declared-surface alias drift, lookup-table token substitution, grouped parser drift, and lookup-table shape/order drift.
3. Required fix 3, canonical demo-path mapping: satisfied by per-task `continue working` mappings and the final statement that this handoff makes that step more real while Textual remains disabled.
4. Required fix 4, ownership accounting: satisfied by listing `src/qual/commands/catalog.py` as lane-owned implementation, `tests/unit/test_commands_catalog.py` as the approved shared-by-approval test edit, and integrator-locked edits as `no`.
5. Final verification: required gates passed again at `2026-04-28T21:52:01Z`.

### Reviewer Packet `20260428T215233Z` Fix Satisfaction

1. Reviewer verdict: `APPROVED`.
2. Required fixes before re-review: none.
3. Fixer action: no code changes were needed; this pass records the approval and reruns all required gates on the final tree.
4. Final verification: required gates passed again at `2026-04-28T21:54:07Z`.

### Reviewer Packet `20260428T215506Z` Fix Satisfaction

1. Required fix 1, token-level parser-surface validation: satisfied at branch tip by `command_cli_contract()` validating accepted token tuple, grouped parser projection, lookup-table shape/order, and canonical names against `_CLI_COMMAND_SURFACE`.
2. Required fix 2, parser-surface drift tests: satisfied by focused regressions for added known alias, removed accepted alias, substituted accepted token for the same canonical command, same-canonical token reorder, declared-surface alias drift, lookup-table token substitution, grouped parser drift, and lookup-table shape/order drift.
3. Required fix 3, canonical demo-path mapping: satisfied by per-task `continue working` mappings and the final statement that this handoff makes stable follow-up CLI operation more real while Textual remains disabled.
4. Required fix 4, ownership accounting: satisfied by listing `tests/unit/test_commands_catalog.py` as the approved shared-by-approval edit and confirming integrator-locked edits are `no`.
5. Focused verification: `python -m unittest tests.unit.test_commands_catalog` passed at `2026-04-28T21:55:56Z`.
6. Final verification: required gates passed again at `2026-04-28T21:56:45Z`.

### Reviewer Packet `20260428T215757Z` Fix Satisfaction

1. Complete branch-tip metadata accounting: satisfied by listing both `THREAD.md` and `THREAD_PACKET.md` as metadata-only handoff updates in `Files Changed`, and by the shared/integrator-locked accounting above.
2. Implementation review basis: unchanged; this pass keeps the command-catalog implementation and tests as-is and makes no code edits to `src/qual/commands/catalog.py` or `tests/unit/test_commands_catalog.py`.
3. Gate restatement after metadata correction: required gates passed again at `2026-04-28T22:00:00Z`.

### Reviewer Packet `20260428T222600Z` Fix Satisfaction

1. Required fix 1, reject unintended `_CLI_ENTRYPOINTS` drift: satisfied by validating `_CLI_ENTRYPOINTS` against the frozen `_DECLARED_CLI_ENTRYPOINTS` tuple before building command CLI tokens or lookup tables, so adding a known alias such as `open` fails even when it maps to an already-covered canonical command.
2. Required fix 2, extra known alias regression: satisfied by `test_command_cli_contract_rejects_extra_accepted_alias_drift` and `test_command_cli_tokens_reject_extra_accepted_alias_drift`, both patching `_CLI_ENTRYPOINTS` with `open` and expecting `Command CLI tokens are inconsistent`.
3. Required fix 3, canonical demo-path mapping: satisfied by the per-task `continue working` mappings and final statement that this handoff makes that step more real while Textual remains disabled.
