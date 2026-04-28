# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Review basis: final branch tip after this `2026-04-28T23:21:20Z` fixer pass for reviewer packet `20260428T231936Z`; implementation, tests, and handoff metadata are reviewed together.
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: harden `command_cli_contract()` so the CLI contract stays deterministic, follows canonical command order, and fails fast when the parser surface drifts from the command catalog.
- Risk reason: this changes the command contract used by the active CLI operator surface while Textual lanes remain disabled.

### Scope / Plan Alignment

- Roadmap alignment: Milestone 3 CLI compatibility for the engine-first workflow loop, and `feat-commands` as the command-surface compatibility lane.
- Vision alignment: canonical engine contract stability while the CLI remains the active operator surface.
- Exact capability delivered: deterministic command-catalog validation for the existing CLI-first MVP loop.
- Blocker removed: parser/catalog drift validation is needed now because the CLI is the active operator surface for the engine-side MVP loop. Without a fail-fast contract check, open/retrieve/basket/revise/patch/save follow-up turns could continue through a parser surface that no longer matches the canonical command catalog.

### Implementation Basis

- This packet submits the full branch-tip implementation for review.
- No commit that modifies `src/qual/commands/catalog.py` or `tests/unit/test_commands_catalog.py` is classified as metadata-only.
- Previous stale review basis `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` is superseded because later branch commits changed command-catalog implementation and tests.
- Metadata-only handoff files are limited to `THREAD.md` and `THREAD_PACKET.md`.

### Shared / Integrator-Locked Accounting

- Lane-owned implementation edit: `src/qual/commands/catalog.py`.
- Approved shared-by-approval test edit: `tests/unit/test_commands_catalog.py`.
- Integrator-locked edits: no.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC` for this reviewer-fix pass.
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Hardened `command_cli_contract()` to validate the full parser surface by comparing grouped parser projection, accepted token tuple, lookup table, canonical names, and the declared parser surface against a separate canonical surface. Canonical demo-path steps protected: `open project/document`, `retrieve relevant material`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `continue working`.
2. Preserved canonical command ordering in the CLI contract while rejecting added aliases, removed aliases, same-canonical alias substitutions, token reordering, and lookup-table shape/order drift. Canonical demo-path commands protected: `bootstrap`, `context-basket`, `diff-preview`, `diff`, and `terminal`.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for extra accepted alias, removed accepted alias, substituted accepted alias, same-canonical `diff` to `diff_preview` substitution, parser-token reorder, declared-surface alias drift, self-consistent declared-surface drift, grouped parser drift, lookup-table token-substitution drift, and lookup-table shape/order drift. Canonical demo-path steps protected: open project/document, retrieve/context basket, patch preview, and continued CLI operation.
4. Regenerated `THREAD.md` and `THREAD_PACKET.md` so the handoff claims match the final implementation, test coverage, branch-tip review basis, canonical demo-path mapping, and ownership accounting. Canonical demo-path step protected: `continue working`.

### Canonical Demo-Path Mapping

- Task 1 protects the `open project/document` step by keeping the `bootstrap` CLI entrypoint aligned with the canonical command catalog.
- Task 2 protects the `retrieve relevant material` and `promote or gather context into the basket` steps by keeping the `context-basket` CLI entrypoint deterministic.
- Task 3 protects the `preview and apply or reject a patch` step by preventing parser/catalog drift for the `diff-preview` and `diff` CLI surface.
- Task 4 protects reviewability of the same demo path by refreshing handoff metadata with the exact branch-tip review basis.
- Final demo-path statement: this handoff makes the open project/document, retrieve/context basket, patch preview, and continued CLI operation portions of the CLI-first MVP loop more real by preventing parser/catalog drift for `bootstrap`, `context-basket`, `diff-preview`, `diff`, and `terminal` while Textual remains disabled.

### Files Changed

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`

### Commands Run + Outcomes

- `python3 -m unittest tests.unit.test_commands_catalog -v`: PASS
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS
- Final verification pass: `2026-04-28T23:21:20Z`

### Risks / Blockers

- Risk: high, because command-contract behavior is operator-facing.
- Blockers: none.

### Required Handoff Fields

- Branch name: `codex/feat-commands`
- Scope completed: command-catalog contract now validates canonical command ordering and rejects parser/catalog drift across accepted tokens, declared parser surface, grouped parser surface, lookup-table shape/order, and canonical names.
- Files changed: listed above.
- Commands run with results: listed above.
- Risks/blockers: listed above.
- Roadmap item(s) affected: Milestone 3 CLI compatibility while the package/layout migration lands; `feat-commands` CLI compatibility and migration-safe entrypoints.
- Vision capability affected: canonical engine contract stability while the CLI remains the active operator surface.
- Routing/provider impact note: none; this change does not touch model routing or provider configuration.

### Reviewer Packet `20260428T231936Z` Fix Satisfaction

1. Required fix 1, concrete canonical demo-path mapping: satisfied by mapping the command-catalog contract to open project/document (`bootstrap`), retrieve/context basket (`context-basket`), patch preview (`diff-preview` and `diff`), and continued CLI operation (`terminal`).
2. Required fix 2, command-catalog-only scope: satisfied; this pass does not add command behavior, CLI flags, Textual work, routing/provider changes, or broader catalog expansion.
3. Required fix 3, approved shared-test exception and limited changed-file list: satisfied by preserving `tests/unit/test_commands_catalog.py` as the approved shared-by-approval test edit and keeping changed files limited to `src/qual/commands/catalog.py`, `tests/unit/test_commands_catalog.py`, `THREAD.md`, and `THREAD_PACKET.md`.
4. Gate rerun: focused catalog regressions and all required gates passed at `2026-04-28T23:21:17Z`.

### Reviewer Packet `20260428T231539Z` Fix Satisfaction

1. Regenerate packet from actual merge candidate: satisfied by submitting the full branch tip after the `2026-04-28T23:21:20Z` fixer pass as the review basis.
2. Submit full branch-tip implementation or clean branch: satisfied by submitting the full branch-tip implementation; no code-bearing command catalog or command catalog test commits are hidden as metadata-only.
3. Reject full parser-surface drift: satisfied by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, and canonical names, including self-consistent declared-surface alias substitutions.
4. Add or retain focused parser-surface drift tests: satisfied by the focused command-catalog tests listed in Tasks Completed.
5. Update completed tasks with canonical demo-path mapping: satisfied by mapping the work to open project/document (`bootstrap`), retrieve/context basket (`context-basket`), patch preview (`diff-preview` and `diff`), and continued CLI operation (`terminal`).
6. Correct ownership accounting: satisfied by recording `tests/unit/test_commands_catalog.py` as an approved shared-by-approval test edit and integrator-locked edits as `no`.
7. Rerun and report required gates: satisfied by the full required gate sequence passing at `2026-04-28T23:21:17Z`.
