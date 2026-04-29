# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: actual branch tip after this fixer commit
- Review basis: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`
- Review range command: `git diff f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`
- Fixer scope: regenerate the handoff for the real branch tip and real review range named by the reviewer, stop treating code/test commits as metadata-only, disclose the shared/integrator-locked CLI parser edit, validate the live argparse parser choices directly, recompute branch-tip size accounting, map every completed task to canonical demo-path steps, and rerun the required gates.

## Traceability Correction

This packet intentionally uses the reviewer-observed actual branch range, `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`. The previous handoff was not traceable because it described a narrower command-catalog slice while the branch tip included additional code, test, and handoff commits.

Commit `f8cfa2337f661b52511ab8dde84d9d7d72288738` is not metadata-only. It changes `tests/unit/test_commands_catalog.py` as well as `THREAD.md` and `THREAD_PACKET.md`, so it remains part of the review range as test work.

The review target is the actual `codex/feat-commands` branch tip after this fixer commit, not `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and not `f8cfa2337f661b52511ab8dde84d9d7d72288738`.

## Scope Completed

1. Bound the real argparse top-level command surface in `src/qual/cli.py` to `command_cli_lookup_table()` and exposed raw `command_parser_tokens()`, so accepted parser tokens consume and report the same source as the command catalog.
   Canonical demo-path steps advanced: `open project/document` through `bootstrap`; `retrieve material` through `context-basket`; `preview/apply/reject patch` through `diff-preview` and `diff`; `continue working` through `terminal`.
2. Added live parser-surface parity checks to `command_cli_contract()` that compare raw argparse choices, canonical parser projection, catalog CLI tokens, and the lookup table, so same-canonical parser-token drift is rejected. This fixer pass also makes `src/qual/cli.py` locate the top-level argparse action by `dest="command"` before exposing parser tokens.
   Canonical demo-path steps advanced: `open project/document`, `retrieve material`, `preview/apply/reject patch`, and `continue working`, by preventing the CLI fallback command names for those steps from drifting away from the catalog.
3. Added and exported the MVP smoke-contract API: `CommandSmokeStep`, `CommandSmokeContract`, `command_mvp_smoke_contract()`, `command_mvp_smoke_commands()`, `command_mvp_smoke_argv()`, and `command_mvp_smoke_lookup_table()` in `src/qual/commands/catalog.py` and `src/qual/commands/__init__.py`.
   Canonical demo-path steps advanced: `open project/document` via `bootstrap`; `retrieve material` via `context-basket list`; `preview/apply/reject patch` via `diff-preview`; `continue working` via `terminal`.
4. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for parser-surface drift and smoke-contract public exports, including tests that mutate a real argparse parser's top-level `choices`, patch `_build_parser()` choices, and intercept `argparse._SubParsersAction.add_parser()` to rewrite the top-level `diff-preview` parser token.
   Canonical demo-path steps advanced: all command-backed fallback steps above, by proving the parser/catalog contract rejects live argparse token drift before integration.

## High-Risk Budget And Size Accounting

This is a high-risk handoff because it changes command surface validation and includes `src/qual/cli.py`, which `THREAD_OWNERSHIP.md` marks as both shared-by-approval for `feat-commands` and integrator-locked.

- Task budget: `4` completed tasks of `4` high-risk tasks allowed.
- Time budget: original high-risk target `30m`; this fixer pass is documentation and gate-rerun work.
- High-risk file budget: `6` files changed in the actual review range, within the `<=8` high-risk file limit.
- High-risk net LOC budget: exceeded in the actual review range. Current branch-tip accounting for `f8d860ed9..HEAD` is `2024 insertions(+), 109 deletions(-)`. This is explicitly disclosed for reviewer/integrator handling instead of being presented as a narrow catalog-only slice.
- Shared-by-approval file: `src/qual/cli.py`.
- Integrator-locked file: `src/qual/cli.py`.
- Approval basis for `src/qual/cli.py`: reviewer-required parser-surface traceability fix for the real CLI parser entrypoint; no routing/provider/config behavior is changed.

## Files Changed

Files changed in `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`:

- `THREAD.md`
- `THREAD_PACKET.md`
- `src/qual/cli.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

Classification:

- Implementation: `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`
- Tests: `tests/unit/test_commands_catalog.py`
- Handoff metadata: `THREAD.md`, `THREAD_PACKET.md`

## Ownership Accounting

- Lane-owned implementation edits: `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`
- Shared-by-approval edits: `src/qual/cli.py`, required because the fix binds and validates the actual argparse parser surface.
- Integrator-locked edits: `src/qual/cli.py`, disclosed here for explicit review/integration approval.
- Test edits: `tests/unit/test_commands_catalog.py`, limited to command-contract and parser-surface regression coverage.
- Non-owned support edits: none.

## Regression Coverage

- `test_actual_argparse_surface_matches_the_command_contract` verifies the live argparse parser surface matches the command catalog.
- `test_command_cli_contract_rejects_actual_parser_surface_mismatch`, `test_command_cli_contract_rejects_real_argparse_choice_drift`, `test_command_cli_contract_rejects_mutated_real_argparse_choices`, and `test_command_cli_contract_rejects_actual_add_parser_token_drift` verify same-canonical parser drift, removed tokens, substituted tokens, added aliases, reordered parser choices, direct mutation of the actual argparse choices map, and a real top-level `add_parser()` token rewrite are rejected.
- `test_public_mvp_smoke_exports_track_the_demo_path` verifies the public `src.qual.commands` exports for the smoke-contract API and locks the MVP smoke argv for `project-open`, `retrieval`, `patch-review`, and `export-handoff`.

## Roadmap And Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 1, Bootstrap Flow Stabilization, specifically command and diff-preview behavior hardening and manual CLI smoke-flow stability.
- Roadmap item affected: `ROADMAP.md` Milestone 2, Test Hardening, specifically focused parser-edge and command-level probe coverage.
- Roadmap item affected: `ROADMAP.md` Milestone 3, Product Readiness, specifically locking user-facing output/command contracts and CLI compatibility.
- MVP focus alignment: `feat-commands` is listed under the active MVP implementation emphasis. This does not start `feat-console`.
- Vision capability affected: `PRODUCT_VISION.md` capability 4, Operator-first control surface. The CLI remains a first-class, reliable fallback surface.
- Vision capability affected: `PRODUCT_VISION.md` capability 5, Agent-to-UI protocol (`A2UI`), by preserving CLI fallback compatibility for structured output/client work.
- Routing/provider impact: none. This handoff does not change model routing, provider configuration, endpoint policy, provider fallback behavior, or provider compatibility probing.
- Proposed `README.md` patch text: none.

## Risks And Blockers

- Risk level: high due to `src/qual/cli.py` shared/integrator-locked parser entrypoint changes and over-budget actual range size.
- Remaining risk: the actual review range is larger than the high-risk net LOC limit and needs reviewer/integrator acceptance as an over-budget resubmission or follow-up split decision.
- Blockers: none known for local validation; approval depends on reviewer/integrator acceptance of the disclosed high-risk scope.

## Commands Run

Required gates rerun for this branch-tip fixer pass:

- `make scope-check` - failed on disclosed shared/integrator-locked `src/qual/cli.py`; this is expected for the actual branch-tip range without the documented shared-file approval flag.
- `SCOPE_ALLOW_SHARED=1 make scope-check` - passed.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed, `187` tests.
- `./typecheck-test.sh` - passed, Python sources compiled.
- `make ci` - failed on strict scope-check for disclosed shared/integrator-locked `src/qual/cli.py`; this is expected without the documented shared-file approval flag.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed, including scope-check, format, lint, typecheck, and `187` tests.

Focused coverage also run previously in this branch:

- `python3 -m unittest tests.unit.test_commands_catalog -v` - passed, `105` tests.
- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_mutated_real_argparse_choices tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_actual_add_parser_token_drift tests.unit.test_commands_catalog.CommandCatalogTests.test_actual_argparse_surface_matches_the_command_contract -v` - passed, `3` tests.
- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_actual_add_parser_token_drift tests.unit.test_commands_catalog.CommandCatalogTests.test_actual_argparse_surface_matches_the_command_contract tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_matches_the_catalog_order -v` - passed, `3` tests.
- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_actual_add_parser_token_drift tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_real_argparse_choice_drift tests.unit.test_commands_catalog.CommandCatalogTests.test_actual_argparse_surface_matches_the_command_contract -v` - passed, `3` tests.

## Handoff Readiness Checklist

- Branch name: `codex/feat-commands`
- Tasks completed: listed in Scope Completed
- Files changed: listed above
- Commands run and outcomes: required gates passed with `SCOPE_ALLOW_SHARED=1` for scope-gated commands; bare `make scope-check` and `make ci` fail on the disclosed `src/qual/cli.py` shared/integrator-locked edit.
- Risks/blockers: listed above
- Required `INTEGRATION.md` fields: present
