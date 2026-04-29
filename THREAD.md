# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: current branch tip after the `20260429T013005Z` reviewer-fix commit.
- Previous implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Scope: command-catalog contract hardening for the current engine-first MVP focus without starting `feat-console`.
- Roadmap alignment: Milestone 3 CLI compatibility for the engine-first workflow loop, and `feat-commands` as the command-surface compatibility lane.
- Vision alignment: canonical engine contract stability while the CLI remains the active operator surface.

## Reviewed Files

- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

## Shared / Approval Notes

- Lane-owned implementation edits: `src/qual/commands/catalog.py`.
- Approved shared-by-approval test edits: `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`.
- Shared-by-approval edits: yes, `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` under approved exception.
- Integrator-locked edits: no.
- Gate-policy edits: no net review change after this fixer pass; `scripts/scope-check.sh` matches the branch review baseline and is absent from the net `main...HEAD` review diff.
- Metadata-only handoff files: `THREAD.md`, `THREAD_PACKET.md`.

## Canonical Demo-Path Mapping

- This makes the open/retrieve/basket/patch-review CLI smoke path more real by keeping the parser-visible command contract deterministic and failing fast when parser tokens drift from the command catalog.

## Reviewer Packet `20260429T012436Z` Fix Satisfaction

1. Review basis now points to the current branch tip instead of a stale `f8d860e` slice.
2. Post-`f8d860e` implementation and test commits are included in review rather than classified as metadata-only.
3. Parser-surface drift coverage includes added aliases, removed aliases, same-canonical substitutions such as replacing `bootstrap` with `open` or `diff-preview` with `diff`, token reordering, lookup-table shape/order drift, and declared-surface drift.
4. Ownership/accounting lists the approved shared test edits and keeps `scripts/scope-check.sh` out of the net `main...HEAD` review diff.

## Reviewer Packet `20260429T013005Z` Fix Satisfaction

1. `command_cli_contract()` validates the full parser-visible token surface through canonical tokens, canonical lookup-table shape, and grouped parser-surface checks.
2. Same-canonical substitutions are covered by focused tests, including `bootstrap` -> `open`, `diff-preview` -> `diff`, and `diff` -> `diff_preview` drift.
3. The handoff basis now points at the actual branch tip and does not classify test-changing commits as metadata-only.
4. Ownership accounting identifies `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` as approved shared-by-approval test edits, with no integrator-locked edits.
5. The canonical demo-path mapping explicitly names the protected `project-open`, `retrieval`, `patch-review`, and `export-handoff` command steps.
