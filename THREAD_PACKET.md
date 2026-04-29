# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Review basis: final branch tip after this fixer pass for reviewer packet `20260429T004707Z`; implementation, tests, scope-check support, and handoff metadata are reviewed together.
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
- Previous branch-tip review basis `8c7cfbea1` is superseded by this reviewer-fix pass; the actual merge candidate is the final `codex/feat-commands` branch tip after the `20260429T004707Z` fixes and gate rerun.
- This fixer pass also satisfies reviewer packet `20260429T004707Z`; no command-catalog implementation or test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are classified as metadata-only.
- Metadata-only handoff files are limited to `THREAD.md` and `THREAD_PACKET.md`.

### Shared / Integrator-Locked Accounting

- Lane-owned implementation edit: `src/qual/commands/catalog.py`.
- Approved shared-by-approval test edit: `tests/unit/test_commands_catalog.py`.
- Integrator-locked edits: no.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: this reviewer-fix pass stays narrow: one focused command-catalog validation refactor, one focused shared-by-approval test addition, and handoff metadata updates. The full branch-tip merge range remains over the high-risk size budget and is submitted explicitly below for review rather than hidden behind a stale narrow basis.
- Max fix attempts per failing gate: `2`

### Tasks Completed

1. Hardened `command_cli_contract()` to validate the full parser surface through `_validate_cli_parser_surface()`, comparing grouped parser projection, accepted token tuple, lookup table, canonical names, declared parser surface, and explicit canonical surface/token/lookup projections against a separate canonical surface. Canonical demo-path steps protected: `open project/document`, `retrieve relevant material`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `continue working`.
2. Preserved canonical command ordering in the CLI contract while rejecting added aliases, removed aliases, same-canonical alias substitutions, token reordering, and lookup-table shape/order drift. Canonical demo-path commands protected: `bootstrap`, `context-basket`, `diff-preview`, `diff`, and `terminal`.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for extra accepted alias, removed accepted alias, substituted accepted alias, same-canonical `diff` to `diff_preview` substitution in accepted and declared parser surfaces, same-canonical alias order drift in accepted tokens and declared surface, canonical command order drift, parser-token reorder, declared-surface alias drift, declared-surface order drift, self-consistent declared-surface drift, grouped parser drift, lookup-table token-substitution drift, lookup-table target-substitution drift, lookup-table added same-canonical alias drift, lookup-table removed-token drift, lookup-table shape/order drift, and canonical token/lookup projection alignment. Canonical demo-path steps protected: open project/document, retrieve/context basket, patch preview, and continued CLI operation.
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

- `python3 -m unittest tests.unit.test_commands_catalog -v`: PASS (62 tests)
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS
- Final verification pass: PASS in final gate rerun for reviewer packet `20260429T004707Z`.
- Exact-tip fixer verification: PASS after the `20260429T004707Z` handoff metadata refresh.

### Risks / Blockers

- Risk: high, because command-contract behavior is operator-facing.
- Blockers: none.

### Required Handoff Fields

- Branch name: `codex/feat-commands`
- Scope completed: command-catalog contract now validates canonical command ordering and rejects parser/catalog drift across accepted tokens, declared parser surface, grouped parser surface, lookup-table shape/order, canonical token/lookup projections, and canonical names.
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

### Reviewer Packet `20260428T234728Z` Fix Satisfaction

1. Regenerate the packet from the actual merge candidate: satisfied by keeping this packet anchored to the current `codex/feat-commands` branch tip and reviewing implementation, tests, scope-check support, and handoff metadata together.
2. Do not classify implementation/test commits as metadata-only: satisfied by stating that no commit modifying `src/qual/commands/catalog.py` or `tests/unit/test_commands_catalog.py` is metadata-only, and by listing the full non-metadata branch-tip file range.
3. Strengthen parser-surface drift rejection: satisfied by `command_cli_contract()` validating the accepted token tuple, declared canonical surface, grouped parser projection, lookup-table shape/order, and canonical names against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Add focused parser-surface drift tests: satisfied by focused catalog tests for added aliases, removed aliases, same-canonical alias substitutions, token reorder, declared-surface drift, grouped parser drift, lookup-table token substitution, and lookup-table shape/order drift.
5. Update demo-path mapping and ownership accounting: satisfied by the `Tasks Completed`, `Canonical Demo-Path Mapping`, `Files Changed`, and `Shared / Integrator-Locked Accounting` sections.
6. Rerun required gates against the final reviewed tip: satisfied by `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passing at `2026-04-28T23:58:30Z`.

### Reviewer Packet `20260428T234820Z` Fix Satisfaction

1. Regenerate the packet from the actual merge candidate, or submit a clean branch whose diff is exactly the intended narrow command-catalog slice: satisfied by anchoring this packet to the final `codex/feat-commands` branch tip and reviewing implementation, tests, scope-check support, and handoff metadata together.
2. Do not classify commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as metadata-only if they modify `src/qual/commands/catalog.py` or tests: satisfied by stating that no code-bearing command-catalog implementation or test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are metadata-only.
3. Strengthen the reviewed implementation so `command_cli_contract()` rejects added aliases, removed aliases, same-canonical alias substitutions, token reorder, and lookup-table shape/order drift: satisfied by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, and canonical names against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Add focused regression tests for those parser-surface drift cases: satisfied by tests covering extra accepted aliases, removed accepted aliases, substituted accepted aliases, same-canonical substitutions, same-canonical order drift, parser-token reorder, declared-surface drift, grouped parser drift, lookup-table token substitution, and lookup-table shape/order drift.
5. Update the handoff with explicit canonical demo-path mapping and corrected shared-file ownership accounting: satisfied in `Tasks Completed`, `Canonical Demo-Path Mapping`, `Files Changed`, and `Shared / Integrator-Locked Accounting`.
6. Rerun and report the required gates against the final reviewed tip: satisfied by this fixer pass rerunning and recording `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Reviewer Packet `20260428T235008Z` Fix Satisfaction

1. Regenerate the packet from the actual merge candidate, or submit a clean branch whose diff is exactly the intended narrow command-catalog slice: satisfied by anchoring this packet to the final `codex/feat-commands` branch tip and reviewing implementation, tests, scope-check support, and handoff metadata together.
2. Do not classify commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as metadata-only if they modify `src/qual/commands/catalog.py` or tests: satisfied by stating that no code-bearing command-catalog implementation or test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are metadata-only.
3. Strengthen the reviewed implementation so `command_cli_contract()` rejects added aliases, removed aliases, same-canonical alias substitutions, token reorder, and lookup-table shape/order drift: satisfied by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, and canonical names against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Add focused regression tests for those parser-surface drift cases: satisfied by tests covering extra accepted aliases, removed accepted aliases, substituted accepted aliases, same-canonical substitutions, parser-token reorder, declared-surface drift, grouped parser drift, lookup-table token substitution, and lookup-table shape/order drift.
5. Update the handoff with explicit canonical demo-path mapping and corrected shared-file ownership accounting: satisfied in `Tasks Completed`, `Canonical Demo-Path Mapping`, `Files Changed`, and `Shared / Integrator-Locked Accounting`.
6. Rerun and report the required gates against the final reviewed tip: satisfied by this fixer pass rerunning and recording `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Reviewer Packet `20260428T235333Z` Fix Satisfaction

1. Strengthen `command_cli_contract()` parser-surface validation: satisfied by validating accepted parser tokens, declared canonical surface, grouped parser projection, lookup-table order/shape, and canonical command order against `_CANONICAL_CLI_COMMAND_SURFACE`.
2. Add parser-surface drift regression tests: satisfied by focused tests for alias substitution that resolves to the same canonical command, same-canonical alias order drift in accepted tokens and declared surface, added aliases, removed aliases, parser-token reorder, grouped parser drift, and lookup-table drift.
3. Name the exact canonical demo-path step: satisfied by mapping the work to open project/document, retrieve/context basket, patch preview, and continued CLI operation.
4. Correct ownership accounting: satisfied by listing command files as lane-owned, tests as approved shared-by-approval, `scripts/scope-check.sh` as shared gate support, metadata files as metadata-only, and integrator-locked edits as `no`.

### Reviewer Packet `20260428T235908Z` Fix Satisfaction

1. Regenerate the packet from the actual merge candidate tip: satisfied by anchoring this packet to the final `codex/feat-commands` branch tip after this fixer pass and reviewing implementation, tests, scope-check support, and handoff metadata together.
2. Stop classifying `0b31059888dc17a5eb264782b00be835aa4673d3` as metadata-only: satisfied by stating that no command-catalog implementation or test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are metadata-only.
3. Reject full parser-surface drift: satisfied by `command_cli_contract()` validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, and canonical names against `_CANONICAL_CLI_COMMAND_SURFACE`, including added same-canonical aliases, removed tokens, same-canonical substitutions, token reorder, and lookup-table shape/order drift.
4. Include focused parser-surface drift regression tests: satisfied by tests covering extra accepted aliases, removed accepted aliases, substituted accepted aliases, same-canonical substitutions, same-canonical order drift, parser-token reorder, declared-surface drift, grouped parser drift, lookup-table token substitution, and lookup-table shape/order drift.
5. Update the handoff packet with explicit canonical demo-path mapping: satisfied in `Tasks Completed` and `Canonical Demo-Path Mapping` by mapping the work to open project/document, retrieve/context basket, patch preview, and continued CLI operation.
6. Rerun required gates against the final reviewed tip: satisfied by this fixer pass rerunning and recording `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Reviewer Packet `20260429T000211Z` Fix Satisfaction

1. Regenerate the packet from the actual merge candidate, or submit a clean branch whose diff is exactly the intended narrow command-catalog slice: satisfied by anchoring this packet to the final `codex/feat-commands` branch tip after this fixer pass and reviewing implementation, tests, scope-check support, and handoff metadata together.
2. Do not classify commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as metadata-only if they modify `src/qual/commands/catalog.py` or tests: satisfied by stating that no command-catalog implementation or test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are metadata-only.
3. Strengthen the reviewed implementation so `command_cli_contract()` rejects added aliases, removed aliases, same-canonical alias substitutions, token reorder, and lookup-table shape/order drift: satisfied by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, canonical token/lookup projections, and canonical names against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Add or retain focused regression tests for those parser-surface drift cases: satisfied by tests covering extra accepted aliases, removed accepted aliases, substituted accepted aliases, same-canonical substitutions, same-canonical order drift, parser-token reorder, declared-surface drift, grouped parser drift, lookup-table token substitution, lookup-table shape/order drift, and canonical token/lookup projection alignment.
5. Update the handoff with explicit canonical demo-path mapping and corrected shared-file ownership accounting: satisfied in `Tasks Completed`, `Canonical Demo-Path Mapping`, `Files Changed`, and `Shared / Integrator-Locked Accounting`.
6. Rerun and report the required gates against the final reviewed tip: this fixer pass reruns and records `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Reviewer Packet `20260429T000757Z` Fix Satisfaction

1. Regenerate the packet from the actual merge candidate, or submit a clean branch whose diff is exactly the intended narrow command-catalog slice: satisfied by anchoring this packet to the final `codex/feat-commands` branch tip after this fixer pass and reviewing implementation, tests, scope-check support, and handoff metadata together.
2. Do not classify commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as metadata-only if they modify `src/qual/commands/catalog.py` or tests: satisfied by stating that no command-catalog implementation or test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are metadata-only.
3. Strengthen the reviewed implementation so `command_cli_contract()` rejects added aliases, removed aliases, same-canonical alias substitutions, token reorder, and lookup-table shape/order drift: satisfied by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, canonical token/lookup projections, and canonical names against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Add or retain focused regression tests for those parser-surface drift cases: satisfied by tests covering extra accepted aliases, removed accepted aliases, substituted accepted aliases, same-canonical substitutions, same-canonical order drift, parser-token reorder, declared-surface drift, grouped parser drift, lookup-table token substitution, lookup-table shape/order drift, and canonical token/lookup projection alignment.
5. Update the handoff with explicit canonical demo-path mapping and corrected shared-file ownership accounting: satisfied in `Tasks Completed`, `Canonical Demo-Path Mapping`, `Files Changed`, and `Shared / Integrator-Locked Accounting`.
6. Rerun and report the required gates against the final reviewed tip: this fixer pass reruns and records `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Reviewer Packet `20260429T001026Z` Fix Satisfaction

1. Strengthen `command_cli_contract()` so it validates parser surface itself: satisfied by comparing accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, canonical surface/token/lookup projections, and canonical names against `_CANONICAL_CLI_COMMAND_SURFACE`.
2. Add focused parser-surface drift tests: satisfied by tests covering added same-canonical alias `open`, same-canonical `diff` to `diff_preview` substitution, removed accepted token, token reorder, and lookup-table shape/order drift, plus declared-surface, grouped parser, lookup-table token substitution, lookup-table target substitution, and lookup-table removed-token drift.
3. Update handoff canonical demo-path mapping: satisfied in `Tasks Completed`, `Canonical Demo-Path Mapping`, and the final demo-path statement by naming open project/document, retrieve/context basket, patch preview, and continued CLI operation.
4. Correct ownership accounting: satisfied by listing `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` as approved shared-by-approval tests, `scripts/scope-check.sh` as shared gate support, and `Integrator-locked edits: no`.
5. Required gates: this fixer pass reruns and records `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Reviewer Packet `20260429T001414Z` Fix Satisfaction

1. Regenerate the packet from the actual merge candidate tip: satisfied by anchoring this packet to the final `codex/feat-commands` branch tip after this fixer pass and reviewing implementation, tests, scope-check support, and handoff metadata together.
2. Do not classify commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as metadata-only if they modify `src/qual/commands/catalog.py` or `tests/unit/test_commands_catalog.py`: satisfied by submitting the full branch-tip implementation and listing command-catalog implementation and test files as reviewed files.
3. Strengthen `command_cli_contract()` so it rejects added aliases, removed aliases, same-canonical alias substitutions, token reorder, and lookup-table shape/order drift: satisfied by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, canonical names, and explicit canonical surface/token/lookup projections against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Add focused regression tests for those parser-surface drift cases: satisfied by tests covering extra accepted aliases, removed accepted aliases, substituted accepted aliases, same-canonical substitutions, same-canonical order drift, parser-token reorder, declared-surface drift, grouped parser drift, lookup-table token substitution, lookup-table target substitution, lookup-table removed-token drift, lookup-table shape/order drift, and canonical token/lookup projection alignment.
5. Update the files-changed and metadata-only sections to include every changed file, including `THREAD.md` if it remains changed: satisfied by the full Files Changed list and by limiting metadata-only handoff files to `THREAD.md` and `THREAD_PACKET.md`.
6. Rerun and report the required gates against the final reviewed tip: this fixer pass reruns and records `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Reviewer Packet `20260429T001930Z` Fix Satisfaction

1. Regenerate the handoff from the actual merge candidate tip: satisfied by anchoring review to the final `codex/feat-commands` branch tip after this fixer pass, with implementation, tests, scope-check support, `THREAD.md`, and `THREAD_PACKET.md` reviewed together.
2. Do not classify command-catalog implementation or test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as metadata-only: satisfied by submitting the full branch-tip implementation and listing command/test files as reviewed files.
3. Strengthen `command_cli_contract()` so it validates the parser surface itself: satisfied by comparing accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, canonical names, and explicit canonical token/lookup projections against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Add focused parser-surface drift tests: satisfied by tests covering added aliases, removed aliases, same-canonical substitutions such as `diff` to `diff_preview`, token reorder, declared-surface drift, grouped parser drift, lookup-table target drift, and lookup-table shape/order drift.
5. Update the handoff to name concrete canonical demo-path steps: satisfied by naming open project/document, retrieve/context basket, patch preview, and continued CLI operation in `Tasks Completed`, `Canonical Demo-Path Mapping`, and the final demo-path statement.
6. Rerun and report the required gates against the final reviewed tip: this fixer pass reruns and records `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Reviewer Packet `20260429T002214Z` Fix Satisfaction

1. Submit one coherent packet for the actual branch tip: satisfied by anchoring review to the final `codex/feat-commands` branch tip after this fixer pass, with implementation, tests, scope-check support, `THREAD.md`, and `THREAD_PACKET.md` reviewed together.
2. Clean narrow-branch alternative: not used, because this packet intentionally submits the actual branch tip and no longer asks reviewers to ignore code-bearing commits.
3. Strengthen `command_cli_contract()` so it rejects parser-surface drift directly: satisfied by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, canonical names, and explicit canonical token/lookup projections against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Add focused regression tests for parser-surface drift classes: satisfied by tests covering added accepted aliases, removed accepted aliases, substituted accepted aliases, same-canonical substitutions such as `diff` to `diff_preview`, parser-token reorder, declared-surface drift, grouped parser drift, lookup-table target drift, lookup-table removed-token drift, lookup-table shape/order drift, and canonical command order drift.
5. Regenerate the handoff packet with accurate accounting and fresh gates: satisfied by listing the complete branch-tip file range, limiting metadata-only classification to `THREAD.md` and `THREAD_PACKET.md`, distinguishing shared-by-approval tests from integrator-locked edits, naming concrete canonical demo-path steps, and rerunning all required gates.

### Reviewer Packet `20260429T002514Z` Fix Satisfaction

1. Strengthen `command_cli_contract()` so it validates the parser surface itself: already satisfied at this branch tip by comparing accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, canonical names, and explicit canonical token/lookup projections against `_CANONICAL_CLI_COMMAND_SURFACE`.
2. Add focused regression tests for same-canonical parser drift and token removal/reorder: satisfied by tests covering extra same-canonical accepted alias `open`, same-canonical `diff` to `diff_preview` substitution, removed accepted token, parser-token reorder, lookup-table added same-canonical alias drift, lookup-table removed-token drift, and lookup-table shape/order drift.
3. Update handoff tasks with exact canonical demo-path steps: satisfied in `Tasks Completed`, `Canonical Demo-Path Mapping`, and the final demo-path statement by naming open project/document, retrieve/context basket, patch preview, and continued CLI operation.
4. Correct ownership note: satisfied by separating lane-owned command files, approved shared-by-approval tests, scope-check support, metadata-only handoff files, and `Integrator-locked edits: no`.

### Reviewer Packet `20260429T002758Z` Fix Satisfaction

1. Submit one coherent review packet for the actual merge candidate: satisfied by anchoring review to the final `codex/feat-commands` branch tip after this fixer pass, with implementation, tests, scope-check support, `THREAD.md`, and `THREAD_PACKET.md` reviewed together.
2. Remove the claim that commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are metadata-only if they modify implementation or tests: satisfied by submitting the full branch-tip implementation and limiting metadata-only classification to `THREAD.md` and `THREAD_PACKET.md`.
3. Strengthen `command_cli_contract()` if reviewing the narrow slice: already satisfied at the actual branch tip by validating accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, canonical names, and explicit canonical token/lookup projections against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Regenerate files-changed and ownership sections against `THREAD_OWNERSHIP.md`: satisfied by distinguishing lane-owned command files, approved shared-by-approval tests, shared scope-check support, metadata-only handoff files, and true integrator-locked edits as `no`.
5. Rerun and report all required gates against the exact reviewed branch tip: this fixer pass reruns and records `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Reviewer Packet `20260429T003118Z` Fix Satisfaction

1. Regenerate the handoff packet from the actual merge candidate tip: satisfied by anchoring review to the final `codex/feat-commands` branch tip after this fixer pass, with implementation, tests, scope-check support, `THREAD.md`, and `THREAD_PACKET.md` reviewed together.
2. Submit a review basis that matches the code being reviewed: satisfied by submitting the full branch-tip implementation and no longer asking reviewers to ignore code-bearing command-catalog or command-test commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
3. Validate parser-surface drift directly: satisfied by `command_cli_contract()` comparing the accepted parser token tuple, lookup table shape/order, declared canonical parser surface, grouped parser projection, canonical command order, and explicit canonical token/lookup projections against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Add focused parser-surface drift tests: satisfied by tests for same-canonical token substitution, accepted-token removal, accepted-token reorder, lookup-table drift, declared-surface drift, grouped parser drift, and canonical command order drift.
5. Correct ownership accounting: satisfied by listing `src/qual/commands/**` files as lane-owned, `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` as approved shared-by-approval tests, `scripts/scope-check.sh` as shared scope-check support, metadata files separately, and integrator-locked edits as `no`.

### Reviewer Packet `20260429T003451Z` Fix Satisfaction

1. Regenerate the handoff packet from the actual `codex/feat-commands` branch tip: satisfied by anchoring this packet to the final branch tip after this fixer pass, with implementation, tests, scope-check support, `THREAD.md`, and `THREAD_PACKET.md` reviewed together.
2. Do not classify code-bearing commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as metadata-only: satisfied by submitting the full branch-tip implementation and limiting metadata-only classification to `THREAD.md` and `THREAD_PACKET.md`.
3. List every changed file and distinguish ownership categories: satisfied by the Files Changed and Shared / Integrator-Locked Accounting sections, which separate lane-owned command files, approved shared-by-approval tests, shared scope-check support, metadata-only handoff files, and integrator-locked edits as `no`.
4. Update completed tasks with canonical demo-path steps and final AGENTS.md demo-path statement: satisfied in Tasks Completed, Canonical Demo-Path Mapping, and the final demo-path statement by naming open project/document, retrieve/context basket, patch preview, and continued CLI operation.
5. Rerun and report required gates against the exact reviewed tip: this fixer pass reruns and records `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Reviewer Packet `20260429T003757Z` Fix Satisfaction

1. Regenerate the packet from the actual merge candidate tip: satisfied by anchoring this packet to the final `codex/feat-commands` branch tip after this fixer pass, with implementation, tests, scope-check support, `THREAD.md`, and `THREAD_PACKET.md` reviewed together.
2. Stop classifying commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as metadata-only if they modify implementation or tests: satisfied by submitting the full branch-tip implementation and limiting metadata-only classification to `THREAD.md` and `THREAD_PACKET.md`.
3. Strengthen `command_cli_contract()` so it validates the parser surface itself, including accepted token tuple, token order, same-canonical alias substitutions, removed tokens, added tokens, lookup-table shape/order, and canonical command order: satisfied by comparing accepted tokens, declared canonical surface, grouped parser projection, lookup-table shape/order, canonical names, and explicit canonical token/lookup projections against `_CANONICAL_CLI_COMMAND_SURFACE`.
4. Add focused regression tests for those parser-surface drift cases: satisfied by tests covering extra accepted aliases, removed accepted aliases, substituted accepted aliases, same-canonical substitutions such as `diff` to `diff_preview`, same-canonical order drift, parser-token reorder, declared-surface drift, grouped parser drift, lookup-table token substitution, lookup-table target substitution, lookup-table removed-token drift, lookup-table shape/order drift, and canonical command order drift.
5. Update handoff tasks with exact canonical demo-path steps protected by the work: satisfied in `Tasks Completed`, `Canonical Demo-Path Mapping`, and the final demo-path statement by naming open project/document, retrieve/context basket, patch preview, and continued CLI operation.
6. Rerun and report `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` against the exact reviewed tip: this fixer pass reruns and records all required gates.

### Reviewer Packet `20260429T004039Z` Fix Satisfaction

1. Regenerate the handoff packet from the actual `codex/feat-commands` merge candidate tip: satisfied by anchoring this packet to the final branch tip after this fixer pass, with implementation, tests, scope-check support, `THREAD.md`, and `THREAD_PACKET.md` reviewed together.
2. Do not classify code-bearing commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as metadata-only: satisfied by submitting the full branch-tip implementation and limiting metadata-only classification to `THREAD.md` and `THREAD_PACKET.md`.
3. Strengthen `command_cli_contract()` so it validates the accepted parser token tuple and lookup table against an explicit canonical parser surface: satisfied by `_CANONICAL_CLI_COMMAND_SURFACE`, `_CLI_COMMAND_SURFACE`, `_CLI_ENTRYPOINTS`, grouped parser projection, accepted token tuple, lookup-table shape/order, canonical names, and explicit canonical token/lookup projection checks.
4. Add focused same-canonical parser-drift tests: satisfied by tests covering added alias `open`, removed accepted token, substituted alias `diff_preview`, same-canonical token/order drift, declared-surface drift, grouped parser drift, lookup-table token/target substitution, lookup-table removed-token drift, lookup-table shape/order drift, and canonical command order drift.
5. Restate the canonical demo-path step this work makes more real: satisfied by naming open project/document, retrieve/context basket, patch preview/apply-reject support, and continued CLI operation while Textual remains disabled.

### Reviewer Packet `20260429T004322Z` Fix Satisfaction

1. Strengthen `command_cli_contract()` so it validates the parser surface itself: satisfied by comparing accepted CLI tokens, token order, lookup-table shape/order, declared canonical parser surface, grouped parser projection, canonical command order, and explicit canonical token/lookup projections against `_CANONICAL_CLI_COMMAND_SURFACE`.
2. Add focused parser-surface drift tests: satisfied by tests covering added same-canonical alias `open`, removed accepted token, token reordering, same-canonical alias substitution such as `diff` to `diff_preview`, lookup-table added same-canonical alias drift, lookup-table removed-token drift, lookup-table token/target substitution drift, and lookup-table shape/order drift.
3. Update the handoff packet with exact canonical demo-path steps: satisfied by mapping this command-catalog work to open project/document (`bootstrap`), retrieve/context basket (`context-basket`), patch preview/apply-reject support (`diff-preview` and `diff`), and continued CLI operation (`terminal`).
4. Correct ownership accounting: satisfied by listing lane-owned command files, approved shared-by-approval tests, shared scope-check support, metadata-only handoff files, and `Integrator-locked edits: no`.
5. Rerun required gates against the final reviewed tip: this fixer pass reruns and records `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Reviewer Packet `20260429T004707Z` Fix Satisfaction

1. Update the handoff packet's files changed section to include every file changed through the current branch tip, separating implementation files from metadata-only files: satisfied by the `Files Changed` section, which lists all command, test, scope-check, and handoff metadata files, and by the `Implementation Basis` metadata-only statement limiting metadata-only files to `THREAD.md` and `THREAD_PACKET.md`.
2. Add an explicit canonical demo-path statement: satisfied by `Canonical Demo-Path Mapping`, including the final demo-path statement naming open project/document, retrieve/context basket, patch preview/apply-reject support, and continued CLI operation.
3. Keep implementation scope unchanged unless regenerating metadata requires docs-only packet updates: satisfied; this fixer pass changes only `THREAD.md` and `THREAD_PACKET.md`.

### Reviewer Packet `20260428T234415Z` Fix Satisfaction

1. No numbered required fixes were requested. The reviewer approved the branch and listed no blocking findings.
2. Fresh required gates were rerun for this fixer packet: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed at `2026-04-28T23:58:30Z`.

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
