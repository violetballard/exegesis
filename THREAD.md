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
- The canonical demo-path mapping for this reviewed slice is the current engine-first CLI path to `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and `continue working`, with this command-catalog hardening specifically stabilizing the command entrypoints that start and traverse that loop.
- Explicit handoff statement: this change makes the canonical demo path more real by keeping the CLI-first operator surface deterministic for the `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and `continue working` steps, and it does not claim broader retrieval-engine, patch-application, persistence, or UI progress.
- Scope-tightening note: this fixer remains command-contract hardening only and does not add any new user-facing command breadth beyond the current MVP loop.
- Concrete blocker removed: without validating that CLI parser entrypoints resolve to the canonical catalog in canonical order, the parser surface feeding the engine-first CLI loop could drift silently from the catalog contract and break deterministic smoke tests for the workflow entrypoints used to open, retrieve, patch-review, and continue.
- Vision capability affected is intentionally narrow: `Canonical engine contract` only.
- This fixer pass stays metadata-only and is limited to `THREAD.md` and `THREAD_PACKET.md`.
