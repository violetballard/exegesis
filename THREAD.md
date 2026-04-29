# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Implementation review target: current branch tip after fixer prompt `20260429T045635Z`
- Current handoff refresh: reviewer fix after prompt `20260429T045635Z`
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

## Fixer Prompt `20260429T042935Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T042935Z`; review should use branch tip after this fixer commit.
2. The branch-tip command-catalog implementation still validates exact parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. Regression coverage still includes extra same-canonical aliases, missing expected aliases, substituted aliases, parser token ordering drift, lookup-table substitutions that preserve the canonical-name set, lookup-table ordering drift, and declared-surface drift.
4. The canonical demo-path mapping remains explicit in `THREAD_PACKET.md`, including the concrete CLI-first blocker removed before Textual is enabled.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T043211Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T043211Z`; review should use the current branch tip after this fixer commit, not `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` alone.
2. `THREAD_PACKET.md` lists the post-anchor implementation commit ledger source for every non-metadata commit that touched `src/qual/commands/catalog.py` or `tests/unit/test_commands_catalog.py` after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
3. The final implementation file set remains `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; metadata-only files remain `THREAD.md` and `THREAD_PACKET.md`.
4. The scope completed is restated as full parser-token surface validation, not only deduplicated canonical-name validation.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T043434Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T043434Z`; review should use the current branch tip after this fixer commit.
2. The branch-tip command-catalog implementation still validates exact accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. Regression coverage still includes added known aliases, removed expected tokens, same-canonical substitutions, parser token ordering drift, lookup-table substitutions, and declared-surface drift.
4. `THREAD_PACKET.md` keeps the unambiguous branch-tip review basis, post-anchor implementation ledger, final implementation file set, and metadata-only file accounting.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T043529Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T043529Z`; review should use the current branch tip after this fixer commit.
2. The branch-tip command-catalog implementation still validates exact accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. Regression coverage includes added known aliases while canonical names still match, removed expected tokens, same-canonical substitutions, parser token ordering drift, lookup-table substitutions, and declared-surface drift.
4. `THREAD_PACKET.md` keeps the unambiguous branch-tip review basis, post-anchor implementation ledger, final implementation file set, and metadata-only file accounting.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T043929Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T043929Z`; review should use the current branch tip after this fixer commit.
2. The branch-tip command-catalog implementation validates exact accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. Regression coverage now also includes canonical-name set drift while the parser token and lookup surfaces remain stable.
4. `THREAD_PACKET.md` keeps the unambiguous branch-tip review basis, post-anchor implementation ledger, final implementation file set, metadata-only file accounting, and canonical demo-path mapping.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T044208Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T044208Z`; review should use the current branch tip after this fixer commit.
2. The branch-tip command-catalog implementation validates exact accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. Regression coverage includes canonical-name set drift while the parser token and lookup surfaces remain stable, plus the reviewer-requested added alias, removed token, substituted same-canonical alias, token order, and lookup-table substitution drift cases.
4. `THREAD_PACKET.md` keeps one branch-tip review basis, the post-anchor implementation ledger, final implementation file set, metadata-only file accounting, shared-test approval basis, and canonical demo-path mapping.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T044433Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T044433Z`; review should use the current branch tip after this fixer commit.
2. The branch-tip command-catalog implementation validates exact accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. Regression coverage includes a self-consistent reordered parser projection with matching lookup-table order, plus the reviewer-requested added alias, removed token, substituted same-canonical alias, token order, and lookup-table substitution drift cases.
4. `THREAD_PACKET.md` keeps one branch-tip review basis, the post-anchor implementation ledger, final implementation file set, metadata-only file accounting, shared-test approval basis, and canonical demo-path mapping.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T044747Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T044747Z`; review should use the current branch tip after this fixer commit.
2. The branch-tip command-catalog implementation continues to validate exact accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. Focused command-catalog coverage remains green for added aliases, missing tokens, substituted same-canonical aliases, token order drift, lookup-table substitution drift, and self-consistent parser projection drift.
4. `THREAD_PACKET.md` keeps one branch-tip review basis, the post-anchor implementation ledger, final implementation file set, metadata-only file accounting, shared-test approval basis, and canonical demo-path mapping.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T045030Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T045030Z`; review should use the current branch tip after this fixer commit.
2. The branch-tip command-catalog implementation continues to validate exact accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
3. Focused command-catalog coverage remains green for added known aliases, removed aliases, same-canonical substitutions, parser-token reordering, lookup-table substitution drift, and self-consistent parser projection drift.
4. `THREAD_PACKET.md` keeps one branch-tip review basis, the post-anchor implementation ledger, final implementation file set, metadata-only file accounting, shared-test approval basis, and canonical demo-path mapping.
5. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T045321Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T045321Z`; review should use the current branch tip after this fixer commit.
2. `THREAD_PACKET.md` keeps each completed task mapped to the canonical demo-path steps it supports and keeps the AGENTS.md final demo-path statement explicit.
3. Ownership accounting now states that no integrator-locked files were edited and that the only non-owned path is the approved shared-test exception `tests/unit/test_commands_catalog.py`.
4. Required gates are rerun after this refresh and recorded in `THREAD_PACKET.md`.

## Fixer Prompt `20260429T045635Z` Fix Satisfaction

1. The handoff target is refreshed for prompt `20260429T045635Z`; review should use the current branch tip after this fixer commit, not the original `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` anchor alone.
2. `command_cli_contract()` now also checks the returned canonical-name tuple directly against the canonical parser-surface projection, while preserving the exact token, lookup-table, grouped-surface, and declared-surface drift checks.
3. The approved shared command-catalog tests still cover added same-canonical aliases, removed tokens, substituted aliases, token order drift, lookup-table order/substitution drift, and declared-surface drift.
4. `THREAD_PACKET.md` keeps each completed task mapped to the canonical demo-path steps it supports, names the blocker removed, and records the latest required gate run.
