# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Reviewed implementation basis:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
  - `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa` (`feat(commands): expose default workflow aliases`)
- Scope completed: hardened the review-step CLI contract for the canonical `preview and apply or reject a patch` step and exposed default workflow aliases so CLI consumers use one stable command-contract surface for that same review/apply-or-reject branch.
- Canonical demo-path step advanced: `preview and apply or reject a patch`
- Required AGENTS sentence: this change makes `preview and apply or reject a patch` more real by forcing the review-step public command surface to stay catalog-locked and fail closed before the operator reaches the wrong CLI verb set.
- Concrete blocker removed: parser/catalog drift can no longer silently drop the public `diff-preview` token and leave only the still-resolvable alias `diff`, and downstream callers no longer need to choose between helper names for the same review/apply-or-reject branch.
- Plan-alignment statement: this is one review-step contract-hardening slice. It does not claim new retrieval, persistence, export, audit-path, or broader workflow behavior.
- Roadmap item(s) affected:
  - `ROADMAP.md` Milestone 3 `Define and lock user-facing output contracts`, narrowly applied to the CLI review-step command boundary for `preview and apply or reject a patch`
- Vision capability affected:
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`, narrowly applied to the CLI-first review-step command contract while Textual remains disabled
- Routing/provider impact note: none; this slice does not touch model routing, provider configuration, or integrator-locked entrypoints.
- Proposed `README.md` patch text: none.

## Tasks Completed
1. Locked the live review-step parser surface to the command catalog so `diff-preview` drift fails closed.
2. Added parser-surface regressions in [tests/unit/test_commands_catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/tests/unit/test_commands_catalog.py:5584) covering alias-only, missing-token, extra-token, and cache-warm drift cases.
3. Added default workflow aliases and trusted-surface aliases in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py:3509) and [src/qual/commands/__init__.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/__init__.py:145), with tests proving those aliases stay equal to the reviewed contract.
4. Updated [handoff_packets/feat-commands.md](/Users/doctor-violet/.codex/worktrees/5494/qual/handoff_packets/feat-commands.md:1), [THREAD_PACKET.md](/Users/doctor-violet/.codex/worktrees/5494/qual/THREAD_PACKET.md:1), and [THREAD.md](/Users/doctor-violet/.codex/worktrees/5494/qual/THREAD.md:1) so the re-review packet points at the real implementation basis, records the approval trace explicitly, and keeps the roadmap and vision mapping narrow.

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
- Verification rerun timestamp: `2026-04-24T08:30:03Z`

## Risks / Blockers
- Risks: future command-surface changes now need to keep `_CLI_ENTRYPOINTS`, the default alias exports, and the shared regression suite aligned.
- Blockers: none.

## Scope-Check / Ownership Note
- Shared-by-approval edit: `tests/unit/test_commands_catalog.py`
- Shared-by-approval approval source: `THREAD_OWNERSHIP.md` marks non-owned paths as approval-only, and `scripts/scope-check.sh` `is_approved_shared_test()` allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`
- Integrator-locked edits: none
