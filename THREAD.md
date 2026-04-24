# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: Milestone 3 CLI compatibility safeguard for the engine-first demo loop, plus one shared regression covering alias-level parser drift in the patch-review command surface
- Canonical demo-path steps advanced: `open project/document`, `promote or gather context into the basket`, and `preview and apply or reject a patch`
- Explicit re-review statement: the current branch tip is the review target, and this slice keeps the active CLI loop trustworthy by specifically hardening `preview and apply or reject a patch`, with `open project/document` and `promote or gather context into the basket` remaining in scope only as the surrounding CLI-first Milestone 3 loop that leads into that patch-review step.
- Concrete blocker removed: alias-level parser drift can no longer quietly drop or mutate `diff` while the canonical command sequence still appears unchanged.
- Traceability note: reviewed implementation remains `ebe78557`, and the prior metadata refresh `e1d22341` updated only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` before this branch-tip packet refresh.
- Canonical roadmap/vision mapping: `ROADMAP.md` Milestone 3 `Real workflow loop` plus `PRODUCT_VISION.md` capability 3 `Canonical engine contract`, because the CLI remains the active operator surface while Textual is disabled.
- Latest verification rerun: `2026-04-24T12:17:42Z`

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Required Gates

- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_mutated_diff_alias_with_stable_canonical_names`
- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
