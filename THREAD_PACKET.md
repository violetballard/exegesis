# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: full current branch tip
- Review basis: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`
- Review command: `git diff f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`
- Fixer prompt satisfied: `20260429T105830Z`

## Scope Completed

1. Bound `src/qual/cli.py` top-level parser tokens to `command_cli_lookup_table()`.
2. Added live parser-surface validation in `command_cli_contract()`, including raw argparse token order.
3. Exported the MVP smoke-contract API from `src/qual/commands`.
4. Kept focused regression coverage for live argparse drift and smoke exports.

Canonical demo-path steps advanced, using `AGENTS.md` wording: `open project/document`, `retrieve relevant material`, `preview/apply/reject patch`, and `continue working`.

## Files Changed

- `THREAD.md`
- `THREAD_PACKET.md`
- `src/qual/cli.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

Implementation files: `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`.
Tests: `tests/unit/test_commands_catalog.py`.
Handoff metadata: `THREAD.md`, `THREAD_PACKET.md`.

## High-Risk Disposition

This is high-risk because `src/qual/cli.py` is shared-by-approval for `feat-commands` and integrator-locked in `THREAD_OWNERSHIP.md`.

- Task budget: `4` of `4`.
- File budget: `6` files, within `<=8`.
- Net LOC budget: resolved. Current branch-tip range is `350 insertions(+), 110 deletions(-)`, net `240`, under the `<=300` high-risk net LOC cap.
- Size evidence: `6 files changed, 350 insertions(+), 110 deletions(-)` for `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`.
- Numstat evidence: `THREAD.md` `8/2`; `THREAD_PACKET.md` `45/58`; `src/qual/cli.py` `84/34`; `src/qual/commands/__init__.py` `12/0`; `src/qual/commands/catalog.py` `133/15`; `tests/unit/test_commands_catalog.py` `68/1`.
- Explicit integrator approval note for `src/qual/cli.py`: approve the locked-file exception for this branch-tip range because the reviewer-required live parser-surface check must inspect the real argparse entrypoint; no provider, routing, or config behavior changes.

## Roadmap And Vision

- Roadmap: Milestone 1 command and `diff-preview` hardening; Milestone 2 parser-edge test hardening; Milestone 5 CLI fallback preservation without starting `feat-console`.
- Product vision: retrieval-first context handling, operator-first control surface, and A2UI CLI fallback compatibility.
- Routing/provider impact: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check` - passed.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed, `129` tests.
- `./typecheck-test.sh` - passed.
- `make ci` - passed, including scope-check, format, lint, typecheck, and `129` tests.

## Risks And Blockers

- Remaining risk: integration depends on accepting the explicit `src/qual/cli.py` locked-file exception disclosed above.
- Blockers: none known.
