# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: final fixer commit from this pass
- Review basis: `HEAD^..HEAD`
- Review range command: `git diff HEAD^..HEAD`
- Current fixer pass: close the parser-token drift gap by binding the real argparse surface to the command catalog contract and documenting the canonical demo-path step advanced by each task.

## Review Basis Correction

This packet intentionally uses the narrow commit-only review basis permitted by the review request.

Do not review older branch-tip history as this packet's implementation basis. The branch contains earlier implementation, later test expansion, support-script, and packet-refresh commits from previous handoffs. Those broader branch-tip changes are not claimed as this handoff's review scope.

The only implementation delta requested for review here is:

- `HEAD^..HEAD`

## Scope Completed

1. Bound the real argparse top-level command surface in `src/qual/cli.py` to `command_cli_lookup_table()`, so accepted parser tokens consume the same source as the command catalog. Canonical demo-path steps advanced: `project-open` (`bootstrap`), `retrieval` (`context-basket`), `patch-review` (`diff-preview`/`diff`), and `export-handoff` (`terminal`).
2. Added a live parser-surface parity check to `command_cli_contract()`, so `bootstrap` -> `open`, removed `diff`, added `diff_preview`, or reordered parser choices fail even when canonical command names still match. Canonical demo-path steps advanced: `project-open` and `patch-review`, with the same exact-token guard applying to `retrieval` and `export-handoff`.
3. Added focused unit coverage for actual argparse-vs-catalog parity and same-canonical parser-token drift. Canonical demo-path steps advanced: `project-open` through the `bootstrap`/`open` regression and `patch-review` through the `diff`/`diff_preview` removal, substitution, and order regressions.
4. Updated this handoff packet to narrow the claim to command-contract integrity and explicitly name the canonical demo-path steps advanced by each completed task.

## AGENTS.md Budget And Size Accounting

This is a high-risk command-contract handoff because it changes command surface validation. The narrow review basis is within the high-risk limits:

- Task budget: `4` completed tasks of `4` allowed.
- Files changed: `4` of `8` allowed.
- Net LOC: `189 insertions(+), 62 deletions(-)`, net `+127`, within the `<=300 net LOC` limit.
- Integrator-locked files: none.
- Shared-by-approval files: `src/qual/cli.py`, touched because the required fix targets the real argparse parser surface.
- Non-owned support files: none.

Because `scripts/scope-check.sh` is not part of the narrow review basis, no approval for that file is required for this handoff. Because `src/qual/cli.py` is shared-by-approval, scope-check should be run with the explicit shared-file allowance for this fixer pass.

## Files Changed

Changed files in `HEAD^..HEAD`:

- `src/qual/cli.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD_PACKET.md`

Classification:

- Implementation: `src/qual/cli.py`, `src/qual/commands/catalog.py`
- Tests: `tests/unit/test_commands_catalog.py`
- Support scripts: none.
- Metadata-only handoff files: `THREAD_PACKET.md`

## Ownership Accounting

- Lane-owned implementation edits: `src/qual/commands/catalog.py`
- Approved shared-test edits: none required; command catalog tests are the lane's direct unit coverage for the command contract.
- Shared-by-approval edits: `src/qual/cli.py`, required to make the actual argparse parser consume the command contract token source and expose live parser parity.
- Integrator-locked edits: none.
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

Required gates rerun after this fixer pass:

- `python3 -m unittest tests.unit.test_commands_catalog -v` - passed.
- `SCOPE_ALLOW_SHARED=1 SCOPE_INCLUDE_WORKTREE=1 make scope-check` - passed.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed.
- `./typecheck-test.sh` - passed.
- `SCOPE_ALLOW_SHARED=1 make ci` - pending final run.

Review-basis verification commands:

- `git diff --name-status HEAD^..HEAD` - run after final commit.
- `git diff --stat HEAD^..HEAD` - run after final commit.

## Handoff Readiness Checklist

- Branch name: `codex/feat-commands`
- Tasks completed: 3
- Files changed: listed above
- Commands run and outcomes: all required gates passed
- Risks/blockers: listed above
- Required `INTEGRATION.md` fields: present
