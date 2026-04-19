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
- The canonical demo-path step advanced by this reviewed slice is the CLI fallback `run` entrypoint in the MVP flow `vault -> context -> run -> patch -> export`, concretely through the already-in-scope `project-open` / `bootstrap` command surface.
- Explicit handoff statement: this change makes the canonical demo path more real at the CLI fallback `run` entrypoint by hardening the existing `bootstrap` / `project-open` command contract, keeping that entrypoint deterministic and aligned to the canonical catalog order without expanding the CLI surface.
- Scope-tightening note: this fixer remains CLI contract hardening only for the existing `bootstrap` / `project-open` surface that feeds the MVP `run` step and does not add any new user-facing command breadth beyond the current MVP loop.
- Concrete blocker removed: without validating that the CLI parser entrypoint resolves to the canonical catalog in canonical order, the parser surface feeding the MVP `run` entrypoint through `bootstrap` / `project-open` in the CLI fallback flow could drift silently from the catalog contract and break deterministic smoke tests for that already-in-scope command path.
- Vision capability affected is intentionally narrow: `Canonical engine contract` only.
- This fixer pass stays metadata-only, is limited to `THREAD.md` and `THREAD_PACKET.md`, and has re-run the required gate suite before re-review.
