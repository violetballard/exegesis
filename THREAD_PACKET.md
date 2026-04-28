# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Review basis: final branch tip after this fixer pass for reviewer packet `20260428T234152Z`; implementation, tests, scope-check support, and handoff metadata are reviewed together.
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
- Previous branch-tip review basis `8a84d0e0e` is superseded by this reviewer-fix pass; the actual merge candidate is the final `codex/feat-commands` branch tip after the `20260428T234152Z` fixes and gate rerun.
- Metadata-only handoff files are limited to `THREAD.md` and `THREAD_PACKET.md`.

### Shared / Integrator-Locked Accounting

- Lane-owned implementation edit: `src/qual/commands/catalog.py`.
- Approved shared-by-approval test edit: `tests/unit/test_commands_catalog.py`.
- Integrator-locked edits: no.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: reviewer-fix pass stays metadata-only; full branch-tip merge range is over the high-risk size budget and is submitted explicitly below for review rather than hidden behind a stale narrow basis.
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Hardened `command_cli_contract()` to validate the full parser surface by comparing grouped parser projection, accepted token tuple, lookup table, canonical names, and the declared parser surface against a separate canonical surface. Canonical demo-path steps protected: `open project/document`, `retrieve relevant material`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `continue working`.
2. Preserved canonical command ordering in the CLI contract while rejecting added aliases, removed aliases, same-canonical alias substitutions, token reordering, and lookup-table shape/order drift. Canonical demo-path commands protected: `bootstrap`, `context-basket`, `diff-preview`, `diff`, and `terminal`.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for extra accepted alias, removed accepted alias, substituted accepted alias, same-canonical `diff` to `diff_preview` substitution, parser-token reorder, declared-surface alias drift, declared-surface order drift, self-consistent declared-surface drift, grouped parser drift, lookup-table token-substitution drift, lookup-table added same-canonical alias drift, and lookup-table shape/order drift. Canonical demo-path steps protected: open project/document, retrieve/context basket, patch preview, and continued CLI operation.
4. Regenerated `THREAD.md` and `THREAD_PACKET.md` so the handoff claims match the final implementation, full branch-tip file range, test coverage, branch-tip review basis, canonical demo-path mapping, and ownership accounting. Canonical demo-path step protected: `continue working`.

### Canonical Demo-Path Mapping

- Task 1 protects the `open project/document` step by keeping the `bootstrap` CLI entrypoint aligned with the canonical command catalog.
- Task 2 protects the `retrieve relevant material` and `promote or gather context into the basket` steps by keeping the `context-basket` CLI entrypoint deterministic.
- Task 3 protects the `preview and apply or reject a patch` step by preventing parser/catalog drift for the `diff-preview` and `diff` CLI surface.
- Task 4 protects reviewability of the same demo path by refreshing handoff metadata with the exact branch-tip review basis.
- Final demo-path statement: this handoff makes the open project/document, retrieve/context basket, patch preview, and continued CLI operation portions of the CLI-first MVP loop more real by preventing parser/catalog drift for `bootstrap`, `context-basket`, `diff-preview`, `diff`, and `terminal` while Textual remains disabled.

### Files Changed

- `src/qual/commands/catalog.py` - lane-owned command catalog and CLI contract implementation.
- `src/qual/commands/__init__.py` - lane-owned command package export surface for the new command catalog contract helpers.
- `src/qual/commands/canonical.py` - lane-owned compatibility wrapper for canonical command resolution.
- `src/qual/commands/diff_preview.py` - lane-owned diff-preview command support used by the canonical patch-preview command surface.
- `tests/unit/test_commands_catalog.py` - approved shared-by-approval regression coverage for command-catalog and parser-surface drift.
- `tests/unit/test_diff_preview.py` - approved shared-by-approval regression coverage for the diff-preview command support.
- `scripts/scope-check.sh` - shared scope-check support so `make scope-check` can evaluate this lane's approved shared test and the active engine-first lane ownership rules.
- `THREAD.md` - metadata-only thread pointer.
- `THREAD_PACKET.md` - metadata-only handoff packet.

### Commands Run + Outcomes

- `python3 -m unittest tests.unit.test_commands_catalog -v`: PASS (56 tests)
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS
- Final verification pass: `2026-04-28T23:43:52Z`

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

### Reviewer Packet `20260428T233046Z` Fix Satisfaction

1. Regenerate the review packet from the actual merge candidate: satisfied by using the final `codex/feat-commands` branch tip as the review basis and stating that implementation, tests, scope-check support, and metadata are reviewed together.
2. Reject full parser-surface drift: satisfied by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, and canonical names, including same-canonical alias substitutions.
3. Add or retain focused parser-surface drift tests: satisfied by the focused command-catalog tests listed in Tasks Completed.
4. Update completed tasks with canonical demo-path mapping: satisfied in `Tasks Completed` and `Canonical Demo-Path Mapping`.
5. Correct ownership/accounting language: satisfied by distinguishing lane-owned command files, approved shared-by-approval tests, shared scope-check support, metadata-only files, and `Integrator-locked edits: no`.

### Reviewer Packet `20260428T233410Z` Fix Satisfaction

1. Parser-surface validation against an explicit canonical parser surface: satisfied by `_CANONICAL_CLI_COMMAND_SURFACE`, `_CLI_COMMAND_SURFACE`, `_CLI_ENTRYPOINTS`, grouped parser projection, accepted token tuple, lookup-table, and canonical-name checks in `command_cli_contract()`.
2. Drift regression matrix: satisfied by focused tests for added same-canonical alias, substituted same-canonical alias, token reorder, removed token, lookup-table shape/order drift, lookup-table token substitution drift, and lookup-table added same-canonical alias drift.
3. Canonical demo-path mapping: satisfied in `Tasks Completed` and `Canonical Demo-Path Mapping` by mapping the work to open project/document, retrieve/context basket, patch preview, and continued CLI operation.
4. Actual merge-candidate packet: satisfied by reviewing the final branch tip after this fixer pass and stating that implementation, tests, scope-check support, and packet metadata are reviewed together.

### Reviewer Packet `20260428T233637Z` Fix Satisfaction

1. Strengthen `command_cli_contract()` parser-token drift validation: satisfied by validating the accepted CLI token tuple, declared canonical CLI surface, grouped parser projection, lookup-table shape/order, and canonical command order against `_CANONICAL_CLI_COMMAND_SURFACE`.
2. Add same-canonical alias substitution regression coverage: satisfied by tests that reject replacing accepted tokens with same-canonical aliases such as `diff_preview` and adding `open` as an accepted `bootstrap` parser row.
3. State the concrete canonical demo-path step: satisfied in `Tasks Completed` and `Canonical Demo-Path Mapping` by mapping the work to open project/document, retrieve/context basket, patch preview, and continued CLI operation.
4. Correct ownership accounting: satisfied by listing the command files as lane-owned, tests as approved shared-by-approval edits, scope-check as shared gate support, and integrator-locked edits as `no`.

### Reviewer Packet `20260428T234152Z` Fix Satisfaction

1. Regenerate the review packet from the actual merge candidate: satisfied by anchoring review to the final `codex/feat-commands` branch tip after this fixer pass, with implementation, tests, `scripts/scope-check.sh`, and handoff metadata reviewed together.
2. Strengthen `command_cli_contract()` so parser-surface drift is rejected: satisfied by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, and canonical names against `_CANONICAL_CLI_COMMAND_SURFACE`, including same-canonical alias substitutions, extra accepted aliases, removed aliases, and token/order drift.
3. Add focused parser-surface drift regression coverage: satisfied by tests for added same-canonical alias drift, substituted same-canonical alias drift, removed accepted alias drift, parser-token reorder, declared-surface drift, lookup-table token-substitution drift, and lookup-table shape/order drift.
4. Reconcile ownership accounting against `THREAD_OWNERSHIP.md`: satisfied by distinguishing lane-owned command files, approved shared-by-approval tests, shared scope-check support, metadata-only files, and `Integrator-locked edits: no`.
5. Rerun and report required gates against the final reviewed tip: satisfied by this fixer pass rerunning `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Reviewer Packet `20260428T231936Z` Fix Satisfaction

1. Required fix 1, concrete canonical demo-path mapping: satisfied by mapping the command-catalog contract to open project/document (`bootstrap`), retrieve/context basket (`context-basket`), patch preview (`diff-preview` and `diff`), and continued CLI operation (`terminal`).
2. Required fix 2, command-surface scope: satisfied under the current full branch-tip accounting; this pass does not add CLI flags, Textual work, routing/provider changes, or non-command business logic.
3. Required fix 3, approved shared-test exception and complete changed-file list: satisfied by listing the real nine-file branch-tip range and distinguishing lane-owned command files, approved shared tests, scope-check support, and metadata files.
4. Gate rerun: focused catalog regressions and all required gates passed at `2026-04-28T23:27:51Z`.

### Reviewer Packet `20260428T231539Z` Fix Satisfaction

1. Regenerate packet from actual merge candidate: satisfied by submitting the full branch tip after the `2026-04-28T23:31:10Z` fixer pass as the review basis.
2. Submit full branch-tip implementation or clean branch: satisfied by submitting the full branch-tip implementation; no code-bearing command or command-test commits are hidden as metadata-only.
3. Reject full parser-surface drift: satisfied by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, and canonical names, including self-consistent declared-surface alias substitutions.
4. Add or retain focused parser-surface drift tests: satisfied by the focused command-catalog tests listed in Tasks Completed.
5. Update completed tasks with canonical demo-path mapping: satisfied by mapping the work to open project/document (`bootstrap`), retrieve/context basket (`context-basket`), patch preview (`diff-preview` and `diff`), and continued CLI operation (`terminal`).
6. Correct ownership accounting: satisfied by recording command files as lane-owned, tests as approved shared-by-approval edits, scope-check as shared gate support, and integrator-locked edits as `no`.
7. Rerun and report required gates: satisfied by the full required gate sequence passing at `2026-04-28T23:31:10Z`.
