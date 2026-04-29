# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: full branch tip of `codex/feat-commands` only
- Review basis: `git diff main...codex/feat-commands`
- Review command: `git diff main...codex/feat-commands`
- Prior packet supersession: this `THREAD_PACKET.md` replaces all earlier packet text, packet-refresh notes, and review-scope claims that named `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` as the submitted target.
- Fixer prompt satisfied: `20260429T122037Z`

## Required-Fix Resolution

1. Review basis is the full branch tip only: `git diff main...codex/feat-commands`. There is no alternate narrow review target in this packet.
2. The narrow `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice is not submitted for review; its earlier packet text is superseded.
3. This is intentionally submitted as high-risk over-budget work with all branch-tip files, task count, LOC count, shared/locked exceptions, and an explicit integrator acceptance requirement below. If integrator does not accept that exception, this handoff must be split before integration.
4. Each completed task below maps to a canonical demo-path step, and the handoff states which CLI-first demo steps are now more real.
5. Ownership accounting distinguishes the locked implementation file, shared policy script, shared tests, owned command files, and metadata files.

## Demo-Path Mapping

Canonical demo-path step advanced: preserving the command surface that keeps `open project/document`, `retrieve/context basket`, `preview/apply/reject patch`, and continuation reachable through the CLI-first MVP loop while Textual remains disabled. This is first-order under the current Milestone 3 narrowing because the MVP demo path is executed through the CLI fallback and command catalog now; it is not deferred Console work or second-order A2UI preparation.

## Scope Completed

1. Added the command catalog and canonical command helpers for CLI tokens, aliases, command lookup, flow lookup, demo-flow contracts, MVP-flow contracts, and smoke-route manifests.
   Canonical demo-path step advanced: `open project/document`, because bootstrap and command aliases are catalog-owned and validated from one source.
2. Bound the live `src/qual/cli.py` argparse surface to the command catalog, with parser construction and `command_cli_contract()` now sharing the catalog-owned `CommandSpec.cli_tokens` source and validating the real argparse choices.
   Canonical demo-path step advanced: `continue working`, because the CLI fallback now resumes through the same catalog-backed command surface.
3. Exported command-catalog, flow-contract, MVP smoke-contract, MVP smoke command-line, demo-path, route-summary, and canonical helper APIs from `src/qual/commands`.
   Canonical demo-path step advanced: `retrieve relevant material`, because `context-basket` smoke argv remains exported and parser-ready.
4. Added the public command-line/demo-path contract for the MVP smoke path, including command lines, operator checkpoints, and engine handoff labels for `open project/document`, `retrieve relevant material`, `preview and accept or reject patch`, and `persist and continue through export handoff`.
   Canonical demo-path step advanced: `retrieve relevant material`, because `context-basket list` is now part of the exported smoke command-line API and is covered through `command_mvp_smoke_command_lines()`.
5. Hardened `diff-preview` behavior with JSON output, safe file labels, emitted-payload fingerprints, no-diff JSON shape, and matching focused regression tests.
   Canonical demo-path step advanced: `preview/apply/reject patch`, because patch previews now have stable text and JSON contracts.
6. Updated `scripts/scope-check.sh` lane policy for current feature lanes and the approved `feat-commands` catalog test surface.
   Integration-readiness step advanced: the branch can report lane scope against the current MVP lane map.
7. Added focused regression coverage for live parser-surface drift in both directions, duplicate CLI entrypoint rejection, MVP smoke command-line exports, MVP demo-path engine handoff exports, command flow contracts, and diff-preview JSON/fingerprint behavior.

Fixer-required demo-path narrowing statement: this correction advances the CLI-first MVP loop by keeping `open project/document`, `retrieve/context basket`, `preview/apply/reject patch`, and `continue working` reachable from the actual argparse surface, not only from a duplicate catalog-side tuple.

## Files Changed

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

Implementation files in scope: `scripts/scope-check.sh`, `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`.
Tests in scope: `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`.
Handoff metadata: `THREAD.md`, `THREAD_PACKET.md`.

## Implementation Commit Traceability

This packet submits exactly one review target: the full branch tip of `codex/feat-commands`. Review should use `git diff main...codex/feat-commands`; do not use the historical `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice or any earlier packet-refresh wording as the review basis.

Non-metadata changes after `f8d860e` are intentionally included in this handoff. In particular, `08466cd7f8d48592c6f6585dd816e4478c102e47` is an implementation commit, not metadata-only: it changes `src/qual/commands/__init__.py` and `src/qual/commands/catalog.py` to export and populate the command MVP smoke command-line API. `091f508e3535b4fdc5d814aa89d68e766e3166c1` is also implementation scope: it changes `src/qual/commands/__init__.py` and `src/qual/commands/catalog.py` to expose the MVP demo-path contract, command lines, and engine handoff labels. The current fixer commit adds focused public-export coverage in `tests/unit/test_commands_catalog.py`. Later runtime/test commits in the submitted branch tip also touch `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`; those changes are represented by the branch-tip file list and gate evidence above.

Commits after `f8d860e` that affect the disputed branch-tip slice are therefore classified as implementation/test when they touch `src/qual/**`, `scripts/**`, or `tests/**`, and as metadata-only only when they touch `THREAD.md` or `THREAD_PACKET.md`.

Test coverage for the exported command-line/demo-path API: `tests/unit/test_commands_catalog.py::CommandCatalogTests.test_public_mvp_smoke_exports_track_the_demo_path` asserts `command_mvp_smoke_command_lines()` through the package export, including `context-basket list`; `test_public_mvp_demo_path_exports_document_engine_handoffs` asserts the package-exported demo-path steps, command lines, and engine handoff labels.

## Ownership And High-Risk Disposition

This is high-risk because `src/qual/cli.py` is shared-by-approval for `feat-commands` and integrator-locked in `THREAD_OWNERSHIP.md`.

- Explicit integrator acceptance required for over-budget high-risk scope: this packet cannot satisfy AGENTS high-risk limits by metadata alone because the true branch-tip diff is `7` tasks, `10` files, and more than `300` net LOC. Integrator must either accept this specific over-budget branch-tip packet before merge or request a split; reviewer should treat absence of that acceptance as a remaining integration blocker, not as an alternate review target.
- Explicit integrator approval note for `src/qual/cli.py`: approve the locked-file exception for this branch-tip range because the canonical demo path must bind the real argparse entrypoint to the command catalog; the edit keeps Textual disabled, does not change provider/routing/config behavior, and is limited to parser construction plus parser-surface introspection.
- Additional non-owned/shared accounting: `scripts/scope-check.sh` updates lane policy for the active MVP lanes and the `feat-commands` approved catalog test surface; `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` are shared test files that cover this branch's command and diff-preview contracts.
- Task budget: `7` meaningful tasks reported against the actual merge diff.
- File count: `10` changed files in `main...codex/feat-commands`.
- Net LOC: `2990 insertions(+), 76 deletions(-)`, net `2914`.
- Budget status: this actual branch-tip merge diff exceeds the nominal high-risk limits of `4` tasks, `<=8` files, and `<=300` net LOC. Re-review should treat this as the true branch scope and require integrator acceptance of the documented over-budget high-risk packet, or request that the lane be split.
- Numstat evidence from `git diff --numstat $(git merge-base main HEAD)`: `THREAD.md` `8/2`; `THREAD_PACKET.md` `106/0`; `scripts/scope-check.sh` `35/4`; `src/qual/cli.py` `84/34`; `src/qual/commands/__init__.py` `228/0`; `src/qual/commands/canonical.py` `1/6`; `src/qual/commands/catalog.py` `1351/0`; `src/qual/commands/diff_preview.py` `214/30`; `tests/unit/test_commands_catalog.py` `790/0`; `tests/unit/test_diff_preview.py` `173/0`.

## Roadmap And Vision

- Roadmap: Milestone 3 "Real workflow loop," specifically preserving CLI compatibility and migration-safe entrypoints for the engine-first MVP loop while Textual remains disabled.
- Roadmap adjacency: Milestone 5 "YC demo readiness," specifically keeping one reproducible retrieve -> basket -> plan/revise -> apply/reject path executable through the current CLI surface.
- Product vision: `Exegesis Engine` remains the engine/runtime and CLI compatibility surface, with structured outputs and command paths kept consumable by CLI now and the `Exegesis Textual Client` MVP target later.
- Routing/provider impact: none. This branch does not touch model routing or provider configuration.
- Proposed `README.md` patch text: none.

## Commands Run

- Fresh `20260429T122037Z` fixer rerun against corrected full branch-tip review target and current roadmap/product labels:
  `make scope-check` passed; `./quality-format.sh --check` passed; `./quality-lint.sh` passed; `./quality-test.sh` passed with smoke tests and `132` unit tests; `./typecheck-test.sh` passed; `make ci` passed with scope-check, format, lint, typecheck, smoke tests, and `132` unit tests.
- `python -m unittest tests.unit.test_commands_catalog` - passed, `50` tests.
- `python -m pytest tests/unit/test_commands_catalog.py` - failed because `pytest` is not installed in the active Python.
- `make scope-check` - passed for branch `codex/feat-commands`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed, including smoke tests and `132` unit tests.
- `./typecheck-test.sh` - passed, compiling Python sources in `src/`.
- `make ci` - passed, including scope-check, format, lint, typecheck, smoke tests, and `132` unit tests.

## Risks And Blockers

- Risk: the true merge diff is high-risk and over the AGENTS high-risk task/file/LOC budget; re-review should evaluate this disclosed scope rather than the earlier command-catalog-only packet. Integration still requires either explicit integrator acceptance of this over-budget packet or a branch split.
- Risk: integration depends on accepting the explicit `src/qual/cli.py` locked-file exception.
- Blockers: none known for local gate execution.
