# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Corrected review target: the branch tip produced by this fixer pass, with the corrected four-file merge-target list below.
- Current fixer packet validated: `fixer__feat-commands__20260429T225130Z`.
- Integration instruction: review and merge the corrected branch tip only if its merge diff remains exactly `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`; otherwise cherry-pick the final corrective commit target that preserves only that command-catalog slice.
- Rejected packet reconciled: prior packet traceability incorrectly treated `ab96cb722094e821105d1cdfd3cae24f4b9184ef`, `2836f5f0e4e0e903acc0e3633e6204be3f982a5d`, and `e72c69d75446e3ad10de3d3d0c7c30b4957c4baa` as metadata-only or ambiguous final-fixer work even though they modified implementation files. This packet classifies all three commits as implementation and reviews them with this packet refresh.
- Accurate implementation commits under review:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`: original command-catalog CLI contract implementation.
  - `ab96cb722094e821105d1cdfd3cae24f4b9184ef`: implementation fix for canonical-token drift, including alias-before-canonical regression coverage.
  - `2836f5f0e4e0e903acc0e3633e6204be3f982a5d`: implementation fix that enforces canonical parser tokens in `src/qual/commands/catalog.py` and refreshes packet traceability.
  - `e72c69d75446e3ad10de3d3d0c7c30b4957c4baa`: implementation fix that modifies `src/qual/commands/catalog.py` to require exact canonical CLI tokens in catalog order; this commit is not metadata-only.
- Metadata-only packet commits included in the branch-tip review basis but not classified as implementation: `0492bb2bc00dd03c126789985d9a5f18e5cd8e67`, `f1931ac437f5f051b397e36ca27560bd1023d975`, `0fe7c8c84e5f65bb0f557d191960ebbcf3946b9ef`, `07a3eeb86c53ae01416569b8806d63d4085e44c1`, `d020227ca44c691f2f8e655762b4465618f1faa5`, `19f037e38c13b9ae1891e3eb3d1a814663164f370`, `6201d051c5eaf86c35cfa123f7625bb9a874a112`, `d80fa9fa97faabae47000e07002757b76e5edc02`, `9d342e7ee5f0b4fb16493d5ef2744b3aa2a2846a`, `bb423d6d29fa2948a87edf13d083b93b3b3c83d1`, `58d798377fa0b9f968f1ac3807bc0bbd4aa00cd3`, `709ae30a46cb415bc1f986589e7b370c1a627831`, `9b5ce70fbf8085decb8c41206d541d1d15190033`, and the final fixer-pass commit for `fixer__feat-commands__20260429T225130Z`.
- Final fixer validation commit for reviewer packet `fixer__feat-commands__20260429T225130Z`: packet update confirming the corrected branch-tip target, required-fix mapping, accurate `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, `ab96cb722094e821105d1cdfd3cae24f4b9184ef`, `2836f5f0e4e0e903acc0e3633e6204be3f982a5d`, and `e72c69d75446e3ad10de3d3d0c7c30b4957c4baa` implementation classification, concrete MVP-loop blocker removed, ownership clarification, exact merge diff, focused regression verification, and green gates. The exact final HEAD SHA is reported by the fixer after commit creation.
- Merge base used for file accounting: `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`.
- Risk classification: low-risk lane-owned implementation plus one shared-by-approval unit-test exception and packet metadata; no integrator-locked files are changed.

## Required Handoff Fields

- Branch name: `codex/feat-commands`
- Scope completed: isolated the command catalog implementation slice from `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, included `ab96cb722094e821105d1cdfd3cae24f4b9184ef`, `2836f5f0e4e0e903acc0e3633e6204be3f982a5d`, and `e72c69d75446e3ad10de3d3d0c7c30b4957c4baa` as implementation fixes, and removed off-lane branch-tip changes from the corrected merge target.
- Implementation review basis: the branch tip produced by this fixer pass. This tip includes the corrected command-catalog slice from implementation commits `f8d860e`, `ab96cb7`, `2836f5f`, and `e72c69d`, plus metadata-only packet refreshes listed above.
- Roadmap item(s) affected: active MVP `feat-commands`; Milestone 3 command surface stability while Textual remains disabled.
- Vision capability affected: canonical engine contract and CLI compatibility through deterministic command catalog metadata.
- Exact canonical demo-path step advanced: `preview/apply/reject patch`.
- Canonical demo-path step advanced before handoff: this strengthens the open/retrieve/context-basket/patch-preview CLI control surface needed to execute the engine-first demo path while Textual remains disabled; the exact canonical step made more real by this command-catalog contract hardening is `preview/apply/reject patch`, with supporting coverage for `open project/document`, `retrieve/gather context into basket`, and `continue working` command routes.
- Scope-tightening blocker removed: parser/catalog drift could silently change the CLI smoke surface used to prove the engine-first loop while Textual remains disabled. The drift risk would let the `diff-preview` / `patch-review` command route be replaced or reordered by an alias without failing tests, weakening the CLI-first MVP loop at the exact point where operators must preview, apply, or reject patch work through the CLI fallback instead of Textual.
- Per-task canonical demo-path mapping using current engine-first MVP language:
  1. Exact canonical CLI-token validation advances `open project/document` via `bootstrap` / `project-open`, `retrieve/gather context into basket` via `context-basket` / `retrieval`, `preview/apply/reject patch` via `diff-preview` / `patch-review`, and `continue working` via `terminal` / `export-handoff` by requiring each catalog command to remain present as its exact parser token.
  2. The `_CLI_ENTRYPOINTS` alias-replacement regression advances `preview/apply/reject patch` via `diff-preview` / `patch-review` by proving alias `diff` cannot replace canonical parser token `diff-preview`.
  3. The `_CLI_ENTRYPOINTS` alias-before-canonical regression advances `preview/apply/reject patch` via `diff-preview` / `patch-review` by proving alias `diff` cannot precede canonical parser token `diff-preview`.
  4. The narrowed command-catalog target advances `preview/apply/reject patch` via `diff-preview` / `patch-review` by keeping review focused on command-surface stability for the patch-preview CLI fallback path.
  5. Packet refresh work advances the handoff evidence for `open project/document`, `retrieve/gather context into basket`, `preview/apply/reject patch`, and `continue working` by making the command-surface evidence and review target explicit for those CLI routes.
- Routing/provider impact note: none. No routing, provider configuration, model selection, or core entrypoint behavior is changed.
- Proposed `README.md` patch text: none.

## Tasks Completed

1. Tightened `command_cli_contract()` so each `command_names()` canonical entry must appear as a canonical CLI token in catalog order. Demo-path mapping: advances `open project/document` (`bootstrap` / `project-open`), `retrieve/gather context into basket` (`context-basket` / `retrieval`), `preview/apply/reject patch` (`diff-preview` / `patch-review`), and `continue working` (`terminal` / `export-handoff`) CLI entrypoint stability.
2. Added a regression test proving that removing canonical token `diff-preview` while keeping alias `diff` raises `ValueError`. Demo-path mapping: strengthens `preview/apply/reject patch` by preserving the canonical `diff-preview` / `patch-review` parser surface.
3. Added a regression test proving that alias `diff` cannot appear before canonical token `diff-preview`. Demo-path mapping: strengthens `preview/apply/reject patch` by preserving canonical-token precedence for the `diff-preview` / `patch-review` route.
4. Narrowed the corrected target to the command-catalog implementation slice: `src/qual/commands/catalog.py`, `tests/unit/test_commands_catalog.py`, and packet metadata only. Demo-path mapping: keeps this lane scoped to preserving the CLI surface for `preview/apply/reject patch`.
5. Regenerated `THREAD_PACKET.md` and `THREAD.md` so they describe the corrected branch-tip target, classify `ab96cb722094e821105d1cdfd3cae24f4b9184ef`, `2836f5f0e4e0e903acc0e3633e6204be3f982a5d`, and `e72c69d75446e3ad10de3d3d0c7c30b4957c4baa` as implementation, classify `d80fa9fa97faabae47000e07002757b76e5edc02`, `9d342e7ee5f0b4fb16493d5ef2744b3aa2a2846a`, `bb423d6d29fa2948a87edf13d083b93b3b3c83d1`, `58d798377fa0b9f968f1ac3807bc0bbd4aa00cd3`, `709ae30a46cb415bc1f986589e7b370c1a627831`, and `9b5ce70fbf8085decb8c41206d541d1d15190033` as metadata-only, and record this final fixer pass as the review target for `fixer__feat-commands__20260429T225130Z`. Demo-path mapping: keeps handoff evidence aligned with `open project/document`, `retrieve/gather context into basket`, `preview/apply/reject patch`, and `continue working` CLI routes.
6. Kept the unit test isolated to the catalog module so the corrected target does not require `src/qual/commands/__init__.py`. Demo-path mapping: limits validation to command-surface behavior used by `open project/document`, `retrieve/gather context into basket`, `preview/apply/reject patch`, and `continue working` in the engine-first CLI fallback path.

## Complete Corrected File List

Exact corrected merge diff from `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27` to the current branch tip:

- `THREAD.md`
- `THREAD_PACKET.md`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

Exact final merge diff name-status:

- `M THREAD.md`
- `A THREAD_PACKET.md`
- `A src/qual/commands/catalog.py`
- `A tests/unit/test_commands_catalog.py`

Exact final merge diff stat:

- `THREAD.md`: 23 changed lines.
- `THREAD_PACKET.md`: 98 inserted lines.
- `src/qual/commands/catalog.py`: 1094 inserted lines.
- `tests/unit/test_commands_catalog.py`: 678 inserted lines.

## Ownership And Scope

- Lane-owned implementation path changed: `src/qual/commands/catalog.py`.
- Shared-by-approval test path changed: `tests/unit/test_commands_catalog.py`.
- Packet metadata files changed: `THREAD.md`, `THREAD_PACKET.md`.
- Shared-by-approval files changed: approved exception for `tests/unit/test_commands_catalog.py` to cover the command-catalog alias-replacement regression.
- Integrator-locked files changed: none in the corrected target.
- Clarified ownership note: shared-by-approval test edit is `YES`; integrator-locked implementation edit is `NO`.
- Corrected ownership note: the owned runtime edit is `src/qual/commands/catalog.py`; the approved shared-by-approval test edit is `tests/unit/test_commands_catalog.py`; no integrator-locked files were edited in the reviewed implementation diff.
- Routing/provider impact: none.

## Commands Run

- `make scope-check`: PASS on 2026-04-29 for the exact corrected branch-tip target after `fixer__feat-commands__20260429T225130Z`.
- `./quality-format.sh --check`: PASS on 2026-04-29 for the exact corrected branch-tip target after `fixer__feat-commands__20260429T225130Z`.
- `./quality-lint.sh`: PASS on 2026-04-29 for the exact corrected branch-tip target after `fixer__feat-commands__20260429T225130Z`.
- `./quality-test.sh`: PASS on 2026-04-29 for the exact corrected branch-tip target after `fixer__feat-commands__20260429T225130Z`.
- `./typecheck-test.sh`: PASS on 2026-04-29 for the exact corrected branch-tip target after `fixer__feat-commands__20260429T225130Z`.
- `make ci`: PASS on 2026-04-29 for the exact corrected branch-tip target after `fixer__feat-commands__20260429T225130Z`.
- `python -m unittest tests.unit.test_commands_catalog`: PASS on 2026-04-29 for the reviewer-required canonical parser-token drift regressions.

## Risks And Blockers

- Risk: branch history still contains rejected broad-scope commits, but the corrected branch-tip merge diff is narrowed to the four-file target above and `ab96cb722094e821105d1cdfd3cae24f4b9184ef` is now explicitly reviewed as implementation.
- Blockers: none after required gates pass.

## Final Readiness Statement

This packet asks review of the corrected branch-tip target only: command catalog implementation, its unit tests, and accurate packet metadata. This strengthens the open/retrieve/context-basket/patch-preview CLI control surface needed to execute the engine-first demo path while Textual remains disabled; the corrected command-catalog work makes `preview/apply/reject patch` more real by preserving deterministic canonical CLI command names, parser tokens, and alias behavior for the patch-preview command surface. The concrete blocker removed is parser/catalog drift silently changing the CLI smoke route operators use to prove patch preview while the UI remains disabled.
