# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Reviewer-visible implementation anchor remains `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`).
- Later handoff-refresh commits are metadata-only for this re-review.
- Review scope stays narrow:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
  - `THREAD.md`
  - `THREAD_PACKET.md`
- The canonical demo-path step advanced is `open project/document`, using the exact current MVP path wording from `AGENTS.md` and `ROADMAP.md`.
- Explicit handoff statement: this change hardens the deterministic CLI contract for the `open project/document` bootstrap step and does not claim broader workflow, retrieval, patch, or UI progress.
- Scope-tightening note: this fixer remains command-contract hardening only and does not add any new user-facing command breadth beyond the current MVP loop.
- Concrete blocker removed: without validating that CLI parser entrypoints resolve to the canonical catalog in canonical order, the `bootstrap` entrypoint for `open project/document` could drift silently from the catalog contract and break deterministic CLI smoke tests for that step.
- Vision capability affected is intentionally narrow: `Canonical engine contract` only.
- This fixer pass stays metadata-only and is limited to `THREAD.md` and `THREAD_PACKET.md`.
