# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Corrected review target: the current branch tip after this fixer packet refresh commit only, with the corrected four-file merge-target list below.
- Integration instruction: review and merge the corrected branch tip only if its merge diff remains exactly `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`; otherwise cherry-pick the final corrective commit target that preserves only that command-catalog slice.
- Rejected packet reconciled: prior packet traceability incorrectly treated `ab96cb722094e821105d1cdfd3cae24f4b9184ef` and `2836f5f0e4e0e903acc0e3633e6204be3f982a5d` as metadata-only even though they modified implementation files. This packet classifies both commits as implementation and reviews them with this packet refresh.
- Accurate implementation commits under review:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`: original command-catalog CLI contract implementation.
  - `ab96cb722094e821105d1cdfd3cae24f4b9184ef`: implementation fix for canonical-token drift, including alias-before-canonical regression coverage.
  - `2836f5f0e4e0e903acc0e3633e6204be3f982a5d`: implementation fix that enforces canonical parser tokens in `src/qual/commands/catalog.py` and refreshes packet traceability.
  - `0492bb2bc00dd03c126789985d9a5f18e5cd8e67`: metadata-only packet refresh that documents the additional implementation commits above; it is not itself implementation.
  - This fixer packet refresh commit: metadata-only correction that resubmits the corrected packet without changing implementation behavior.
- Merge base used for file accounting: `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`.
- Risk classification: low-risk lane-owned implementation plus one shared-by-approval unit-test exception and packet metadata; no integrator-locked files are changed.

## Required Handoff Fields

- Branch name: `codex/feat-commands`
- Scope completed: isolated the command catalog implementation slice from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, included `ab96cb722094e821105d1cdfd3cae24f4b9184ef` and `2836f5f0e4e0e903acc0e3633e6204be3f982a5d` as implementation fixes, and removed off-lane branch-tip changes from the corrected merge target.
- Implementation review basis: the current branch tip after this fixer packet refresh commit only. This tip includes the corrected command-catalog slice from `f8d860e`, `ab96cb7`, and `2836f5f`, plus metadata-only packet refreshes from `0492bb2` and this commit.
- Roadmap item(s) affected: active MVP `feat-commands`; Milestone 3 command surface stability while Textual remains disabled.
- Vision capability affected: canonical engine contract and CLI compatibility through deterministic command catalog metadata.
- Exact canonical demo-path step advanced: `preview/apply/reject patch`.
- Canonical demo-path step advanced: this command-catalog hardening makes `preview/apply/reject patch` more real by preserving deterministic command tokens and canonical command names for the patch-preview command surface.
- Per-task canonical demo-path mapping using current engine-first MVP language:
  1. Exact canonical CLI-token validation advances the engine-first path `Engine stability -> A2UI contracts with CLI fallback -> preview/apply/reject patch` by requiring each catalog command, including `diff-preview`, to remain present as its exact parser token.
  2. The `_CLI_ENTRYPOINTS` alias-replacement regression advances the engine-first path `Engine stability -> A2UI contracts with CLI fallback -> preview/apply/reject patch` by proving alias `diff` cannot replace canonical parser token `diff-preview`.
  3. The `_CLI_ENTRYPOINTS` alias-before-canonical regression advances the engine-first path `Engine stability -> A2UI contracts with CLI fallback -> preview/apply/reject patch` by proving alias `diff` cannot precede canonical parser token `diff-preview`.
  4. The narrowed command-catalog target advances the engine-first path `Engine stability -> A2UI contracts with CLI fallback -> preview/apply/reject patch` by keeping review focused on command-surface stability for the patch-preview CLI fallback path.
  5. Packet refresh work advances the engine-first path `Engine stability -> A2UI contracts with CLI fallback -> preview/apply/reject patch` by making the command-surface evidence and review target explicit for that path.
- Routing/provider impact note: none. No routing, provider configuration, model selection, or core entrypoint behavior is changed.
- Proposed `README.md` patch text: none.

## Tasks Completed

1. Tightened `command_cli_contract()` so each `command_names()` canonical entry must appear as a canonical CLI token in catalog order. Demo-path mapping: advances `preview/apply/reject patch` CLI entrypoint stability.
2. Added a regression test proving that removing canonical token `diff-preview` while keeping alias `diff` raises `ValueError`. Demo-path mapping: strengthens `preview/apply/reject patch` by preserving the canonical `diff-preview` parser surface.
3. Added a regression test proving that alias `diff` cannot appear before canonical token `diff-preview`. Demo-path mapping: strengthens `preview/apply/reject patch` by preserving canonical-token precedence.
4. Narrowed the corrected target to the command-catalog implementation slice: `src/qual/commands/catalog.py`, `tests/unit/test_commands_catalog.py`, and packet metadata only. Demo-path mapping: keeps this lane scoped to preserving the CLI surface for `preview/apply/reject patch`.
5. Regenerated `THREAD_PACKET.md` and `THREAD.md` so they describe the corrected branch-tip target, classify `ab96cb722094e821105d1cdfd3cae24f4b9184ef` and `2836f5f0e4e0e903acc0e3633e6204be3f982a5d` as implementation, and classify `0492bb2bc00dd03c126789985d9a5f18e5cd8e67` as metadata-only. Demo-path mapping: keeps handoff evidence aligned with the engine-first path `Engine stability -> A2UI contracts with CLI fallback -> preview/apply/reject patch`.
6. Kept the unit test isolated to the catalog module so the corrected target does not require `src/qual/commands/__init__.py`. Demo-path mapping: limits validation to command-surface behavior used by the engine-first path `Engine stability -> A2UI contracts with CLI fallback -> preview/apply/reject patch`.

## Complete Corrected File List

Actual corrected merge diff from `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27` to the current branch tip:

- `THREAD.md`
- `THREAD_PACKET.md`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Ownership And Scope

- Lane-owned implementation path changed: `src/qual/commands/catalog.py`.
- Shared-by-approval test path changed: `tests/unit/test_commands_catalog.py`.
- Packet metadata files changed: `THREAD.md`, `THREAD_PACKET.md`.
- Shared-by-approval files changed: approved exception for `tests/unit/test_commands_catalog.py` to cover the command-catalog alias-replacement regression.
- Integrator-locked files changed: none in the corrected target.
- Corrected ownership note: the reviewed implementation touched `src/qual/commands/catalog.py` plus approved shared test `tests/unit/test_commands_catalog.py`; no integrator-locked files were changed in the reviewed implementation commit.
- Routing/provider impact: none.

## Commands Run

- `make scope-check`: PASS on the corrected target.
- `./quality-format.sh --check`: PASS on the corrected target.
- `./quality-lint.sh`: PASS on the corrected target.
- `./quality-test.sh`: PASS on the corrected target.
- `./typecheck-test.sh`: PASS on the corrected target.
- `make ci`: PASS on the corrected target.

## Risks And Blockers

- Risk: branch history still contains rejected broad-scope commits, but the corrected branch-tip merge diff is narrowed to the four-file target above and `ab96cb722094e821105d1cdfd3cae24f4b9184ef` is now explicitly reviewed as implementation.
- Blockers: none after required gates pass.

## Final Readiness Statement

This packet asks review of the corrected branch-tip target only: command catalog implementation, its unit tests, and accurate packet metadata. The corrected command-catalog work now makes `preview/apply/reject patch` more real by preserving deterministic canonical CLI command names, parser tokens, and alias behavior for the patch-preview command surface.
