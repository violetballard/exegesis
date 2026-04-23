# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Reviewer-visible implementation anchors are:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
  - `1e04f9633c4abc4988dcb991944680b86f94f753` (`Fix command shim subcommand routing`)
- Intermediate handoff-refresh commits between those implementation anchors are metadata-only for this re-review.
- Review scope stays narrow:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
  - `THREAD.md`
  - `THREAD_PACKET.md`
- The canonical demo-path step advanced by this reviewed slice is the CLI fallback early-path in the Milestone exit criterion `vault -> context -> run -> patch -> export`, specifically the existing `bootstrap` / `project-open` entrypoints that keep the operator on the CLI path while Textual remains disabled.
- Explicit handoff statement: this change makes the canonical demo path more real for `A2UI contracts with CLI fallback` by hardening the existing CLI operator surface at the `vault` / `context` side of the loop and preserving the deterministic handoff into `run`, without claiming progress on later `patch` or `export` steps.
- Scope-tightening note: this fixer remains CLI contract hardening only for the existing `bootstrap` / `project-open` and routed retrieval command surfaces that keep the `vault -> context -> run` portion of the MVP loop reachable; it does not add new user-facing command breadth or imply broader workflow progress beyond that path.
- Concrete blockers removed:
- without validating that the CLI parser entrypoint resolves to the canonical catalog in canonical order, the `bootstrap` / `project-open` surface that carries the operator through the `vault` step and into `context`/`run` in the CLI fallback flow could drift silently from the catalog contract and break deterministic smoke tests for that already-in-scope path
- without preserving explicit subcommands when a flow-step shim resolves through the retrieval surface, the CLI fallback `context` step could silently collapse `search` back to the default list behavior instead of preserving the intended routed action
- Vision capability affected is intentionally narrow: `Canonical engine contract` only.
- This fixer pass stays metadata-only, is limited to `THREAD.md` and `THREAD_PACKET.md`, and re-ran `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on `2026-04-23` before re-review.
