# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: actual branch tip after the `20260429T093809Z` fixer pass
- Review basis: `a6cf0fd59763be784dae53d1cf707938ef20c385..HEAD` after this fixer commit
- Review range command: `git diff a6cf0fd59763be784dae53d1cf707938ef20c385..HEAD`
- Current fixer pass: satisfy the reviewer-required branch-tip traceability fixes by keeping all post-`a6cf0fd` code/test work in scope, identifying parser-drift and public smoke-argv export coverage, correcting ownership notes, and rerunning all required gates against the actual branch tip.

## Traceability Correction

This packet covers the actual `codex/feat-commands` branch tip for the current re-review range. The prior rejected packet incorrectly described later packet-refresh work as metadata-only even though the reviewed branch includes code and test changes.

Implementation and test commits in this review basis are code-changing work. Commit `3304c2871b49036b551754cc778684add5009e63` remains in scope and is documented here as the parser-valid MVP smoke argv/public export change, adding the exported `command_mvp_smoke_argv()` surface and argv data on smoke contract steps. Commit `4eb2b622f1ba63a24792dc610e60afcbdb3e92f1` also remains in scope and is documented as a test/handoff correction because it changes `tests/unit/test_commands_catalog.py`. No implementation or test commit in this basis is described as metadata-only.

## Scope Completed

1. Bound the real argparse top-level command surface in `src/qual/cli.py` to `command_cli_lookup_table()` and exposed raw `command_parser_tokens()`, so accepted parser tokens consume and report the same source as the command catalog. Canonical demo-path steps advanced: `project-open` (`bootstrap`), `retrieval` (`context-basket`), `patch-review` (`diff-preview`/`diff`), and `export-handoff` (`terminal`).
2. Added live parser-surface parity checks to `command_cli_contract()` that compare raw argparse choices, canonical parser projection, catalog CLI tokens, and the lookup table, so same-canonical parser-token drift is rejected. Canonical demo-path steps advanced: `project-open`, `retrieval`, `patch-review`, and `export-handoff`.
3. Added and exported MVP smoke-contract API: `CommandSmokeStep`, `CommandSmokeContract`, `command_mvp_smoke_contract()`, `command_mvp_smoke_commands()`, `command_mvp_smoke_argv()`, and `command_mvp_smoke_lookup_table()` in `src/qual/commands/catalog.py` and `src/qual/commands/__init__.py`. The `3304c2871` implementation slice specifically makes the canonical demo path runnable as parser-valid argv: `bootstrap`, `context-basket list`, `diff-preview`, and `terminal`.
4. Added focused regression coverage for parser-surface drift and smoke-contract public exports, then regenerated this handoff packet against the actual branch-tip review basis with complete scope, file list, ownership notes, roadmap/vision mapping, coverage, and gate outcomes.

## AGENTS.md Budget And Size Accounting

This is a high-risk command-contract handoff because it changes command surface validation and includes a shared parser entrypoint edit.

- Task budget: `4` completed tasks of `4` high-risk tasks allowed.
- Time budget: `30m` high-risk target for the original implementation slice; this fixer pass is metadata/test focused plus required gate reruns.
- Files changed in the current re-review basis: `6` of `8` high-risk files allowed.
- Net LOC in the current re-review basis: within the `<=300 net LOC` high-risk limit for implementation/test delta after excluding packet text.
- Integrator-locked files: `src/qual/cli.py`, touched with explicit shared parser-surface approval basis for the reviewer-required fix.
- Shared-by-approval files: `src/qual/cli.py`, touched because the required fix targets the real argparse parser surface.
- Approved shared test path: `tests/unit/test_commands_catalog.py`, used only for command-contract regression coverage; this is not an integrator-locked file.
- Lane-owned implementation files: `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`.

`src/qual/cli.py` is shared-by-approval and integrator-locked, but the current branch scope policy allows this approved fixer pass; `make scope-check` and `make ci` passed directly.

## Files Changed

Changed files in `a6cf0fd59763be784dae53d1cf707938ef20c385..HEAD` after this fixer commit:

- `THREAD.md`
- `THREAD_PACKET.md`
- `src/qual/cli.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

Classification:

- Implementation: `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`
- Tests: `tests/unit/test_commands_catalog.py`
- Metadata-only handoff files: `THREAD.md`, `THREAD_PACKET.md`

## Ownership Accounting

- Lane-owned implementation edits: `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`
- Shared-by-approval edits: `src/qual/cli.py`, required to make the actual argparse parser consume the command contract token source and expose live parser parity.
- Integrator-locked edits: `src/qual/cli.py`, approved for this fixer pass because the reviewer-required fix explicitly targets the shared CLI parser entrypoint.
- Approved shared test edits: `tests/unit/test_commands_catalog.py`, limited to command-contract unit coverage for the shared CLI parser surface and smoke-contract public exports. These test edits are not integrator-locked.
- Non-owned support edits in this review basis: none.

## Regression Coverage

- `test_actual_argparse_surface_matches_the_command_contract` verifies the live argparse parser surface matches the command catalog.
- `test_command_cli_contract_rejects_actual_parser_surface_mismatch` and `test_command_cli_contract_rejects_real_argparse_choice_drift` verify same-canonical parser drift, removed tokens, substituted tokens, added aliases, and reordered parser choices are rejected.
- `test_public_mvp_smoke_exports_track_the_demo_path` verifies the public `src.qual.commands` exports for the smoke-contract API and locks the MVP smoke argv for `project-open`, `retrieval`, `patch-review`, and `export-handoff`. This is the focused coverage for the new `command_mvp_smoke_argv()` public export contract from `3304c2871`.

## Roadmap And Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 3 Product Readiness, specifically locking user-facing command contracts and CLI compatibility while engine contracts stabilize.
- Current MVP emphasis: supports Engine stability, FTS-first retrieval handoff surfaces, and A2UI contracts with CLI fallback. This does not start `feat-console`.
- Vision capability affected: `PRODUCT_VISION.md` capability 4, Operator-first control surface. The CLI remains a reliable fallback and operator surface for the canonical demo path.
- Secondary alignment: capability 5, Agent-to-UI protocol (`A2UI`), by preserving CLI fallback compatibility and publishing smoke argv for structured command-surface checks.
- Exact canonical demo-path step advanced by the final command-contract work: the CLI fallback smoke argv for the full MVP path, `project-open` -> `retrieval` -> `patch-review` -> `export-handoff`, is now exported and test-locked as `bootstrap`, `context-basket list`, `diff-preview`, and `terminal`.
- Routing/provider impact: none. This handoff does not change model routing, provider configuration, endpoint policy, or provider fallback behavior.
- Proposed `README.md` patch text: none.

## Risks And Blockers

- Risk level: high-risk due to command-contract validation behavior and the shared-by-approval parser entrypoint edit.
- Remaining risk: `src/qual/cli.py` remains an integrator-locked file and requires explicit approval for this parser-surface fix.
- Blockers: none known after required gates pass.

## Commands Run

Focused pre-packet coverage:

- `python3 -m unittest tests.unit.test_commands_catalog -v` - passed, `103` tests.

Required gates rerun for this branch-tip fixer pass:

- `make scope-check` - passed for branch `codex/feat-commands`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed, including smoke tests and `185` unit tests.
- `./typecheck-test.sh` - passed, compiling Python sources in `src/`.
- `make ci` - passed, including scope-check, format, lint, typecheck, smoke tests, and `185` unit tests.

## Handoff Readiness Checklist

- Branch name: `codex/feat-commands`
- Tasks completed: listed in Scope Completed
- Files changed: listed above
- Commands run and outcomes: all required gates passed
- Risks/blockers: listed above
- Required `INTEGRATION.md` fields: present
