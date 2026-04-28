# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Review basis: final branch tip after this fixer pass; implementation, tests, and handoff metadata are reviewed together.
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
- This packet presents the final branch tip as the implementation basis so implementation commits are not hidden behind metadata-only packet refreshes.

### Implementation Basis

- Reviewed implementation commits include every code-bearing command-catalog/test change through the final branch tip, including:
  - `9df1a4e32 fix(commands): enforce full CLI contract drift checks`
  - `ea0ab36b4 fix(commands): enforce parser surface drift checks`
  - `b438f4554 fix(commands): validate full CLI parser surface`
  - this fixer pass, which adds direct lookup-table shape/order drift coverage.
- Packet-refresh commits after those implementation commits are metadata-only only when they touch `THREAD.md` or `THREAD_PACKET.md`.
- No commit that modifies `src/qual/commands/catalog.py` or `tests/unit/test_commands_catalog.py` is classified as metadata-only in this packet.

### Canonical Demo-Path Mapping

- Task 1 advances `continue working`: parser/catalog validation prevents follow-up CLI turns from continuing through a silently drifted command contract.
- Task 2 advances `continue working`: canonical command ordering stays deterministic across operator turns and command smoke checks.
- Task 3 advances `continue working`: regression tests lock accepted-token, lookup-table, and alias-level parser drift before handoff.
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
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for extra accepted alias, removed accepted alias, substituted accepted alias, reordered parser-token surface drift, and lookup-table shape/order drift. Canonical demo-path step: `continue working`.
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
- Final verification pass: `2026-04-28T21:10:05Z` on branch `codex/feat-commands`.

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

1. Reviewer fix 1, full parser-surface validation: satisfied by `command_cli_contract()` validating grouped parser projection, accepted token tuple, lookup table shape/order, and canonical names against the declared command-catalog projection.
2. Reviewer fix 2, drift regression tests: satisfied by focused tests for extra accepted alias, removed accepted alias, substituted accepted alias, parser-token reorder preserving canonical names, grouped token-to-canonical drift, and lookup-table shape/order drift.
3. Reviewer fix 3, unambiguous review basis: satisfied by the `Implementation Basis` section. This packet uses final branch tip as the review basis and does not mark code-bearing catalog/test commits as metadata-only.
4. Reviewer fix 4, canonical demo-path mapping: satisfied by per-task `continue working` mappings and the final statement that this handoff makes that step more real while Textual remains disabled.
5. Reviewer fix 5, ownership clarity: satisfied by the `Shared / Integrator-Locked Accounting` section, which records the approved shared-by-approval test edit and confirms no integrator-locked edits.
