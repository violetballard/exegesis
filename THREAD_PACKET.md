# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: full branch tip of `codex/feat-commands`
- Review basis: `git diff main...codex/feat-commands`
- Pre-fixer branch-tip SHA before this fixer pass: `fc6e67941`
- Fixer prompt satisfied: `20260429T131636Z`

This packet supersedes all earlier packets and packet-refresh notes. No commit in the reviewed range is described as metadata-only; implementation and handoff edits are part of the branch-tip review target.

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
4. Added unit coverage for catalog determinism, parser drift detection, smoke command lines, demo-path checkpoints, diff-preview rendering, and public command exports.
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

This is a high-risk branch-tip handoff because the full branch review target includes an earlier approved edit to `src/qual/cli.py`, which is integrator-locked in `THREAD_OWNERSHIP.md`. The current `20260429T131018Z` fixer slice does not newly edit integrator-locked files.

- Lane-owned command paths: `src/qual/commands/**`.
- Earlier full-branch integrator-locked exception: `src/qual/cli.py`, needed so the actual argparse parser consumes the command catalog token contract.
- Approved shared-test exception: `tests/unit/test_commands_catalog.py`, retained as the focused command-catalog regression surface.
- Current fixer-slice ownership: handoff metadata only; no new integrator-locked implementation edit.
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
- Risk: this packet deliberately reviews the full branch tip instead of a narrowed implementation commit, so reviewers should ignore earlier packet wording and use the file list above.
- Blockers: none known after gate rerun.

## Final Readiness Statement

This command-catalog slice now makes the canonical `retrieve material` and `gather/promote context` steps more real for the CLI-first Milestone 3 loop, while also locking the adjacent `preview/apply/reject patch`, `persist/save`, and `continue` command handoffs needed to complete that loop from the current CLI surface.
