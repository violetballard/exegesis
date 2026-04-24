# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Reviewed implementation basis:
  - `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa` (`feat(commands): expose default workflow aliases`)
  - reviewer-requested parser-surface fixes are included in the reviewed ancestry:
    - `dbb8e0156f3520c759d4d29e2cbbb186013f6df7` (`fix(commands): harden parser surface drift checks`)
    - `6890b8c6d81c7700e84b6cbf9402177d0bafab4f` (`test(commands): lock parser drift regressions to live entrypoints`)
    - `bd118a6c0d7693d58882f74efc8066387bc82189` (`test(commands): cover cached parser surface drift`)
- Scope completed: hardened the review-step CLI contract for the canonical `preview and apply or reject a patch` step so the public `diff-preview` entrypoint stays locked to the live parser/catalog surface, then exposed default workflow and trusted-surface alias helpers as thin forwards to the current MVP contract helpers.
- Canonical demo-path step advanced: `preview and apply or reject a patch`
- Required AGENTS sentence: this change makes `preview and apply or reject a patch` more real by forcing the review-step public command surface to stay catalog-locked and fail closed before the operator reaches the wrong CLI verb set.
- Concrete blocker removed: parser/catalog drift can no longer silently drop the public `diff-preview` token and leave only the still-resolvable alias `diff`, which keeps the CLI fallback deterministic at the patch-review step of the current MVP loop.
- Plan-alignment statement: this is one review-step contract-hardening slice inside the current engine-first Milestone 3 loop. It does not claim new retrieval, persistence, export, audit-path, or broader workflow behavior.
- Packet refresh traceability: later `docs(commands)` commits are metadata-only and update only `handoff_packets/feat-commands.md`, `THREAD_PACKET.md`, and `THREAD.md`.
- Roadmap item(s) affected:
  - `ROADMAP.md` MVP focus active lane: `feat-commands`
  - `ROADMAP.md` Milestone 3 current CLI loop `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff`
  - `ROADMAP.md` Milestone 3 `Define and lock user-facing output contracts`
- Vision capability affected:
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`
  - specific requirement advanced: `Engine emits structured outputs that can be consumed by CLI now and Exegesis Console next`, with `the engine contracts come first`
  - no claim against `PRODUCT_VISION.md` capability 3 `Auditable generation`; this diff does not add persistence, audit hooks, or workflow trace records
- Routing/provider impact note: none; this slice does not touch model routing, provider configuration, or integrator-locked entrypoints.
- Proposed `README.md` patch text: none.

## Tasks Completed
1. Locked the live review-step parser surface to the command catalog so `diff-preview` drift fails closed.
2. Added parser-surface regressions in [tests/unit/test_commands_catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/tests/unit/test_commands_catalog.py:5584) covering alias-only, missing-token, extra-token, and cache-warm drift cases.
3. Added thin public alias helpers that forward the default workflow and trusted-surface contract accessors to the current MVP helpers in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py:3511).
4. Updated [handoff_packets/feat-commands.md](/Users/doctor-violet/.codex/worktrees/5494/qual/handoff_packets/feat-commands.md:1), [THREAD_PACKET.md](/Users/doctor-violet/.codex/worktrees/5494/qual/THREAD_PACKET.md:1), and [THREAD.md](/Users/doctor-violet/.codex/worktrees/5494/qual/THREAD.md:1) so the re-review packet points to commit `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa`, states the canonical demo-path step explicitly, and keeps the non-owned test edit labeled as a shared-by-approval exception.

## Files Changed
- `src/qual/commands/catalog.py`
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
- Verification rerun timestamp: `2026-04-24T08:43:00Z UTC`

## Risks / Blockers
- Risks: future command-surface changes now need to keep `_CLI_ENTRYPOINTS`, the shared regression suite, and the default alias-forwarding helpers aligned so the public `diff-preview` review token stays catalog-locked.
- Blockers: none.

## Scope-Check / Ownership Note
- Shared-by-approval edit: `tests/unit/test_commands_catalog.py`
- Approval trace: `THREAD_OWNERSHIP.md` marks the test path as non-owned and `scripts/scope-check.sh` `is_approved_shared_test()` allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`
- Integrator-locked edits: `none`
