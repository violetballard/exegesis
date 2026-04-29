# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: final fixer commit range through the `20260429T091158Z` fixer commit
- Review basis: `HEAD~9..HEAD` after this fixer commit
- Scope: command CLI contract hardening for the current Engine-first MVP focus without starting `feat-console`
- Current fixer pass: reconcile the review basis to include the code-changing `e9705f5` parser-binding commit, keep shared CLI ownership accounting explicit, and rerun required gates against the final review basis.

## Fixer Prompt `20260429T083033Z` Fix Satisfaction

1. `THREAD_PACKET.md` uses one clear final fixer review basis: `HEAD~7..HEAD` after the `20260429T085733Z` fixer commit.
2. The packet lists and classifies every file changed by that review basis, including implementation, tests, and handoff metadata.
3. The implementation verifies the real argparse parser surface through `src.qual.cli.command_parser_lookup_table()`, not catalog-internal tables alone.
4. The packet records `src/qual/cli.py` as a shared-by-approval and integrator-locked parser-surface edit required by the reviewer fix.
5. The packet names the canonical demo-path steps strengthened by the work: `project-open`, `retrieval`, `patch-review`, and `export-handoff`.

## Fixer Prompt `20260429T084441Z` Fix Satisfaction

1. Required gates were rerun directly in this worktree and now pass without fallback allowances: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
2. `THREAD_PACKET.md` records the passing gate results for re-review, including `184` passing unit tests plus smoke tests through `./quality-test.sh`.

## Fixer Prompt `20260429T085016Z`, `20260429T085633Z`, And `20260429T085733Z` Fix Satisfaction

1. The authoritative review basis is the final fixer range `HEAD~7..HEAD`, which includes the parser implementation, parser-surface tests, packet corrections, current gate evidence, and this basis reconciliation.
2. Parser-surface drift coverage now patches the actual `_build_parser()` argparse choices, so same-canonical token replacement, removal, substitution, and reordering are proven against accepted parser tokens.
3. Runtime/test edits after `f8d860e` are included in that basis and are not described as metadata-only.
4. Ownership accounting stays tied to that exact basis: `src/qual/commands/catalog.py` is lane-owned, `src/qual/cli.py` is shared-by-approval and integrator-locked, and `tests/unit/test_commands_catalog.py` is command-contract unit coverage.
5. The packet explicitly names the canonical demo-path steps made more real: `project-open`, `retrieval`, `patch-review`, and `export-handoff`.

## Fixer Prompt `20260429T090331Z` Fix Satisfaction

1. `src/qual/cli.py` now exposes raw `command_parser_tokens()` from the actual argparse subparser choices, and `src/qual/commands/catalog.py` compares those raw choices exactly to the catalog CLI tokens.
2. `tests/unit/test_commands_catalog.py` includes direct `_build_parser()` argparse-choice drift coverage for `open` replacing `bootstrap`, `diff` removal, `diff_preview` substitution, added `diff_preview`, and parser token reordering.
3. `THREAD_PACKET.md` maps each completed task to canonical demo-path steps and distinguishes `tests/unit/test_commands_catalog.py` as shared-by-approval test coverage from `src/qual/cli.py` as the approved integrator-locked parser entrypoint edit.

## Fixer Prompt `20260429T091158Z` Fix Satisfaction

1. `THREAD_PACKET.md` now uses the final review basis `HEAD~9..HEAD` after this fixer commit and explicitly includes `e9705f5` as a code-changing parser-binding commit, not metadata-only work.
2. The reviewed files and ownership accounting include `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
3. The intended fix remains the branch-tip parser binding: `command_cli_contract()` validates the live argparse token surface through `command_parser_tokens()` and `command_parser_lookup_table()`.
