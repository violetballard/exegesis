# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: full current branch tip `HEAD`
- Review basis: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3^..HEAD`, including `f8d860ed9` and every later branch-tip implementation and handoff metadata commit.
- Review command: `git diff f8d860ed9f6299f0169c4f21321ac5f37c949fd3^..HEAD -- THREAD.md THREAD_PACKET.md src/qual/cli.py src/qual/commands/__init__.py src/qual/commands/catalog.py tests/unit/test_commands_catalog.py`
- Fixer prompt satisfied: `20260429T111645Z`

## Scope Completed

1. Bound `src/qual/cli.py` top-level parser tokens to `command_cli_lookup_table()`.
   Canonical demo-path step advanced: `open project/document`, because the bootstrap parser token remains catalog-owned.
2. Added exact live parser-surface validation in `command_cli_contract()`, including raw argparse token order, parser choice mutation, and same-canonical alias drift.
   Canonical demo-path step advanced: `continue working`, because the CLI fallback can resume through the same command surface without accepting stray aliases.
3. Exported the MVP smoke-contract API from `src/qual/commands`.
   Canonical demo-path step advanced: `retrieve relevant material`, because `context-basket` smoke argv keeps the retrieval/basket CLI path parser-ready.
4. Kept focused regression coverage for live argparse drift, same-canonical alias drift, and smoke exports.
   Canonical demo-path step advanced: `preview/apply/reject patch`, because `diff-preview` remains pinned to the reviewed parser token surface.

## Files Changed

- `THREAD.md`
- `THREAD_PACKET.md`
- `src/qual/cli.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

Implementation files in scope: `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`.
Tests in scope: `tests/unit/test_commands_catalog.py`.
Handoff metadata: `THREAD.md`, `THREAD_PACKET.md`.
Ownership accounting: lane-owned implementation under `src/qual/commands/**`; shared/integrator-locked implementation file `src/qual/cli.py` is included in this branch-tip review under the explicit approval note below; shared test `tests/unit/test_commands_catalog.py` is included as the focused regression surface for the command contract.

## High-Risk Disposition

This is high-risk because `src/qual/cli.py` is shared-by-approval for `feat-commands` and integrator-locked in `THREAD_OWNERSHIP.md`.

- Task budget: `4` of `4`.
- File budget: `6` files, within `<=8`.
- Net LOC budget: resolved. Current branch-tip review range is `382 insertions(+), 111 deletions(-)`, net `271`, under the `<=300` high-risk net LOC cap.
- Size evidence: `6 files changed, 382 insertions(+), 111 deletions(-)` for `f8d860ed9f6299f0169c4f21321ac5f37c949fd3^..HEAD`.
- Numstat evidence: `THREAD.md` `8/2`; `THREAD_PACKET.md` `51/59`; `src/qual/cli.py` `84/34`; `src/qual/commands/__init__.py` `12/0`; `src/qual/commands/catalog.py` `140/16`; `tests/unit/test_commands_catalog.py` `87/0`.
- Explicit integrator approval note for `src/qual/cli.py`: approve the locked-file exception for this branch-tip range because the reviewer-required live parser-surface check must inspect the real argparse entrypoint; no provider, routing, or config behavior changes.

## Roadmap And Vision

- Roadmap: Milestone 3 Product Readiness, specifically locking the user-facing CLI command output/input contract for engine-first CLI compatibility.
- Product vision: operator-first control surface and A2UI CLI fallback compatibility, with retrieval-first context handling preserved through the `context-basket` smoke command path.
- Routing/provider impact: none.
- Proposed `README.md` patch text: none.

## Commands Run

- `python -m unittest tests.unit.test_commands_catalog` - passed, `48` tests.
- `python -m pytest tests/unit/test_commands_catalog.py -q` - failed because `pytest` is not installed in the active Python.
- `make scope-check` - passed.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed, `130` tests.
- `./typecheck-test.sh` - passed.
- `make ci` - passed, including scope-check, format, lint, typecheck, and `130` tests.

## Risks And Blockers

- Remaining risk: integration depends on accepting the explicit `src/qual/cli.py` locked-file exception disclosed above.
- Blockers: none known.
