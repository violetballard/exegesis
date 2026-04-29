# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: current branch tip after fixer prompt `20260429T075238Z`
- Review basis: all branch-tip changes relative to merge base `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`
- Review range command: `git diff 06cdebc2d5d53533b73f264a4bbf5a4b4daacb27..HEAD`
- Current fixer pass: focused accepted parser-token regression coverage plus handoff correction in `THREAD.md` and `THREAD_PACKET.md`
- Prior implementation anchor referenced by earlier packets: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Important correction: `b9e1076e1fafac66a69b8916154db6e85c2bf7c4` is implementation/test-plus-metadata scope because it changes `src/qual/commands/catalog.py`, `tests/unit/test_commands_catalog.py`, `THREAD.md`, and `THREAD_PACKET.md`. It is not metadata-only.

## Scope Completed

1. Project open: hardened `command_cli_contract()` so the accepted `bootstrap` parser token cannot silently drift to a same-canonical alias such as `open`. Concrete blocker removed: the CLI could otherwise accept a different project/document open token while the catalog contract still passed.
2. Retrieval/basket: kept `context-basket` locked to the exact accepted parser-token surface and canonical order. Concrete blocker removed: retrieval context gathering could otherwise lose or reorder its parser token without an early catalog failure.
3. Patch review: added focused parser-drift regression coverage for same-canonical substitution, extra accepted alias, missing accepted alias, and token order drift across `diff-preview`/`diff`. Concrete blocker removed: preview/apply/reject patch review could otherwise drift within the same canonical command and evade the weaker catalog-name invariant.
4. Save/continue/export handoff: preserved the `terminal` CLI surface and command-lane compatibility helpers for export handoff routing while refreshing ownership accounting. Concrete blocker removed: the final operator handoff path now remains tied to the exact parser surface before `feat-console` starts.

## AGENTS.md Demo-Path Statement

This work makes the canonical CLI-first demo path more real for these steps:

1. Project open: `bootstrap` remains the accepted parser token for opening or bootstrapping a project/document path.
2. Retrieval/basket: `context-basket` remains the accepted parser token for gathering retrieved context into the working basket.
3. Patch review: `diff-preview` and `diff` remain the accepted parser tokens for previewing and reviewing patch output.
4. Export handoff: `terminal` remains the accepted parser token for persisting/exporting the operator handoff.

The concrete blocker removed is silent parser-token drift before Textual/`feat-console` is enabled. The CLI smoke path now fails loudly if the parser, command catalog, or compatibility lookup tables stop agreeing on those demo-path steps.

## Files Changed

Changed files against merge base `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`:

- `THREAD.md`
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

Size accounting against merge base after the final `20260429T075238Z` fixer pass:

- `9 files changed, 3968 insertions(+), 42 deletions(-)`

Implementation/test versus metadata classification:

- Implementation files: `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`
- Test files: `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`
- Scope-check support file: `scripts/scope-check.sh`
- Metadata-only handoff files: `THREAD.md`, `THREAD_PACKET.md`

## Ownership Accounting

- Lane-owned implementation edits: `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`
- Approved shared-test edits: `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`
- Other non-owned support file in branch diff: `scripts/scope-check.sh`
- Integrator-locked edits: none
- Metadata-only handoff edits: `THREAD.md`, `THREAD_PACKET.md`

Shared/approval note: the command tests are included as the approved shared-test coverage for this lane's command contract. `scripts/scope-check.sh` is not integrator-locked; it is listed separately so review can account for its branch-scope impact.

## Roadmap And Vision Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 1 command and diff-preview behavior hardening; Milestone 2 command-level probes for integration confidence; MVP active lane `feat-commands`.
- Vision capability affected: `PRODUCT_VISION.md` capability 4, Operator-first control surface. The CLI remains a first-class reliable operator surface while Engine contracts are stabilized before `Exegesis Console`.
- Routing/provider impact: none. This branch does not change model routing, provider configuration, endpoint policy, or provider fallback behavior.
- Proposed `README.md` patch text: none.

## Risks And Blockers

- Risk level: high-risk thread accounting because the work locks CLI parser and command-contract behavior and touches approved shared test files.
- Remaining risk: branch-size accounting exceeds the default AGENTS size guideline, so this packet calls out the full branch diff rather than narrowing review to only the later command-catalog slice.
- Blockers: none known after the required gates pass.

## Commands Run

- `make scope-check` - passed (`[devex] scope-check: passed for branch 'codex/feat-commands'`)
- `./quality-format.sh --check` - passed (`[format] check passed`)
- `./quality-lint.sh` - passed (`[lint] passed`)
- `python3 -m unittest tests.unit.test_commands_catalog -q` - passed (`Ran 98 tests ... OK`)
- `./quality-test.sh` - passed (`Ran 180 tests ... OK`; smoke passed)
- `./typecheck-test.sh` - passed (`[typecheck] compiling Python sources in src/`)
- `make ci` - passed (`[devex] CI entrypoint completed`)

## Handoff Readiness Checklist

- Branch name: `codex/feat-commands`
- Tasks completed: 4
- Files changed: listed above
- Commands run and outcomes: all required gates passed
- Risks/blockers: listed above
- Required `INTEGRATION.md` fields: present
