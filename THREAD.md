# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Reviewer-visible implementation commits at the current branch tip are:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
  - `1e04f9633c4abc4988dcb991944680b86f94f753` (`Fix command shim subcommand routing`)
  - `5c89ce987fc78ed158d378a988b3e211ce93145d` (`feat(commands): stabilize no-diff diff-preview payload`)
- Review scope for the truthful current tip is:
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
  - `THREAD.md`
  - `THREAD_PACKET.md`
- Canonical demo-path steps advanced by this reviewed slice are the CLI fallback surfaces for:
  - `open project/document` via `bootstrap` / `project-open`
  - `retrieve relevant material` via the routed `context-basket search` surface
  - `preview and apply or reject a patch` via `diff-preview`
- Explicit handoff statement: this slice hardens the existing CLI operator contract for those already-in-scope Milestone 3 steps while Textual remains disabled; it does not claim new workflow breadth beyond the current CLI fallback surface.
- Shared-path approval basis:
  - current `scripts/scope-check.sh` still explicitly allows `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`
  - historical branch approval for `tests/unit/test_diff_preview.py` was recorded in `e00623f0be7934383d64df46fdaec99d9f92f13c`, `8a38d7bde29da3ecfb3da905ff78416034b151b7`, and `9e6b2206d7a37fc28b1233569ed2ac473e61f15a`
- This fixer pass stays metadata-only, limited to `THREAD.md` and `THREAD_PACKET.md`.
