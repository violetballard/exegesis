# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: added public helper APIs for the canonical and trusted Milestone 3 apply/reject command branches so callers can request the stable demo-loop token sequence directly instead of reconstructing it from invocation tables.
- Canonical demo-path step advanced: `patch-review -> apply-patch/reject-patch -> persist -> export-handoff`
- Demo-path mapping: this change makes the review/apply-or-reject/persist/export section of the CLI-first MVP loop easier to drive deterministically by exposing the exact canonical branch tokens and the exact trusted surface tokens for either decision path.
- Roadmap item(s) affected: `ROADMAP.md` Milestone 1 `Bootstrap Flow Stabilization` via command-surface hardening, and `ROADMAP.md` Milestone 5 `A2UI Presentation Layer` exit criteria requiring the CLI to execute the MVP flow through patch and export on stable contracts.
- Vision capability affected: `PRODUCT_VISION.md` capability 4 `Operator-first control surface`, specifically keeping the CLI command path deterministic and easy to smoke-test.
- Routing/provider impact note: none; this slice does not touch model routing, provider configuration, or shared entrypoints.
- Proposed `README.md` patch text: none.

## Tasks Completed
1. Added `command_demo_workflow_branch_tokens()` and `command_mvp_workflow_branch_tokens()` in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py:3587) to expose the canonical apply/reject branch token order directly.
2. Added `command_demo_workflow_trusted_tokens()` and `command_mvp_workflow_trusted_tokens()` in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py:3622) to expose the preferred stable command surface for the same branch.
3. Re-exported the new helpers from [src/qual/commands/__init__.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/__init__.py:150) so command consumers can import them from the lane’s public package surface.
4. Added focused regression coverage in [tests/unit/test_commands_catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/tests/unit/test_commands_catalog.py:4027) proving apply/reject aliases normalize to the right canonical branch and trusted token sequence.
5. Ran the required gate suite and scope check.

## Files Changed
- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `tests/unit/test_commands_catalog.py`
- `handoff_packets/feat-commands.md`

## Commands Run With Results
- `python -m unittest tests.unit.test_commands_catalog -q` -> passed (`131` tests)
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed (`214` tests plus smoke)
- `./typecheck-test.sh` -> passed
- `make ci` -> passed

## Risks / Blockers
- Risks: future workflow-branch contract changes now need to keep the new token helpers aligned with the existing invocation-plan helpers and tests; the new coverage is intended to fail fast if they drift.
- Blockers: none.
