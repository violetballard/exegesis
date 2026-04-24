# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Reviewed implementation basis:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
  - `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa` (`feat(commands): expose default workflow aliases`)
- Packet refresh scope:
  - this refresh is metadata-only
  - it updates `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`
  - required gates reran successfully at `2026-04-24T08:30:03Z`
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/__init__.py`
  - `tests/unit/test_commands_catalog.py`
- Canonical demo-path step advanced:
  - `preview and apply or reject a patch`
- Required AGENTS mapping sentence:
  - this change makes `preview and apply or reject a patch` more real by forcing the review-step public command surface to stay catalog-locked and fail closed before the operator reaches the wrong CLI verb set
- Concrete blocker removed:
  - the parser can no longer silently drop the public `diff-preview` token and leave only the still-resolvable alias `diff`, and callers no longer have to choose between helper names for the same review/apply-or-reject branch
- Scope note:
  - this slice hardens CLI/catalog consistency and default workflow alias exposure only
  - it does not claim new persistence, audit-path, retrieval, patch-apply, export, routing, or UI behavior
- Roadmap / vision alignment:
  - `ROADMAP.md` Milestone 3 `Define and lock user-facing output contracts`, narrowly applied to the CLI review-step command boundary
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`, narrowly applied to the CLI-first review-step contract while Textual remains disabled
- Ownership / approval trace:
  - lane-owned edits: `src/qual/commands/catalog.py`, `src/qual/commands/__init__.py`
  - approved shared-by-approval edit: `tests/unit/test_commands_catalog.py`
  - approval source: `THREAD_OWNERSHIP.md` plus `scripts/scope-check.sh` `is_approved_shared_test()` for `codex/feat-commands*`
  - integrator-locked edits: `none`
