# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Corrected review target: the full current branch tip produced by this fixer pass, not the earlier `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice.
- Current fixer packet validated: `fixer__feat-commands__20260429T230431Z`.
- Integration instruction: review the full branch-tip merge diff exactly as reported below. This packet no longer asks reviewers to treat `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as the only implementation commit.
- Rejected packet reconciled: prior packet traceability incorrectly treated the branch-tip implementation basis as a four-commit slice. The actual implementation history for the branch tip is the full set of commits touching `src/qual/commands/catalog.py` or `tests/unit/test_commands_catalog.py` between `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27` and this branch tip.
- Accurate implementation commits under review: `git log --reverse --format='%H %s' main..HEAD -- src/qual/commands/catalog.py tests/unit/test_commands_catalog.py` reports `339` implementation commits for the current branch-tip review target. This includes `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, `ab96cb722094e821105d1cdfd3cae24f4b9184ef`, `2836f5f0e4e0e903acc0e3633e6204be3f982a5d`, and `e72c69d75446e3ad10de3d3d0c7c30b4957c4baa`, but is not limited to them. Reviewers should treat that generated command output as the implementation commit list for this over-budget branch-tip target.
- Metadata-only packet commits: all commits in `main..HEAD` that do not touch `src/qual/commands/catalog.py` or `tests/unit/test_commands_catalog.py` are packet, traceability, or handoff maintenance for this branch-tip review. They are included in branch history but are not used to narrow the implementation basis.
- Merge base used for file accounting: `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`.
- Risk classification: over-budget branch-tip review target. The merge diff is lane-owned implementation plus one shared-by-approval unit-test exception and packet metadata; no integrator-locked files are changed.

## Required Handoff Fields

- Branch name: `codex/feat-commands`
- Scope completed: command catalog implementation and regression coverage as represented by the full branch-tip merge diff. This packet does not claim the implementation basis is narrowed to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Implementation review basis: the branch tip produced by this fixer pass. The implementation history is the full 339-commit set returned by `git log --reverse --format='%H %s' main..HEAD -- src/qual/commands/catalog.py tests/unit/test_commands_catalog.py`.
- Roadmap item(s) affected: active MVP `feat-commands`; Milestone 3 command surface stability while Textual remains disabled.
- Vision capability affected: canonical engine contract and CLI compatibility through deterministic command catalog metadata.
- Exact canonical demo-path step advanced: `preview/apply/reject patch`.
- Canonical demo-path step advanced before handoff: this strengthens the CLI control surface needed to execute the engine-first demo path while Textual remains disabled; the exact canonical step made more real by this command-catalog contract hardening is `preview/apply/reject patch`, with supporting coverage for `open project/document`, `retrieve relevant material`, `promote/gather context`, and `save and continue` command routes.
- Scope-tightening blocker removed: parser/catalog drift could silently change the CLI smoke surface used to prove the engine-first loop while Textual remains disabled. The drift risk would let the `diff-preview` / `patch-review` command route be replaced or reordered by an alias without failing tests, weakening the CLI-first MVP loop at the exact point where operators must preview, apply, or reject patch work through the CLI fallback instead of Textual.
- Budget and size compliance: `NOT COMPLIANT` with the normal AGENTS size limits. The exact branch-tip merge diff from `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27` is `1891` insertions and `2` deletions across `4` files, which exceeds both the high-risk `<=300` net LOC and default `<=500` net LOC limits. This review requires explicit integrator acceptance of an over-budget branch-tip target or a separate split/cherry-pick request; this packet does not assert normal budget compliance.
- Per-task canonical demo-path mapping using current engine-first MVP language:
  1. Exact canonical CLI-token validation advances `open project/document` via `bootstrap` / `project-open`, `retrieve relevant material` via `retrieval`, `promote/gather context` via `context-basket`, `preview/apply/reject patch` via `diff-preview` / `patch-review`, and `save and continue` via `terminal` / `export-handoff` by requiring each catalog command to remain present as its exact parser token.
  2. The `_CLI_ENTRYPOINTS` alias-replacement regression advances `preview/apply/reject patch` via `diff-preview` / `patch-review` by proving alias `diff` cannot replace canonical parser token `diff-preview`.
  3. The `_CLI_ENTRYPOINTS` alias-before-canonical regression advances `preview/apply/reject patch` via `diff-preview` / `patch-review` by proving alias `diff` cannot precede canonical parser token `diff-preview`.
  4. The branch-tip command-catalog target advances `preview/apply/reject patch` via `diff-preview` / `patch-review` by keeping the reviewed runtime surface focused on command-surface stability for the patch-preview CLI fallback path.
  5. Packet refresh work advances the handoff evidence for `open project/document`, `retrieve relevant material`, `promote/gather context`, `preview/apply/reject patch`, and `save and continue` by making the command-surface evidence, review target, and over-budget status explicit for those CLI routes.
- Routing/provider impact note: none. No routing, provider configuration, model selection, or core entrypoint behavior is changed.
- Proposed `README.md` patch text: none.

## Tasks Completed

1. Tightened `command_cli_contract()` so each `command_names()` canonical entry must appear as a canonical CLI token in catalog order. Demo-path mapping: advances `open project/document` (`bootstrap` / `project-open`), `retrieve relevant material` (`retrieval`), `promote/gather context` (`context-basket`), `preview/apply/reject patch` (`diff-preview` / `patch-review`), and `save and continue` (`terminal` / `export-handoff`) CLI entrypoint stability.
2. Added a regression test proving that removing canonical token `diff-preview` while keeping alias `diff` raises `ValueError`. Demo-path mapping: strengthens `preview/apply/reject patch` by preserving the canonical `diff-preview` / `patch-review` parser surface.
3. Added a regression test proving that alias `diff` cannot appear before canonical token `diff-preview`. Demo-path mapping: strengthens `preview/apply/reject patch` by preserving canonical-token precedence for the `diff-preview` / `patch-review` route.
4. Kept the corrected branch-tip merge diff to `src/qual/commands/catalog.py`, `tests/unit/test_commands_catalog.py`, and packet metadata only, while truthfully reporting that the history behind those files is over budget. Demo-path mapping: keeps this lane scoped to preserving the CLI surface for `preview/apply/reject patch`.
5. Regenerated `THREAD_PACKET.md` and `THREAD.md` so they describe the full branch-tip target, classify implementation history by actual file touches, and record this final fixer pass as the review target for `fixer__feat-commands__20260429T230431Z`. Demo-path mapping: keeps handoff evidence aligned with `open project/document`, `retrieve relevant material`, `promote/gather context`, `preview/apply/reject patch`, and `save and continue` CLI routes.
6. Kept the unit test isolated to the catalog module so the corrected target does not require `src/qual/commands/__init__.py`. Demo-path mapping: limits validation to command-surface behavior used by `open project/document`, `retrieve relevant material`, `promote/gather context`, `preview/apply/reject patch`, and `save and continue` in the engine-first CLI fallback path.

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
- Total branch-tip diff size: `1891` insertions, `2` deletions, `1889` net LOC. This exceeds AGENTS size budgets.

## Ownership And Scope

- Lane-owned implementation path changed: `src/qual/commands/catalog.py`.
- Shared-by-approval test path changed: `tests/unit/test_commands_catalog.py`.
- Packet metadata files changed: `THREAD.md`, `THREAD_PACKET.md`.
- Shared-by-approval files changed: approved exception for `tests/unit/test_commands_catalog.py` to cover the command-catalog alias-replacement regression.
- Integrator-locked files changed: none in the corrected target.
- Clarified ownership note: shared-by-approval test edit is `YES`; integrator-locked implementation edit is `NO`.
- Routing/provider impact: none.

## Commands Run

- `make scope-check`: PASS on 2026-04-29 for `fixer__feat-commands__20260429T230431Z`.
- `./quality-format.sh --check`: PASS on 2026-04-29 for `fixer__feat-commands__20260429T230431Z`.
- `./quality-lint.sh`: PASS on 2026-04-29 for `fixer__feat-commands__20260429T230431Z`.
- `./quality-test.sh`: PASS on 2026-04-29 for `fixer__feat-commands__20260429T230431Z`.
- `./typecheck-test.sh`: PASS on 2026-04-29 for `fixer__feat-commands__20260429T230431Z`.
- `make ci`: PASS on 2026-04-29 for `fixer__feat-commands__20260429T230431Z`.
- `python -m unittest tests.unit.test_commands_catalog`: PASS on 2026-04-29 for `fixer__feat-commands__20260429T230431Z`.

## Risks And Blockers

- Risk: branch-tip diff size exceeds AGENTS size budgets. This packet is intentionally truthful about that status and requires integrator acceptance of the over-budget branch tip or a follow-up split/cherry-pick instruction.
- Blockers: none after required gates pass.

## Final Readiness Statement

This packet asks review of the full corrected branch-tip target: command catalog implementation, its unit tests, and accurate packet metadata. The corrected command-catalog work makes the canonical demo-path step `preview/apply/reject patch` more real by preserving deterministic canonical CLI command names, parser tokens, and alias behavior for the `diff-preview` / `patch-review` command surface. The concrete blocker removed is parser/catalog drift silently changing the CLI smoke route operators use to prove patch preview while the UI remains disabled. The branch tip is over the normal AGENTS size budget and must be accepted explicitly or split by integrator instruction.
