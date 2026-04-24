# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: current branch-tip Milestone 3 CLI compatibility safeguard for the engine-first demo loop plus one shared regression for alias-level parser-surface drift
- Canonical demo-path steps advanced: `open project/document`, `promote or gather context into the basket`, and `preview and apply or reject a patch`
- Required mapping statement: this slice strengthens the active CLI demo loop by specifically making `preview and apply or reject a patch` more reliable, with `open project/document` and `promote or gather context into the basket` included only as the surrounding CLI-first Milestone 3 path that feeds the patch-review step, because the `diff-preview` CLI surface now fails fast if the `diff` alias drops or mutates while the canonical command order still looks stable.
- Concrete blocker removed: before this slice, alias-level parser drift could silently change or remove the `diff` entrypoint while `canonical_names` still matched, weakening the deterministic CLI control surface for the patch-review step.
- Traceability note: reviewed implementation commit is `ebe78557`; prior metadata refresh `e1d22341` changed only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` before this branch-tip packet refresh.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the Milestone 3 CLI compatibility surface deterministic by rejecting alias-level parser drift in the command catalog contract that protects the engine-first demo loop.
- Risk reason: this touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Tighten the CLI contract to validate full grouped parser surface, not just canonical command order.
2. Add a regression proving alias-level drift raises even when canonical names stay unchanged.
3. Refresh the handoff packet so it matches the current branch tip, states the shared-test exception explicitly, and maps the work to the concrete Milestone 3 CLI demo-path steps it protects.
4. Re-run the required gates and record the results.

## Review Basis

- Implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `handoff_packets/feat-commands.md`

## Commands Run and Outcomes

- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_mutated_diff_alias_with_stable_canonical_names`: `PASSED`
- `make scope-check`: `PASSED`
- `./quality-format.sh --check`: `PASSED`
- `./quality-lint.sh`: `PASSED`
- `./quality-test.sh`: `PASSED`
- `./typecheck-test.sh`: `PASSED`
- `make ci`: `PASSED`
- Verification rerun timestamp: `2026-04-24T12:17:02Z`

## Ownership Note

- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval mechanism: `scripts/scope-check.sh` branch allowlist for `codex/feat-commands*`
- Integrator-locked edits: `none`
- Scope note: the current branch tip contains only the two implementation files above plus the handoff metadata files in this packet.
- Packet-refresh accounting note: metadata-only refresh commit `e1d22341` changed `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`; those files are intentionally part of the branch-level handoff record.

## Roadmap and Vision Mapping

- `ROADMAP.md` Milestone 3 `Real workflow loop`: this change is a CLI compatibility safeguard for the engine-first MVP loop while Textual remains disabled, making the `diff-preview` patch-review entrypoint deterministic and drift-resistant.
- `ROADMAP.md` canonical demo path steps: the direct operator-visible gain is `preview and apply or reject a patch`, while `open project/document` and `promote or gather context into the basket` stay relevant only as the surrounding CLI-first loop that must still arrive at a trustworthy `diff-preview` step; alias-level parser drift on `diff` now fails fast instead of silently weakening that patch-review surface.
- `ROADMAP.md` active lane mapping: `feat-commands` owns CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract`: the CLI compatibility surface stays stable for the future client while Textual remains disabled.
- `PRODUCT_VISION.md` near-term product truth: the CLI remains the active operator surface until UI lanes are enabled, so guarding the `diff-preview` patch-review entrypoint removes a concrete blocker on that active path.
