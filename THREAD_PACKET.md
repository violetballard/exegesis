# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: full branch tip of `codex/feat-commands`
- Review basis: `git diff main...codex/feat-commands`
- Review target tip before this fixer pass: `9a476b0ad862d2770f9cd32c549b5a6fa2e33ba5`
- Latest implementation-bearing commit before this metadata-only fixer pass: `04974e20df08b704f39a065e6082194f9024fd26`
- Fixer prompt satisfied: `20260429T135712Z`

This packet supersedes all earlier packets and packet-refresh notes. The selected review target is the full branch tip, not a narrowed `f8d860ed9` slice. Commits after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` are in review scope when they affect the final branch-tip implementation/test diff. Commit `04974e20df08b704f39a065e6082194f9024fd26` is included in implementation scope because it changes `tests/unit/test_commands_catalog.py` as well as handoff metadata; it is not described as metadata-only. Commits `e19ff6362a4b6f9cae64810dca7414b1c526ed99` and `9a476b0ad862d2770f9cd32c549b5a6fa2e33ba5` are metadata-only and remain in review scope as packet corrections. This `20260429T135712Z` fixer pass is metadata-only and exists to correct review-target traceability.

## Required-Fix Resolution

1. Parser drift coverage is enforceable against the live argparse surface: `command_cli_contract()` imports and compares `src.qual.cli.command_parser_lookup_table()` against the catalog-owned lookup table, and `tests/unit/test_commands_catalog.py` covers parser token rename, extra-token, and missing-token drift from the actual subparser choices.
2. Review basis is unambiguous: review the full branch tip with `git diff main...codex/feat-commands`.
3. Files changed are listed from that branch-tip review basis, including `src/qual/cli.py`, `src/qual/commands/__init__.py`, and all other files in `main...HEAD`.
4. The earlier full-branch parser edit to `src/qual/cli.py` is explicitly included as an approved shared/integrator-locked exception because the parser must consume catalog-owned CLI tokens to keep the command contract enforceable; this `20260429T131018Z` fixer slice did not newly edit integrator-locked files.
5. The false metadata-only label is removed.
6. Every completed task below maps to the exact canonical MVP demo-path step it strengthens.
7. The concrete blocker statement below explains why parser/catalog drift was direct loop breakage for the CLI-first Milestone 3 path.
8. The final readiness statement names which canonical demo-path steps this command-catalog slice now makes more real.
9. Ownership wording now distinguishes the approved shared-test exception from the earlier branch-tip integrator-locked parser exception.
10. Fresh gate evidence is recorded for the `20260429T131636Z` offline-review fallback fix request; no source changes were required because all required gates passed on rerun.
11. Intended review target is explicitly the current branch tip, including implementation commits `894e6c128e4e2ece1406f4e95f5086b774955905` (`Add MVP demo command lookup contract`) and `04974e20df08b704f39a065e6082194f9024fd26` (`fix(commands): satisfy branch tip lookup review`).
12. The `894e6c128...` runtime API/export changes are listed as implementation scope: `CommandDemoPathLookupContract`, `command_mvp_demo_path_lookup_contract()`, `command_mvp_demo_path_lookup_table()`, `command_mvp_demo_path_command_lookup_table()`, `command_mvp_demo_path_cli_lookup_table()`, `command_mvp_demo_path_action_lookup_table()`, and `command_mvp_demo_path_handoff_lookup_table()`.
13. The branch-tip demo lookup contract is mapped to the canonical demo path as a direct strengthening of `retrieve material`, `gather/promote context`, `preview/apply/reject patch`, `persist/save`, and `continue`, with `open document` retained in the ordered lookup surface.
14. The `04974e20...` shared-test delta is explicitly in scope: `tests/unit/test_commands_catalog.py` keeps public demo-path lookup export regression coverage visible in the reviewed branch-tip diff.
15. The current fixer pass updates packet traceability; it does not hide `894e6c128...`, `04974e20...`, or the shared-test delta behind a metadata-only label.
16. Fresh `20260429T135712Z` gate evidence below is for the exact branch tip proposed for merge after this packet update.
17. This packet now explicitly names the exact `f8d860ed9..HEAD` comparison that triggered re-review: `git diff --name-status f8d860ed9f6299f0169c4f21321ac5f37c949fd3..9a476b0ad862d2770f9cd32c549b5a6fa2e33ba5` changes `THREAD.md`, `THREAD_PACKET.md`, `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
18. The complete post-`f8d860e` implementation-bearing commit list for the final branch-tip code/test delta is the 243-commit set returned by `git log --oneline --reverse f8d860ed9f6299f0169c4f21321ac5f37c949fd3..9a476b0ad862d2770f9cd32c549b5a6fa2e33ba5 -- src/qual/cli.py src/qual/commands/__init__.py src/qual/commands/catalog.py tests/unit/test_commands_catalog.py`; no later packet-refresh commit is treated as a substitute review basis.

## Implementation Commit List

Current review target: full branch tip of `codex/feat-commands` after the `20260429T135712Z` fixer packet update.

Implementation commits that must be reviewed as implementation scope include every code/test-bearing commit in `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..9a476b0ad862d2770f9cd32c549b5a6fa2e33ba5` that touches `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, or `tests/unit/test_commands_catalog.py`. The exact audit command is:

```sh
git log --oneline --reverse f8d860ed9f6299f0169c4f21321ac5f37c949fd3..9a476b0ad862d2770f9cd32c549b5a6fa2e33ba5 -- src/qual/cli.py src/qual/commands/__init__.py src/qual/commands/catalog.py tests/unit/test_commands_catalog.py
```

That command currently returns 243 commits. The following commits are the non-metadata branch-tip implementation commits that materially define the final public command contract and test surface and therefore must not be hidden behind packet-refresh labels:

- `f8d860ed9` - `feat(commands): lock CLI contract to command catalog`; modifies `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py` to lock parser/catalog drift coverage.
- `2f9eb28ca` - `fix(commands): derive cli surface from catalog specs`; modifies `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py` so the live parser consumes catalog-owned command specs.
- `08466cd7f` - `Add command smoke command lines`; modifies `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py` to publish parser-ready smoke command lines.
- `091f508e3` - `Expose MVP command demo path contract`; modifies `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py` to expose demo-path command contract helpers.
- `383c53cee` - `fix(commands): align handoff with smoke command APIs`; modifies `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py` to align public exports and coverage with smoke APIs.
- `60a1c88e7` - `Expose command demo path checkpoints`; modifies `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py` to expose operator checkpoint contract data.
- `5ca4e4533` - `Harden MVP command demo action contract`; modifies `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py` to stabilize action/handoff contract exports.
- `894e6c128e4e2ece1406f4e95f5086b774955905` - `Add MVP demo command lookup contract`; modifies `src/qual/commands/__init__.py` and `src/qual/commands/catalog.py` to add the demo-path lookup contract and public exports.
- `04974e20df08b704f39a065e6082194f9024fd26` - `fix(commands): satisfy branch tip lookup review`; modifies `THREAD.md`, `THREAD_PACKET.md`, and `tests/unit/test_commands_catalog.py`; it records the branch-tip review basis and keeps the public demo-path lookup export regression test in the reviewed diff.
- `e19ff6362a4b6f9cae64810dca7414b1c526ed99` - `fix(commands): clarify branch tip review scope`; modifies `THREAD.md` and `THREAD_PACKET.md` only; it is metadata-only but included in the branch-tip review target.
- `9a476b0ad862d2770f9cd32c549b5a6fa2e33ba5` - `fix(commands): clarify post-f8 branch scope`; modifies `THREAD.md` and `THREAD_PACKET.md` only; it is metadata-only but included in the branch-tip review target.
- This `20260429T135712Z` fixer commit - updates `THREAD.md` and `THREAD_PACKET.md` only; it corrects packet traceability for the full branch-tip review target.

The branch also contains earlier command-catalog, CLI parser, diff-preview, scope-check, test, and packet-maintenance commits reflected by the full `git diff main...codex/feat-commands` file list below. Reviewers should use the full branch-tip diff, not an individual historical packet label, as the merge basis.

## Post-f8 Delta Called Out By Reviewer

The exact `f8d860e..9a476b0` diff that was missing from the prior packet is:

- `THREAD.md`
- `THREAD_PACKET.md`
- `src/qual/cli.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

Shortstat for that comparison: `6 files changed, 937 insertions(+), 139 deletions(-)`.

Implementation/test files changed in that comparison:

- `src/qual/cli.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

Handoff metadata changed in that comparison:

- `THREAD.md`
- `THREAD_PACKET.md`

## Canonical Demo-Path Alignment

Canonical demo-path sequence: `open document`, `retrieve material`, `gather/promote context`, `plan/revise`, `preview/apply/reject patch`, `persist/save`, `continue`.

This slice directly advances `open document`, `retrieve material`, `gather/promote context`, `preview/apply/reject patch`, `persist/save`, and `continue`. It does not claim to implement or directly advance `plan/revise`; it keeps the command surface deterministic around that engine-side step so the CLI-first loop can reach patch review and persistence without parser/catalog disagreement.

Parser/catalog drift was a concrete blocker for the CLI-first Milestone 3 loop because the operator-facing parser, command catalog, smoke command lines, and engine handoff labels could disagree about the same step. If `context-basket`, `diff-preview`/`diff`, or `terminal` parsed differently than the catalog and demo-path exports described them, the demo loop could not reliably retrieve material, promote context into the working set, preview and accept or reject a patch, or persist the handoff from the CLI. That is direct loop breakage, not second-order hardening.

## Scope Completed

1. Made the command catalog the deterministic source for command names, aliases, flow steps, CLI tokens, lookup tables, flow routes, and surface contracts.
   Canonical demo-path step advanced: `retrieve material`, by keeping the retrieval command token `context-basket` stable and discoverable from the catalog.
   Canonical demo-path step advanced: `gather/promote context`, by making the context-basket command contract deterministic for the CLI step that promotes retrieved material into the active working context.
2. Aligned the actual argparse command parser with the catalog-owned CLI token contract, including alias handling for `diff`.
   Canonical demo-path step advanced: `open document`, because the catalog/parser contract keeps the bootstrap/open command path aligned with the command surface.
   Canonical demo-path step advanced: `retrieve material`, because retrieval commands now parse through the same catalog contract used by tests.
   Canonical demo-path step advanced: `preview/apply/reject patch`, because `diff-preview` and its `diff` alias are catalog-owned parser tokens for the patch-review step.
   Canonical demo-path step advanced: `continue`, because terminal export handoff routing stays represented in the parser/catalog surface used by the loop.
3. Added MVP smoke/demo-path exports for command lines, parser argv, operator checkpoints, engine handoffs, and engine actions.
   Canonical demo-path step advanced: `open document`, through exported bootstrap/open smoke command lines.
   Canonical demo-path step advanced: `retrieve material`, through exported retrieval smoke command lines and engine handoff labels.
   Canonical demo-path step advanced: `gather/promote context`, through exported context-basket checkpoints and engine actions.
   Canonical demo-path step advanced: `preview/apply/reject patch`, through exported patch-review command lines plus `preview_patch`, `apply_patch`, and `reject_patch` actions.
   Canonical demo-path step advanced: `persist/save`, through exported terminal/export-handoff command lines and `persist_session` action.
   Canonical demo-path step advanced: `continue`, through exported terminal/export-handoff routing after persistence.
4. Added branch-tip demo-path lookup contract APIs and exports for ordered lookup by flow step, command name, CLI token, engine action, and engine handoff.
   API/export changes: `CommandDemoPathLookupContract`, `command_mvp_demo_path_lookup_contract()`, `command_mvp_demo_path_lookup_table()`, `command_mvp_demo_path_command_lookup_table()`, `command_mvp_demo_path_cli_lookup_table()`, `command_mvp_demo_path_action_lookup_table()`, and `command_mvp_demo_path_handoff_lookup_table()` are public through `src/qual/commands/__init__.py`.
   Canonical demo-path step advanced: `open document`, by keeping the bootstrap/open step addressable in the ordered flow-step and CLI-token lookup surfaces.
   Canonical demo-path step advanced: `retrieve material`, by giving retrieval consumers a stable lookup from flow step, command name, CLI token, engine action, and engine handoff.
   Canonical demo-path step advanced: `gather/promote context`, by giving context-basket promotion a stable command/demo-path lookup record for future CLI and A2UI consumers.
   Canonical demo-path step advanced: `preview/apply/reject patch`, by exposing patch-review actions and handoff labels through validated lookup tables.
   Canonical demo-path step advanced: `persist/save`, by exposing terminal/export-handoff persistence actions and labels through the handoff/action lookup tables.
   Canonical demo-path step advanced: `continue`, by keeping the terminal/export-handoff continuation route stable in the command-name, CLI-token, and handoff lookup surfaces.
5. Added unit coverage for catalog determinism, parser drift detection, smoke command lines, demo-path checkpoints, diff-preview rendering, and public command exports.
   Canonical demo-path step advanced: `retrieve material`, by guarding retrieval command tokens against catalog/parser drift.
   Canonical demo-path step advanced: `gather/promote context`, by testing context-basket visibility in the command contract.
   Canonical demo-path step advanced: `preview/apply/reject patch`, by testing diff-preview rendering and patch-review command exports.
   Canonical demo-path step advanced: `persist/save`, by testing terminal/export-handoff visibility in the command contract.
   Canonical demo-path step advanced: `continue`, by testing the export-handoff route remains in the public command surface.

Scope boundary: this branch validates the current MVP command contract and demo-path command surface. It does not implement new retrieval ranking, provider routing, model configuration, Textual console work, or new `plan/revise` behavior.

## Files Changed

From `git diff --name-status main...HEAD`:

- `THREAD.md`
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `src/qual/cli.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

Implementation files in scope:

- `scripts/scope-check.sh`
- `src/qual/cli.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`

Tests in scope:

- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

Handoff metadata:

- `THREAD.md`
- `THREAD_PACKET.md`

## Ownership And Risk

This is a high-risk branch-tip handoff because the full branch review target includes an earlier approved edit to `src/qual/cli.py`, which is integrator-locked in `THREAD_OWNERSHIP.md`. The current `20260429T135712Z` fixer slice does not newly edit integrator-locked files.

- Lane-owned command paths: `src/qual/commands/**`.
- Earlier full-branch integrator-locked exception: `src/qual/cli.py`, needed so the actual argparse parser consumes the command catalog token contract. Public command-contract impact: no new provider/routing behavior; the public CLI parser surface is bound to catalog-owned tokens and aliases so `context-basket`, `diff-preview`/`diff`, `terminal`, and related demo-path commands parse through the same contract exported by `src/qual/commands`.
- Approved shared-test exception: `tests/unit/test_commands_catalog.py`, retained as the focused command-catalog regression surface.
- Current fixer-slice ownership: handoff metadata only; no new shared-test or integrator-locked implementation edit.
- Scope-check exception behavior: full-window scope checks that include `src/qual/cli.py` require `SCOPE_ALLOW_SHARED=1`; the default recent scope check only validates the current metadata-fix commit.
- Task budget: `4` high-risk tasks completed.
- Budget status: within high-risk task budget; the branch-tip diff exceeds the default packet-only size limits because this review target intentionally includes all implementation commits.

## Roadmap And Vision

- Roadmap: Milestone 3 "Real workflow loop," specifically CLI compatibility for the current MVP command catalog and parser surface.
- Roadmap adjacency: Milestone 5 "YC demo readiness," specifically reproducible demo-path command lines for open, retrieval, patch review, and export handoff.
- Product vision: `Exegesis Engine` remains the engine/runtime and CLI compatibility surface, with structured command contracts consumable by CLI now and the `Exegesis Textual Client` MVP target later.
- Routing/provider impact: none. This branch does not touch model routing or provider configuration.
- Proposed `README.md` patch text: none.

## Commands Run

- Fresh `20260429T135712Z` fixer rerun for the branch-tip traceability review request:
  `make scope-check` passed; `./quality-format.sh --check` passed; `./quality-lint.sh` passed; `./quality-test.sh` passed with smoke tests and `133` unit tests; `./typecheck-test.sh` passed; `make ci` passed with scope-check, format, lint, typecheck, smoke tests, and `133` unit tests.
- Fresh `20260429T134945Z` fixer rerun for the branch-tip traceability review request:
  `make scope-check` passed; `./quality-format.sh --check` passed; `./quality-lint.sh` passed; `./quality-test.sh` passed with smoke tests and `133` unit tests; `./typecheck-test.sh` passed; `make ci` passed with scope-check, format, lint, typecheck, smoke tests, and `133` unit tests.
- Fresh `20260429T134038Z` fixer rerun for the branch-tip traceability review request:
  `make scope-check` passed; `./quality-format.sh --check` passed; `./quality-lint.sh` passed; `./quality-test.sh` passed with smoke tests and `133` unit tests; `./typecheck-test.sh` passed; `make ci` passed with scope-check, format, lint, typecheck, smoke tests, and `133` unit tests.
- Fresh `20260429T133117Z` fixer rerun for the branch-tip lookup-contract review request:
  `make scope-check` passed; `./quality-format.sh --check` passed; `./quality-lint.sh` passed; `./quality-test.sh` passed with smoke tests and `133` unit tests; `./typecheck-test.sh` passed; `make ci` passed with scope-check, format, lint, typecheck, smoke tests, and `133` unit tests.
- Fresh `20260429T131636Z` fixer rerun for offline-review fallback:
  `make scope-check` passed; `./quality-format.sh --check` passed; `./quality-lint.sh` passed; `./quality-test.sh` passed with smoke tests and `132` unit tests; `./typecheck-test.sh` passed; `make ci` passed with scope-check, format, lint, typecheck, smoke tests, and `132` unit tests.
- Fresh `20260429T131018Z` fixer rerun after live parser-surface and ownership-note updates:
  `python -m unittest tests.unit.test_commands_catalog` passed with `50` tests; `make scope-check` passed; `./quality-format.sh --check` passed; `./quality-lint.sh` passed; `./quality-test.sh` passed with smoke tests and `132` unit tests; `./typecheck-test.sh` passed; `make ci` passed with scope-check, format, lint, typecheck, smoke tests, and `132` unit tests.
- Fresh `20260429T130328Z` fixer rerun after canonical demo-path handoff updates:
  `make scope-check` passed; `./quality-format.sh --check` passed; `./quality-lint.sh` passed; `./quality-test.sh` passed with smoke tests and `132` unit tests; `./typecheck-test.sh` passed; `make ci` passed with scope-check, format, lint, typecheck, smoke tests, and `132` unit tests.
- `make scope-check` - passed for branch `codex/feat-commands`.
- `SCOPE_WINDOW=full SCOPE_ALLOW_SHARED=1 make scope-check` - passed for the branch-tip review target with the explicit `src/qual/cli.py` shared-file exception enabled.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed, including smoke tests and `132` unit tests.
- `./typecheck-test.sh` - passed, compiling Python sources in `src/`.
- `make ci` - passed, including scope-check, format, lint, typecheck, smoke tests, and `132` unit tests.
- Prior successful packet evidence: `make scope-check` passed; `./quality-format.sh --check` passed; `./quality-lint.sh` passed; `./quality-test.sh` passed with smoke tests and `132` unit tests; `./typecheck-test.sh` passed; `make ci` passed with scope-check, format, lint, typecheck, smoke tests, and `132` unit tests.
- Prior direct unit evidence: `python -m unittest tests.unit.test_commands_catalog` passed with `50` tests.
- Prior unavailable command: `python -m pytest tests/unit/test_commands_catalog.py` failed because `pytest` is not installed in the active Python.

## Risks And Blockers

- Risk: `src/qual/cli.py` is integrator-locked, so review must include the explicit shared-file exception above.
- Risk: `894e6c128...` expands the public command API/export surface from `src/qual/commands/__init__.py`; this is intentional branch-tip implementation scope and should be reviewed as such.
- Risk: `04974e20...` changes `tests/unit/test_commands_catalog.py` and handoff metadata; this is intentional branch-tip implementation/test scope and should be reviewed as such.
- Risk: this packet deliberately reviews the full branch tip instead of a narrowed implementation commit, so reviewers should ignore earlier packet wording and use the file list above.
- Blockers: none known after gate rerun.

## Final Readiness Statement

This command-catalog slice now makes the canonical `retrieve material` and `gather/promote context` steps more real for the CLI-first Milestone 3 loop, while also locking the adjacent `preview/apply/reject patch`, `persist/save`, and `continue` command handoffs needed to complete that loop from the current CLI surface.
