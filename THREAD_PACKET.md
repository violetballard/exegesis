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
- Final verification pass: `2026-04-28T21:01:08Z` on branch `codex/feat-commands`.

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

1. Latest required fix 1 is satisfied by the `Canonical Demo-Path Mapping` section: the concrete canonical demo-path step is `continue working`.
2. Latest required fix 2 is satisfied by mapping each completed task to `continue working`; all four tasks strengthen the same named demo-path step.
3. Latest required fix 3 is satisfied by keeping this fixer pass metadata-only. No code was added for the latest review packet.
4. The prior implementation still keeps `command_cli_contract()` deterministic and covered by parser-surface drift regression tests.

### Fixer Re-Review Disposition

- Reviewer packet `fixer__feat-commands__20260428T205934Z` requested a metadata-only handoff correction: name the canonical demo-path step, map completed tasks to that step, and keep the code scope unchanged.
- Fixer follow-up scope: metadata-only updates to `THREAD.md` and `THREAD_PACKET.md`.
- Final fixer pass reran the required handoff gates from the final branch tip after this metadata correction.
