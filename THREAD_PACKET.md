# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: narrow implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Review basis: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3^..f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Review range command: `git diff 06bf38928dc337748b3616e2cdacfc0c3246edab..f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Current fixer pass: regenerate the handoff against one clear narrow review basis and exclude broader branch-tip packet-refresh work from this review.

## Review Basis Correction

This packet intentionally uses the narrow commit-only review basis permitted by the review request.

Do not review `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27..HEAD` as this packet's implementation basis. The branch tip contains earlier implementation, later test expansion, support-script, and packet-refresh commits from previous handoffs. Those broader branch-tip changes are not claimed as this handoff's review scope.

The only implementation delta requested for review here is:

- `f8d860ed9f6299f0169c4f21321ac5f37c949fd3^..f8d860ed9f6299f0169c4f21321ac5f37c949fd3`

## Scope Completed

1. Locked the command CLI contract to the canonical catalog order, so same-canonical or missing-canonical parser drift cannot pass through `command_cli_contract()` silently.
2. Added focused unit coverage proving the CLI contract exposes parser tokens, canonical command names, and lookup table data consistently.
3. Added a regression test for catalog drift by patching `command_names()` and asserting the contract raises `ValueError`.

## AGENTS.md Budget And Size Accounting

This is a high-risk command-contract handoff because it changes command surface validation. The narrow review basis is within the high-risk limits:

- Task budget: `3` completed tasks of `4` allowed.
- Files changed: `2` of `8` allowed.
- Net LOC: `19 insertions(+), 3 deletions(-)`, within the `<=300 net LOC` limit.
- Integrator-locked files: none.
- Shared-by-approval files: none.
- Non-owned support files: none.

Because `scripts/scope-check.sh` is not part of the narrow review basis, no approval for that file is required for this handoff.

## Files Changed

Changed files in `f8d860ed9f6299f0169c4f21321ac5f37c949fd3^..f8d860ed9f6299f0169c4f21321ac5f37c949fd3`:

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

Classification:

- Implementation: `src/qual/commands/catalog.py`
- Tests: `tests/unit/test_commands_catalog.py`
- Support scripts: none.
- Metadata-only handoff files: none in the review basis.

## Ownership Accounting

- Lane-owned implementation edits: `src/qual/commands/catalog.py`
- Approved shared-test edits: none required; command catalog tests are the lane's direct unit coverage for the command contract.
- Shared-by-approval edits: none.
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

- Risk level: high-risk due to command-contract validation behavior, but the narrow handoff is within AGENTS.md high-risk size and task limits.
- Remaining risk: broader branch-tip history contains changes outside this packet's review basis; those must not be treated as part of this handoff unless a separate branch-tip packet is generated and approved.
- Blockers: none known after required gates pass.

## Commands Run

Required gates rerun after this packet correction:

- `make scope-check` - passed.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed.
- `./typecheck-test.sh` - passed.
- `make ci` - passed.

Review-basis verification commands:

- `git diff --name-status f8d860ed9f6299f0169c4f21321ac5f37c949fd3^..f8d860ed9f6299f0169c4f21321ac5f37c949fd3` - shows only `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- `git diff --stat f8d860ed9f6299f0169c4f21321ac5f37c949fd3^..f8d860ed9f6299f0169c4f21321ac5f37c949fd3` - shows `2 files changed, 19 insertions(+), 3 deletions(-)`.

## Handoff Readiness Checklist

- Branch name: `codex/feat-commands`
- Tasks completed: 3
- Files changed: listed above
- Commands run and outcomes: all required gates passed
- Risks/blockers: listed above
- Required `INTEGRATION.md` fields: present
