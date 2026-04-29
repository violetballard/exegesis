# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Implementation review target: branch tip after fixer prompt `20260429T042639Z`
- Current handoff refresh: reviewer fix after prompt `20260429T042639Z`
- Prior implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Scope: command-catalog contract hardening for the current engine-first MVP focus without starting `feat-console`.
- Roadmap alignment: Milestone 3 CLI compatibility for the engine-first workflow loop, and `feat-commands` as the command-surface compatibility lane.
- Vision alignment: canonical engine contract stability while the CLI remains the active operator surface.

## Reviewed Implementation Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Baseline Restoration

- `scripts/scope-check.sh` is restored to the submitted baseline and is not part of the branch-tip implementation diff.

## Metadata-Only Handoff Files

- `THREAD.md`
- `THREAD_PACKET.md`

## Branch-Tip Review Basis

- Review range: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`
- Matching changed-file scope:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`

## Ownership Accounting

- Lane-owned implementation edits: `src/qual/commands/catalog.py`.
- Shared-by-approval implementation/test edits: `tests/unit/test_commands_catalog.py` under the approved shared-test exception.
- Integrator-locked edits: none.
- Metadata-only handoff edits: `THREAD.md`, `THREAD_PACKET.md`.

## Fixer Prompt `20260429T035831Z` Fix Satisfaction

1. `command_cli_contract()` validates the exact accepted parser-token surface, grouped canonical surface, lookup table, and canonical command order.
2. Regression coverage includes removed tokens, added same-canonical aliases, replacement aliases, lookup-table substitutions, and declared-surface drift.
3. `THREAD_PACKET.md` is regenerated with explicit canonical demo-path mapping for each completed task.
4. The demo-path step made more real is stated explicitly in `THREAD_PACKET.md`.
5. Required gates are rerun and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T040101Z` Fix Satisfaction

1. `THREAD_PACKET.md` now puts the canonical demo-path step directly on every completed task line.
2. `THREAD_PACKET.md` now states the concrete blocker removed by this command-catalog work.
3. This refresh is metadata-only; implementation remains limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.

## Fixer Prompt `20260429T040347Z` Fix Satisfaction

1. `THREAD_PACKET.md` is refreshed against the actual branch-tip review target after prompt `20260429T040347Z`.
2. The packet lists all implementation, test, baseline-restoration, and metadata files changed since `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
3. The command-catalog implementation still validates exact parser tokens, lookup table, grouped canonical surface, declared surface, and canonical name order.
4. Regression coverage for removed tokens, added same-canonical aliases, replacement aliases, lookup substitutions, and declared-surface drift remains in `tests/unit/test_commands_catalog.py`.
5. Required gates are rerun and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T040701Z` Fix Satisfaction

1. The branch-tip review basis is refreshed again for the latest reviewer packet.
2. `THREAD.md` and `THREAD_PACKET.md` remain listed as metadata-only files.
3. Parser-surface validation still rejects extra known aliases, missing accepted aliases, substituted aliases, and ordering drift before returning `CommandCliContract`.
4. Regression coverage remains limited to the approved shared test file and covers the reviewer-requested drift classes.
5. Required gates are rerun and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T040923Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T040923Z`; review should use branch tip, not only `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
2. The existing implementation still validates exact parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. The existing test slice still covers added same-canonical aliases, removed tokens, replacement aliases, lookup-table substitutions that preserve the name set, and declared-surface drift.
4. The canonical demo-path mapping remains explicit in `THREAD_PACKET.md`, including the CLI-first blocker removed for project open, retrieval/basket, patch review, and export handoff.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T041242Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T041242Z`; review should use branch tip after this fixer commit.
2. The command-catalog implementation validates exact parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. Regression coverage now includes an explicitly named declared missing accepted-alias drift case in addition to extra aliases, removed tokens, substituted aliases, parser token ordering drift, lookup-table ordering drift, and declared-surface drift.
4. The canonical demo-path mapping remains explicit in `THREAD_PACKET.md`, including the CLI-first blocker removed for project open, retrieval/basket, patch review, and export handoff.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T041540Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T041540Z`; review should use branch tip after this fixer commit.
2. The branch-tip command-catalog implementation still validates exact parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. Regression coverage still includes extra same-canonical aliases, missing expected aliases, substituted aliases, parser token ordering drift, lookup-table substitutions that preserve the canonical-name set, lookup-table ordering drift, and declared-surface drift.
4. The canonical demo-path mapping remains explicit in `THREAD_PACKET.md`, including the concrete CLI-first blocker removed before Textual is enabled.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T041829Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T041829Z`; review should use branch tip after this fixer commit.
2. The branch-tip command-catalog implementation still validates exact parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. Regression coverage still includes extra same-canonical aliases, missing expected aliases, substituted aliases, parser token ordering drift, lookup-table substitutions that preserve the canonical-name set, lookup-table ordering drift, and declared-surface drift.
4. The canonical demo-path mapping remains explicit in `THREAD_PACKET.md`, including the concrete CLI-first blocker removed before Textual is enabled.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T042108Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T042108Z`; review should use branch tip after this fixer commit.
2. The branch-tip command-catalog implementation still validates exact parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. Regression coverage still includes extra same-canonical aliases, missing expected aliases, substituted aliases, parser token ordering drift, lookup-table substitutions that preserve the canonical-name set, lookup-table ordering drift, and declared-surface drift.
4. The canonical demo-path mapping remains explicit in `THREAD_PACKET.md`, including the concrete CLI-first blocker removed before Textual is enabled.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T042332Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T042332Z`; review should use branch tip after this fixer commit.
2. The branch-tip command-catalog implementation still validates exact parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. Regression coverage still includes extra same-canonical aliases, missing expected aliases, substituted aliases, parser token ordering drift, lookup-table substitutions that preserve the canonical-name set, lookup-table ordering drift, and declared-surface drift.
4. The canonical demo-path mapping remains explicit in `THREAD_PACKET.md`, including the concrete CLI-first blocker removed before Textual is enabled.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T042639Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T042639Z`; review should use branch tip after this fixer commit.
2. The branch-tip command-catalog implementation still validates exact parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. Regression coverage still includes extra same-canonical aliases, missing expected aliases, substituted aliases, parser token ordering drift, lookup-table substitutions that preserve the canonical-name set, lookup-table ordering drift, and declared-surface drift.
4. The canonical demo-path mapping remains explicit in `THREAD_PACKET.md`, including the concrete CLI-first blocker removed before Textual is enabled.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.
