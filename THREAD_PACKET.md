# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Review basis: final branch tip after this fixer pass; implementation and packet metadata are reviewed together.
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
- This packet presents the final branch tip as the implementation basis so the implementation, regression tests, and handoff claims agree.

### Canonical Demo-Path Mapping

- Task 1 advances `continue working`: parser/catalog validation prevents follow-up CLI turns from continuing through a silently drifted command contract.
- Task 2 advances `continue working`: returning the canonical command-name tuple preserves deterministic command ordering across operator turns.
- Task 3 advances `continue working`: regression tests lock the command-catalog contract so later CLI drift is caught before handoff.
- Task 4 advances `continue working`: refreshed handoff metadata gives reviewer/integrator the exact narrow review basis.
- Final demo-path statement: this handoff makes `continue working` more real by keeping the CLI command contract deterministic while Textual remains disabled.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: within the narrow reviewed implementation slice, with post-implementation changes limited to packet metadata.
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Hardened `command_cli_contract()` to compare the full grouped parser projection, CLI token tuple, and lookup table against the declared command-catalog projection. Canonical demo-path step: `continue working`.
2. Preserved canonical command ordering in the CLI contract while rejecting alias-only parser drift that keeps the same canonical-name order. Canonical demo-path step: `continue working`.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for extra accepted alias, removed accepted alias, substituted accepted alias, and reordered parser-token surface drift. Canonical demo-path step: `continue working`.
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
- Final verification pass: `2026-04-28T20:56:19Z` on branch `codex/feat-commands`.

### Risks / Blockers

- Risk: high, because command-contract behavior is operator-facing.
- Blockers: none.

### Required Handoff Fields

- Branch name: `codex/feat-commands`
- Scope completed: command-catalog contract now validates canonical command ordering and rejects parser/catalog drift.
- Files changed: listed above.
- Commands run with results: listed above.
- Risks/blockers: listed above.
- Roadmap item(s) affected: Milestone 3 CLI compatibility while the package/layout migration lands; `feat-commands` CLI compatibility and migration-safe entrypoints.
- Vision capability affected: canonical engine contract stability while the CLI remains the active operator surface.
- Routing/provider impact note: none; this change does not touch model routing or provider configuration.

### Required Fix Satisfaction

1. Required fix 1 is satisfied by validating the full declared CLI parser surface: grouped parser projection, token tuple, lookup table, and canonical-name order now must match the command catalog declaration.
2. Required fix 2 is satisfied by focused tests that patch `_CLI_ENTRYPOINTS` for added valid alias, removed accepted token, substituted valid token, and reordered parser-token drift.
3. Required fix 3 is satisfied by mapping each completed task to the canonical demo-path step it advances and stating the final demo-path step made more real.
4. Required fix 4 is satisfied by rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on the exact final branch tip after implementation and packet metadata agree.

### Fixer Re-Review Disposition

- Reviewer packet `fixer__feat-commands__20260428T205430Z` requested full parser-surface drift validation, regression tests for added/removed/substituted/reordered parser tokens, canonical demo-path mapping in the handoff, and a full gate rerun.
- Fixer follow-up scope: keep the implementation narrow to `src/qual/commands/catalog.py`, `tests/unit/test_commands_catalog.py`, `THREAD.md`, and `THREAD_PACKET.md`.
- Final fixer pass reran the required handoff gates from the final branch tip.
