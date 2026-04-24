# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: current branch-tip command-catalog contract hardening plus one shared regression for alias-level parser-surface drift
- Canonical demo-path step advanced: `preview and apply or reject a patch`
- Required mapping statement: this slice strengthens the patch-review step because the `diff-preview` CLI surface now fails fast if the `diff` alias drops or mutates while the canonical command order still looks stable.
- Concrete blocker removed: before this slice, alias-level parser drift could silently change or remove the `diff` entrypoint while `canonical_names` still matched, weakening the deterministic CLI control surface for the patch-review step.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the patch-review CLI surface deterministic by rejecting alias-level parser drift in the command catalog contract.
- Risk reason: this touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Tighten the CLI contract to validate full grouped parser surface, not just canonical command order.
2. Add a regression proving alias-level drift raises even when canonical names stay unchanged.
3. Refresh the handoff packet so it matches the current branch tip, states the shared-test exception explicitly, and maps the work to `preview and apply or reject a patch`.
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
- Verification rerun timestamp: `2026-04-24T12:04:35Z`

## Ownership Note

- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval mechanism: `scripts/scope-check.sh` branch allowlist for `codex/feat-commands*`
- Integrator-locked edits: `none`
- Scope note: the current branch tip contains only the two implementation files above plus the handoff metadata files in this packet.

## Roadmap and Vision Mapping

- `ROADMAP.md` Milestone 1 `Bootstrap Flow Stabilization (In Progress)`: command and `diff-preview` behavior hardening.
- `ROADMAP.md` Milestone 2 `Test Hardening (In Progress)`: focused parser-edge regression coverage.
- `ROADMAP.md` MVP focus lane: `feat-commands`.
- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: the CLI remains a first-class deterministic operator surface.
- `PRODUCT_VISION.md` handoff alignment rule: this packet stays scoped to roadmap- and vision-mapped command-surface hardening only.
