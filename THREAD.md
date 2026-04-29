# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: current branch tip after this reviewer-fix commit.
- Previous implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Scope: command-catalog contract hardening for the current engine-first MVP focus without starting `feat-console`.
- Roadmap alignment: Milestone 3 CLI compatibility for the engine-first workflow loop, and `feat-commands` as the command-surface compatibility lane.
- Vision alignment: canonical engine contract stability while the CLI remains the active operator surface.

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Shared / Approval Notes

- Lane-owned implementation edits: `src/qual/commands/catalog.py`.
- Approved shared-by-approval test edit: `tests/unit/test_commands_catalog.py`.
- Shared-by-approval edits: yes, `tests/unit/test_commands_catalog.py` under approved exception.
- Integrator-locked edits: no.
- Gate-policy edits: no net change after this fixer pass.
- Metadata-only handoff files: `THREAD.md`, `THREAD_PACKET.md`.

## Canonical Demo-Path Mapping

- This makes the open/retrieve/basket/patch-review CLI smoke path more real by keeping the parser-visible command contract deterministic and failing fast when parser tokens drift from the command catalog.

## Reviewer Packet `20260429T010426Z` Fix Satisfaction

1. Review basis now points to the current branch tip instead of a stale `f8d860e` slice.
2. Post-`f8d860e` implementation and test commits are included in review rather than classified as metadata-only.
3. Parser-surface drift coverage includes added aliases, removed aliases, same-canonical substitutions, token reordering, lookup-table shape/order drift, and declared-surface drift.
4. Ownership/accounting lists the approved shared test edit and removes the prior `scripts/scope-check.sh` policy edit from the net diff.
