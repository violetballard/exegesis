# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: actual branch tip after this fixer commit
- Review basis: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`
- Review range command: `git diff f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`
- Fixer scope: satisfy fixer prompt `20260429T104143Z` by making `command_cli_contract()` consume the live argparse parser surface explicitly, preserving regression coverage for real parser token drift, naming the canonical demo-path steps advanced, and clarifying ownership for the current fixer slice versus the broader branch-tip range.

## Traceability Correction

This packet intentionally uses the reviewer-observed actual branch range, `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`. The previous handoff was not traceable because it described a narrower command-catalog slice while the branch tip included additional code, test, and handoff commits.

Commit `f8cfa2337f661b52511ab8dde84d9d7d72288738` is not metadata-only. It changes `tests/unit/test_commands_catalog.py` as well as `THREAD.md` and `THREAD_PACKET.md`, so it remains part of the review range as test work.

Commit `50921ba10fee9d5d3a8ef3c7ed34f02e0c710f5d` is also not metadata-only. It changes `src/qual/commands/catalog.py` by adding runtime validation that the MVP smoke argv token for each `CommandSmokeStep` starts with the smoke step's command. This runtime command-catalog validation is included in the reviewed implementation scope.

The review target is the actual `codex/feat-commands` branch tip after this fixer commit, not `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and not `f8cfa2337f661b52511ab8dde84d9d7d72288738`.

## Scope Completed

1. Bound the real argparse top-level command surface in `src/qual/cli.py` to `command_cli_lookup_table()` and exposed raw `command_parser_tokens()`, so accepted parser tokens consume and report the same source as the command catalog.
   Canonical demo-path steps advanced: `open project/document` through `bootstrap`; `retrieve material` through `context-basket`; `preview/apply/reject patch` through `diff-preview` and `diff`; `continue working` through `terminal`.
2. Added live parser-surface parity checks to `command_cli_contract()` that explicitly capture the real `src.qual.cli._build_parser()` path through `command_parser_tokens()` and `command_parser_lookup_table()`, then compare raw argparse choices, canonical parser projection, catalog CLI tokens, and the lookup table. Same-canonical parser-token drift is rejected even when the canonical command names still match. This fixer pass also makes the validator inputs easy to audit at the `command_cli_contract()` call site.
   Canonical demo-path steps advanced: `open project/document`, `retrieve material`, `preview/apply/reject patch`, and `continue working`, by preventing the CLI fallback command names for those steps from drifting away from the catalog.
3. Added and exported the MVP smoke-contract API: `CommandSmokeStep`, `CommandSmokeContract`, `command_mvp_smoke_contract()`, `command_mvp_smoke_commands()`, `command_mvp_smoke_argv()`, and `command_mvp_smoke_lookup_table()` in `src/qual/commands/catalog.py` and `src/qual/commands/__init__.py`.
   This includes the `50921ba10fee9d5d3a8ef3c7ed34f02e0c710f5d` runtime validation change in `src/qual/commands/catalog.py`, which rejects smoke steps whose argv no longer begins with the declared command.
   Canonical demo-path steps advanced: `open project/document` via `bootstrap`; `retrieve material` via `context-basket list`; `preview/apply/reject patch` via `diff-preview`; `continue working` via `terminal`.
4. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for parser-surface drift and smoke-contract public exports, including tests that mutate a real argparse parser's top-level `choices`, patch `_build_parser()` choices, and intercept `argparse._SubParsersAction.add_parser()` to rewrite the top-level `diff-preview` parser token.
   Canonical demo-path steps advanced: all command-backed fallback steps above, by proving the parser/catalog contract rejects live argparse token drift before integration.

## High-Risk Budget And Size Accounting

This is a high-risk handoff because it changes command surface validation and includes `src/qual/cli.py`, which `THREAD_OWNERSHIP.md` marks as both shared-by-approval for `feat-commands` and integrator-locked.

- Task budget: `4` completed tasks of `4` high-risk tasks allowed.
- Time budget: original high-risk target `30m`; this fixer pass is documentation and gate-rerun work.
- High-risk file budget: `6` files changed in the actual review range, within the `<=8` high-risk file limit.
- High-risk net LOC budget: exceeded in the actual review range. Current branch-tip accounting for `f8d860ed9..HEAD` including this fixer packet refresh is `2068 insertions(+), 109 deletions(-)`. This is explicitly disclosed for reviewer/integrator handling instead of being presented as a narrow catalog-only slice.
- Current `git diff --stat f8d860ed9..HEAD` evidence including this fixer packet refresh:
  - `THREAD.md`: `18` lines changed
  - `THREAD_PACKET.md`: `174` lines changed
  - `src/qual/cli.py`: `118` lines changed
  - `src/qual/commands/__init__.py`: `12` lines changed
  - `src/qual/commands/catalog.py`: `333` lines changed
  - `tests/unit/test_commands_catalog.py`: `1522` lines changed
  - Total: `6 files changed, 2068 insertions(+), 109 deletions(-)`
- Current `git diff --numstat f8d860ed9..HEAD` evidence including this fixer packet refresh:
  - `THREAD.md`: `16` insertions, `2` deletions
  - `THREAD_PACKET.md`: `118` insertions, `56` deletions
  - `src/qual/cli.py`: `84` insertions, `34` deletions
  - `src/qual/commands/__init__.py`: `12` insertions, `0` deletions
  - `src/qual/commands/catalog.py`: `317` insertions, `16` deletions
  - `tests/unit/test_commands_catalog.py`: `1521` insertions, `1` deletion
- Size-budget disposition: this handoff is not within the high-risk net LOC budget. Re-review must either explicitly accept the over-budget branch-tip range as an exception or send the lane back for an integrator-directed split; this packet does not claim pre-existing acceptance.
- Current fixer-slice ownership: `src/qual/commands/catalog.py` is lane-owned command contract code; `THREAD.md` and `THREAD_PACKET.md` are handoff metadata. This fixer slice does not add a new integrator-locked implementation edit.
- Branch-tip shared-by-approval file already in the wider review range: `src/qual/cli.py`.
- Branch-tip integrator-locked file already in the wider review range: `src/qual/cli.py`.
- Approval basis for the existing `src/qual/cli.py` branch-tip edit: reviewer-required parser-surface traceability for the real CLI parser entrypoint; no routing/provider/config behavior is changed.
- Shared/integrator-locked disposition requested for the wider branch-tip range: approve the existing `src/qual/cli.py` exception because live argparse validation is required for the numbered reviewer fix. If that exception is not accepted, the required disposition is an integrator-directed split rather than promotion of this range.
- Expected strict scope-check behavior: the required bare `make scope-check` gate must pass on this branch tip; if integrator reruns with stricter shared-file policy, `src/qual/cli.py` is the disclosed shared/integrator-locked exception and `SCOPE_ALLOW_SHARED=1 make scope-check` is the documented approval mode from `THREAD_OWNERSHIP.md`.

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
- Current `20260429T104143Z` fixer slice: `src/qual/commands/catalog.py` lane-owned; `THREAD.md` and `THREAD_PACKET.md` handoff metadata; no new shared or integrator-locked implementation file in this fixer commit.

## Regression Coverage

- `test_actual_argparse_surface_matches_the_command_contract` verifies the live argparse parser surface matches the command catalog.
- `test_actual_argparse_surface_rebuilds_from_catalog_tokens` points at the real argparse construction path by patching catalog tokens and proving `src.qual.cli._build_parser()` rebuilds top-level parser choices from the catalog lookup table.
- `test_command_cli_contract_rejects_actual_parser_surface_mismatch`, `test_command_cli_contract_rejects_real_argparse_choice_drift`, `test_command_cli_contract_rejects_mutated_real_argparse_choices`, and `test_command_cli_contract_rejects_actual_add_parser_token_drift` verify same-canonical parser drift, removed tokens, substituted tokens, added aliases, reordered parser choices, direct mutation of the actual argparse choices map, and a real top-level `add_parser()` token rewrite are rejected.
- `test_public_mvp_smoke_exports_track_the_demo_path` verifies the public `src.qual.commands` exports for the smoke-contract API and locks the MVP smoke argv for `project-open`, `retrieval`, `patch-review`, and `export-handoff`.

## Roadmap And Vision Mapping

- Roadmap item affected: current Milestone 3, Real workflow loop, specifically the command-backed MVP loop from project bootstrap/open through context retrieval, diff preview, terminal continuation, and handoff/export fallback.
- Active MVP note alignment: `AGENTS.md` says current MVP work should target Engine stability, FTS-first retrieval, and A2UI contracts with CLI fallback. This handoff affects Engine command stability and CLI fallback contracts only; it does not start `feat-console`.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling. The command smoke surface keeps retrieval-context commands stable for the FTS-first MVP path.
- Vision capability affected: `PRODUCT_VISION.md` capability 4, Operator-first control surface. The CLI remains a first-class, reliable fallback surface for development, recovery, and repeatable workflow execution.
- Vision capability affected: `PRODUCT_VISION.md` capability 5, Agent-to-UI protocol (`A2UI`). The CLI fallback remains aligned with structured output/client work without adding a console implementation.
- Routing/provider impact: none. This handoff does not change model routing, provider configuration, endpoint policy, provider fallback behavior, or provider compatibility probing.
- Proposed `README.md` patch text: none.

## Risks And Blockers

- Risk level: high due to `src/qual/cli.py` shared/integrator-locked parser entrypoint changes and over-budget actual range size.
- Remaining risk: the actual review range is larger than the high-risk net LOC limit and includes the disclosed shared/integrator-locked `src/qual/cli.py` edit. This handoff requires explicit reviewer/integrator acceptance as an over-budget branch-tip range with a CLI-file exception, or an integrator-directed split before promotion.
- Blockers: none known for local validation; approval depends on reviewer/integrator acceptance of the disclosed high-risk scope.

## Commands Run

Required gates rerun for this branch-tip fixer pass:

- `make scope-check` - passed for branch `codex/feat-commands`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed, `187` tests.
- `./typecheck-test.sh` - passed, Python sources compiled.
- `make ci` - passed, including scope-check, format, lint, typecheck, and `187` tests.

Focused coverage also run previously in this branch:

- `python3 -m unittest tests.unit.test_commands_catalog -v` - passed, `105` tests.
- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_mutated_real_argparse_choices tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_actual_add_parser_token_drift tests.unit.test_commands_catalog.CommandCatalogTests.test_actual_argparse_surface_matches_the_command_contract -v` - passed, `3` tests.
- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_actual_add_parser_token_drift tests.unit.test_commands_catalog.CommandCatalogTests.test_actual_argparse_surface_matches_the_command_contract tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_matches_the_catalog_order -v` - passed, `3` tests.
- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_actual_add_parser_token_drift tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_real_argparse_choice_drift tests.unit.test_commands_catalog.CommandCatalogTests.test_actual_argparse_surface_matches_the_command_contract -v` - passed, `3` tests.

## Handoff Readiness Checklist

- Branch name: `codex/feat-commands`
- Tasks completed: listed in Scope Completed
- Files changed: listed above
- Commands run and outcomes: required gates passed bare on the current branch tip, including `make scope-check` and `make ci`.
- Risks/blockers: listed above
- Required `INTEGRATION.md` fields: present
