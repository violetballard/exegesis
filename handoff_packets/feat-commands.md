# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: hardened the review-step CLI contract for the canonical `preview and apply or reject a patch` step and exposed default current-MVP workflow aliases so CLI consumers use one stable command-contract surface for the same review/apply-or-reject branch.
- Canonical demo-path step advanced: `preview and apply or reject a patch`
- Demo-path mapping: this slice makes the canonical `preview and apply or reject a patch` step more real by keeping the operator-facing `diff-preview` preview entrypoint stable and by exposing one default current-MVP helper surface for the apply/reject branch of that same review step.
- Concrete blocker removed: parser/catalog drift can no longer silently drop the public `diff-preview` token and leave only the still-resolvable alias `diff`, and downstream callers no longer need to choose between demo-only and MVP-only helper names for the current review/apply-or-reject branch while the CLI fallback remains the active operator path.
- Plan-alignment statement: this is one review-step contract-hardening slice. It does not claim new retrieval, persistence, export, audit-path, or broader workflow behavior.
- Reviewed implementation basis:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
  - `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa` (`feat(commands): expose default workflow aliases`)
- Packet refresh traceability: this resubmission is metadata-only and updates only `handoff_packets/feat-commands.md`, `THREAD_PACKET.md`, and `THREAD.md`.
- Roadmap item(s) affected:
  - `ROADMAP.md` MVP focus active lane: `feat-commands`
  - `ROADMAP.md` Milestone 3 `Define and lock user-facing output contracts`
  - `ROADMAP.md` Milestone 5 CLI fallback exit criterion for the MVP flow
- Vision capability affected:
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`
  - engine-contracts-first alignment while `Exegesis Console` stays deferred
- Routing/provider impact note: none; this slice does not touch model routing, provider configuration, or integrator-locked entrypoints.
- Proposed `README.md` patch text: none.

## Tasks Completed
1. Locked the live review-step parser surface to the command catalog so `diff-preview` drift fails closed.
2. Added parser-surface regressions in [tests/unit/test_commands_catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/tests/unit/test_commands_catalog.py:5584) covering alias-only, missing-token, extra-token, and cache-warm drift cases.
3. Added public default current-MVP workflow aliases and trusted-surface aliases in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py:3509) and [src/qual/commands/__init__.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/__init__.py:145), with tests proving those aliases stay equal to the current MVP contract.
4. Updated [handoff_packets/feat-commands.md](/Users/doctor-violet/.codex/worktrees/5494/qual/handoff_packets/feat-commands.md:1), [THREAD_PACKET.md](/Users/doctor-violet/.codex/worktrees/5494/qual/THREAD_PACKET.md:1), and [THREAD.md](/Users/doctor-violet/.codex/worktrees/5494/qual/THREAD.md:1) so the re-review packet points at the real implementation basis, records the fresh verification traceability, and distinguishes shared-by-approval test scope from integrator-locked scope.

## Files Changed
- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Commands Run With Results
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed
- Verification rerun timestamp: `2026-04-24T08:19:27Z UTC`

## Risks / Blockers
- Risks: future command-surface changes now need to keep `_CLI_ENTRYPOINTS`, the public default current-MVP alias exports, and the shared regression suite aligned.
- Blockers: none.

## Scope-Check / Ownership Note
- Shared-by-approval edit: `tests/unit/test_commands_catalog.py`
- Approval trace: `scripts/scope-check.sh` `is_approved_shared_test()` allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`
- Integrator-locked edits: `none`
