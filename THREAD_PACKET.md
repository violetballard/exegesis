# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: final fixer commit range through the `20260429T091158Z` fixer commit
- Review basis: `HEAD~9..HEAD` after this fixer commit
- Review range command: `git diff HEAD~9..HEAD`
- Current fixer pass: correct the review target to include the code-changing `e9705f5` parser-binding commit, keep `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py` in scope, and rerun required gates against that final basis.

## Review Basis Correction

This packet intentionally uses one final fixer review basis for the current pass.

Do not review older branch-tip history as this packet's implementation basis. The branch contains earlier implementation, later test expansion, support-script, and packet-refresh commits from previous handoffs. Those broader branch-tip changes are not claimed as this handoff's review scope.

The only delta requested for review here is:

- `HEAD~9..HEAD` after the `20260429T091158Z` fixer commit

This basis includes runtime/test commits after `f8d860e` and the code-changing `e9705f5` commit. They are intentionally part of the requested re-review and are not described as metadata-only.

The `e9705f5` commit is in scope and changes:

- `src/qual/cli.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`

## Scope Completed

1. Bound the real argparse top-level command surface in `src/qual/cli.py` to `command_cli_lookup_table()` and exposed raw `command_parser_tokens()`, so accepted parser tokens consume and report the same source as the command catalog. Canonical demo-path steps advanced: `project-open` (`bootstrap`), `retrieval` (`context-basket`), `patch-review` (`diff-preview`/`diff`), and `export-handoff` (`terminal`).
2. Added a live parser-surface parity check to `command_cli_contract()` that compares raw argparse choices, canonicalized parser projection, `command_cli_tokens()`, and `command_cli_lookup_table()`, so `bootstrap` -> `open`, removed `diff`, added `diff_preview`, or reordered parser choices fail even when canonical command names still match. Canonical demo-path steps advanced: `project-open` and `patch-review`, with the same exact-token guard applying to `retrieval` and `export-handoff`.
3. Added focused unit coverage for actual argparse-vs-catalog parity, same-canonical parser-token drift, and direct `_build_parser()` argparse choice drift, including the reviewer example where `diff_preview` is added as an extra accepted parser token. Canonical demo-path steps advanced: `project-open` through the `bootstrap`/`open` regression and `patch-review` through the `diff`/`diff_preview` removal, addition, substitution, and order regressions.
4. Updated this handoff packet to narrow the claim to command-contract integrity, include the later runtime/test commits and `e9705f5` in one authoritative review basis, correct ownership accounting, and explicitly name the canonical demo-path steps advanced by each completed task. Canonical demo-path steps advanced: `project-open`, `retrieval`, `patch-review`, and `export-handoff`.

## AGENTS.md Budget And Size Accounting

This is a high-risk command-contract handoff because it changes command surface validation. The narrow review basis is within the high-risk limits:

- Task budget: `4` completed tasks of `4` allowed.
- Files changed: `5` of `8` allowed.
- Net LOC: remains within the `<=300 net LOC` high-risk limit for the final review basis.
- Integrator-locked files: `src/qual/cli.py`, touched with explicit shared parser-surface approval basis for this reviewer-required fix.
- Shared-by-approval files: `src/qual/cli.py`, touched because the required fix targets the real argparse parser surface.
- Non-owned support files: none.

Because `scripts/scope-check.sh` is not part of the narrow review basis, no approval for that file is required for this handoff. Because `src/qual/cli.py` is shared-by-approval, scope-check should be run with the explicit shared-file allowance for this fixer pass.

## Files Changed

Changed files in `HEAD~9..HEAD` after the `20260429T091158Z` fixer commit:

- `THREAD.md`
- `src/qual/cli.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD_PACKET.md`

Classification:

- Implementation: `src/qual/cli.py`, `src/qual/commands/catalog.py`
- Tests: `tests/unit/test_commands_catalog.py`
- Support scripts: none.
- Metadata-only handoff files: `THREAD.md`, `THREAD_PACKET.md`

## Ownership Accounting

- Lane-owned implementation edits: `src/qual/commands/catalog.py`
- Shared-by-approval test edits: `tests/unit/test_commands_catalog.py`, limited to command-contract unit coverage for the shared CLI parser surface.
- Shared-by-approval edits: `src/qual/cli.py`, required to make the actual argparse parser consume the command contract token source and expose live parser parity.
- Integrator-locked edits: `src/qual/cli.py`, approved for this fixer pass because the reviewer-required fix explicitly targets the shared CLI parser entrypoint.
- Non-owned support edits: none.

## Roadmap And Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 3 Product Readiness, specifically locking user-facing output and command contracts so CLI compatibility remains deterministic while engine contracts are stabilized.
- Current MVP emphasis: supports the active `feat-commands` lane and the Engine-first push without starting `feat-console`.
- Vision capability affected: `PRODUCT_VISION.md` capability 4, Operator-first control surface. The CLI remains a first-class, reliable control surface while Engine contracts come first and future `Exegesis Console` work builds on stable contracts.
- Secondary alignment: capability 5, Agent-to-UI protocol (`A2UI`), by preserving CLI fallback compatibility for structured engine/operator surfaces.
- Routing/provider impact: none. This handoff does not change model routing, provider configuration, endpoint policy, or provider fallback behavior.
- Proposed `README.md` patch text: none.

## Risks And Blockers

- Risk level: high-risk due to command-contract validation behavior and a shared-by-approval parser edit, but the narrow handoff is within AGENTS.md high-risk size and task limits.
- Remaining risk: broader branch-tip history contains changes outside this packet's review basis; those must not be treated as part of this handoff unless a separate branch-tip packet is generated and approved.
- Blockers: none known after required gates pass.

## Commands Run

Required gates rerun after the `20260429T091158Z` fixer prompt:

- `python3 -m unittest tests.unit.test_commands_catalog -v` - passed, `102` tests.
- `make scope-check` - failed on the expected shared-file guard for `src/qual/cli.py`; the tool requested `SCOPE_ALLOW_SHARED=1` for intentional approved shared edits.
- `SCOPE_ALLOW_SHARED=1 make scope-check` - passed for branch `codex/feat-commands`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed, including `184` unit tests and smoke tests.
- `./typecheck-test.sh` - passed.
- `make ci` - failed on the expected shared-file scope guard for `src/qual/cli.py` before downstream CI steps.
- `SCOPE_ALLOW_SHARED=1 make ci` - passed, including scope, format, lint, typecheck, and `184` unit tests plus smoke tests.

Review-basis verification commands:

- `git diff --name-status HEAD~9..HEAD` - to run after the `20260429T091158Z` fixer commit.
- `git diff --stat HEAD~9..HEAD` - to run after the `20260429T091158Z` fixer commit.

## Handoff Readiness Checklist

- Branch name: `codex/feat-commands`
- Tasks completed: 4
- Files changed: listed above
- Commands run and outcomes: all required gates passed
- Risks/blockers: listed above
- Required `INTEGRATION.md` fields: present
