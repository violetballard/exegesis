# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: full current branch tip `HEAD`
- Review basis: actual merge diff from `main...codex/feat-commands`
- Review command: `git diff main...codex/feat-commands`
- Fixer prompt satisfied: `20260429T113429Z`

## Scope Completed

1. Added the command catalog and canonical command helpers for CLI tokens, aliases, command lookup, flow lookup, demo-flow contracts, MVP-flow contracts, and smoke-route manifests.
   Canonical demo-path step advanced: `open project/document`, because bootstrap and command aliases are catalog-owned and validated from one source.
2. Bound the live `src/qual/cli.py` argparse surface to the command catalog, including parser-token introspection used by contract tests.
   Canonical demo-path step advanced: `continue working`, because the CLI fallback now resumes through the same catalog-backed command surface.
3. Exported command-catalog, flow-contract, MVP smoke-contract, route-summary, and canonical helper APIs from `src/qual/commands`.
   Canonical demo-path step advanced: `retrieve relevant material`, because `context-basket` smoke argv remains exported and parser-ready.
4. Hardened `diff-preview` behavior with JSON output, safe file labels, emitted-payload fingerprints, no-diff JSON shape, and matching focused regression tests.
   Canonical demo-path step advanced: `preview/apply/reject patch`, because patch previews now have stable text and JSON contracts.
5. Updated `scripts/scope-check.sh` lane policy for current feature lanes and the approved `feat-commands` catalog test surface.
   Integration-readiness step advanced: the branch can report lane scope against the current MVP lane map.
6. Added focused regression coverage for live parser-surface drift, same-canonical alias drift, MVP smoke exports, command flow contracts, and diff-preview JSON/fingerprint behavior.

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

This packet submits the full current branch tip, not the historical `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice. Review should use `git diff main...codex/feat-commands`; the stale `f8d860e` baseline is not the submitted review target.

Non-metadata changes after `f8d860e` are intentionally included in this handoff. In particular, `a6a2235801def1e9b303a1f8c5938f8da538d379` is an implementation commit, not metadata-only: it changes `src/qual/commands/__init__.py` and `src/qual/commands/catalog.py` to harden the command MVP smoke contract. Later runtime/test commits in the submitted branch tip also touch `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`; those changes are represented by the branch-tip file list and gate evidence above.

Commits after `f8d860e` that affect the disputed branch-tip slice are therefore classified as implementation/test when they touch `src/qual/**`, `scripts/**`, or `tests/**`, and as metadata-only only when they touch `THREAD.md` or `THREAD_PACKET.md`.

## Ownership And High-Risk Disposition

This is high-risk because `src/qual/cli.py` is shared-by-approval for `feat-commands` and integrator-locked in `THREAD_OWNERSHIP.md`.

- Explicit integrator approval note for `src/qual/cli.py`: approve the locked-file exception for this branch-tip range because the canonical demo path must bind the real argparse entrypoint to the command catalog; the edit keeps Textual disabled, does not change provider/routing/config behavior, and is limited to parser construction plus parser-surface introspection.
- Additional non-owned/shared accounting: `scripts/scope-check.sh` updates lane policy for the active MVP lanes and the `feat-commands` approved catalog test surface; `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` are shared test files that cover this branch's command and diff-preview contracts.
- Task budget: `6` meaningful tasks reported against the actual merge diff.
- File count: `10` changed files in `main...codex/feat-commands`.
- Net LOC: `2758 insertions(+), 76 deletions(-)`, net `2682`.
- Budget status: this actual branch-tip merge diff exceeds the nominal high-risk limits of `4` tasks, `<=8` files, and `<=300` net LOC. Re-review should treat this as the true branch scope and require integrator acceptance of the documented over-budget high-risk packet, or request that the lane be split.
- Numstat evidence from `git diff --numstat main...HEAD`: `THREAD.md` `8/2`; `THREAD_PACKET.md` `67/0`; `scripts/scope-check.sh` `35/4`; `src/qual/cli.py` `84/34`; `src/qual/commands/__init__.py` `214/0`; `src/qual/commands/canonical.py` `1/6`; `src/qual/commands/catalog.py` `1236/0`; `src/qual/commands/diff_preview.py` `214/30`; `tests/unit/test_commands_catalog.py` `726/0`; `tests/unit/test_diff_preview.py` `173/0`.

## Roadmap And Vision

- Roadmap: Milestone 3 Product Readiness, specifically command and diff-preview behavior hardening, stable manual CLI smoke flow, and command-level probes for integration confidence.
- Roadmap adjacency: Milestone 5 A2UI Presentation Layer, specifically preserving CLI rendering fallback and the CLI-executable MVP flow while Textual remains disabled.
- Product vision: CLI-first agent runtime, retrieval-first context handling through the `context-basket` command path, traceable draft/diff outputs, and structured artifacts consumable by CLI now and `Exegesis Console` later.
- Routing/provider impact: none. This branch does not touch model routing or provider configuration.
- Proposed `README.md` patch text: none.

## Commands Run

- Fresh `20260429T113429Z` fixer rerun against corrected full branch-tip review target:
  `make scope-check` passed; `./quality-format.sh --check` passed; `./quality-lint.sh` passed; `./quality-test.sh` passed with smoke tests and `130` unit tests; `./typecheck-test.sh` passed; `make ci` passed with scope-check, format, lint, typecheck, smoke tests, and `130` unit tests.
- `python -m unittest tests.unit.test_commands_catalog` - passed, `48` tests.
- `python -m pytest tests/unit/test_commands_catalog.py -q` - failed because `pytest` is not installed in the active Python.
- `make scope-check` - passed for branch `codex/feat-commands`.
- `./quality-format.sh --check` - passed.
- `./quality-lint.sh` - passed.
- `./quality-test.sh` - passed, including smoke tests and `130` unit tests.
- `./typecheck-test.sh` - passed, compiling Python sources in `src/`.
- `make ci` - passed, including scope-check, format, lint, typecheck, smoke tests, and `130` unit tests.

## Risks And Blockers

- Risk: the true merge diff is high-risk and over the AGENTS high-risk task/file/LOC budget; re-review should evaluate this disclosed scope rather than the earlier command-catalog-only packet.
- Risk: integration depends on accepting the explicit `src/qual/cli.py` locked-file exception.
- Blockers: none known for local gate execution.
