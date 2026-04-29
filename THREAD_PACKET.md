# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Corrected review target: the current branch tip after this fixer commit, with the corrected four-file target listed below.
- Integration instruction: review and merge the corrected branch tip only if its merge diff remains exactly `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`; otherwise cherry-pick the final corrective commit target that preserves only that command-catalog slice.
- Rejected packet reconciled: `f5a35438c2808b247cb70a86da7e0e9b19f82f67` claimed a metadata-only packet refresh while modifying both `THREAD.md` and `THREAD_PACKET.md`, and described a broad full-branch-tip review target. This packet replaces that with a narrowed command-catalog review target.
- Merge base used for file accounting: `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`.
- Risk classification: low-risk; implementation changes stay in `src/qual/commands/**` with unit-test coverage and packet metadata.

## Required Handoff Fields

- Branch name: `codex/feat-commands`
- Scope completed: isolated the command catalog implementation slice from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and removed off-lane branch-tip changes from the corrected merge target.
- Implementation review basis: starts from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this fixer tightens the CLI contract guard, adds the alias-replacement regression, and refreshes packet metadata.
- Roadmap item(s) affected: active MVP `feat-commands`; Milestone 3 command surface stability while Textual remains disabled.
- Vision capability affected: canonical engine contract and CLI compatibility through deterministic command catalog metadata.
- Canonical demo-path step advanced: this command-catalog hardening strengthens the CLI path for `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch` by keeping command tokens and canonical command names deterministic.
- Routing/provider impact note: none. No routing, provider configuration, model selection, or core entrypoint behavior is changed.
- Proposed `README.md` patch text: none.

## Tasks Completed

1. Tightened `command_cli_contract()` so each `command_names()` canonical entry must appear as a canonical CLI token in catalog order. Demo-path mapping: strengthens `open project/document`, `retrieve relevant material`, and `apply/reject` CLI entrypoint stability.
2. Added a regression test proving that removing canonical token `diff-preview` while keeping alias `diff` raises `ValueError`. Demo-path mapping: strengthens `apply/reject` by preserving the canonical diff-preview parser surface.
3. Narrowed the corrected target to the command-catalog implementation slice: `src/qual/commands/catalog.py`, `tests/unit/test_commands_catalog.py`, and packet metadata only. Demo-path mapping: keeps this lane scoped to command-surface stability for the active demo path.
4. Regenerated `THREAD_PACKET.md` and `THREAD.md` so they describe the corrected branch-tip target instead of the rejected broad review basis. Demo-path mapping: keeps handoff evidence aligned with command-catalog work that supports `open project/document`, `retrieve relevant material`, and `apply/reject`.
5. Reconciled the prior metadata mismatch by explicitly noting that `f5a35438c2808b247cb70a86da7e0e9b19f82f67` modified both packet files and described the wrong target. Demo-path mapping: keeps review metadata accurate for the command-catalog handoff.
6. Kept the unit test isolated to the catalog module so the corrected target does not require `src/qual/commands/__init__.py`. Demo-path mapping: limits validation to command-surface behavior used by the active demo path.

## Complete Corrected File List

Actual corrected merge diff from `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27` to the current branch tip:

- `THREAD.md`
- `THREAD_PACKET.md`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Ownership And Scope

- Lane-owned implementation path changed: `src/qual/commands/catalog.py`.
- Test path changed: `tests/unit/test_commands_catalog.py`.
- Metadata-only handoff files changed: `THREAD.md`, `THREAD_PACKET.md`.
- Shared-by-approval files changed: none in the corrected target.
- Integrator-locked files changed: none in the corrected target.
- Routing/provider impact: none.

## Commands Run

- `make scope-check`: PASS on the corrected target.
- `./quality-format.sh --check`: PASS on the corrected target.
- `./quality-lint.sh`: PASS on the corrected target.
- `./quality-test.sh`: PASS on the corrected target.
- `./typecheck-test.sh`: PASS on the corrected target.
- `make ci`: PASS on the corrected target.

## Risks And Blockers

- Risk: branch history still contains rejected broad-scope commits, but the corrected branch-tip merge diff is narrowed to the four-file target above.
- Blockers: none after required gates pass.

## Final Readiness Statement

This packet asks review of the corrected branch-tip target only: command catalog implementation, its unit tests, and accurate packet metadata. It does not ask reviewer or integrator to approve the prior broad full-branch-tip scope.
