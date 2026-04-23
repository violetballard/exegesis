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
- Canonical demo-path steps advanced by this reviewed slice are the current CLI fallback surfaces for:
  - `open project/document` via `bootstrap` / `project-open`
  - `retrieve relevant material` via the routed `context-basket search` surface
  - `preview and apply or reject a patch` via `diff-preview`
- Concrete blocker removed from the CLI-first MVP loop: the operator could complete step 1 (`open project/document`) yet still hit non-deterministic command resolution in step 2 (`retrieve relevant material`) or lose review-state fidelity in step 3 (`preview and apply or reject a patch`) before A2UI/Textual was involved; this slice makes those failures deterministic and test-covered instead.
- Explicit handoff statement: this slice makes step 2 (`retrieve relevant material`) and step 3 (`preview and apply or reject a patch`) materially more real by locking the command contract that step 1 feeds into, preserving routed retrieval subcommands, and preserving no-diff preview state on the current CLI fallback path while Textual remains disabled.
- Shared-path approval basis:
  - current `scripts/scope-check.sh` still explicitly allows `tests/unit/test_commands_catalog.py` only for `codex/feat-commands*`
  - approver / policy author: `Violet Ballard`
  - approval date: `2026-03-28`
  - traceable approval source for `tests/unit/test_commands_catalog.py`: `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50` added that allowlist entry in `scripts/scope-check.sh`, and `c3a66bb580772d65201a630d673a8de1d4a63776` preserved it while tightening the packet text
  - historical branch approval for `tests/unit/test_diff_preview.py` was recorded in `e00623f0be7934383d64df46fdaec99d9f92f13c`, `8a38d7bde29da3ecfb3da905ff78416034b151b7`, and `9e6b2206d7a37fc28b1233569ed2ac473e61f15a`
- This fixer pass stays metadata-only, limited to `THREAD.md` and `THREAD_PACKET.md`, and the required gate sequence passed on `2026-04-23`.
- Fresh verification note for this follow-up fixer pass: the branch was revalidated from clean `HEAD` `233a0c1c8bb848cc904d8831d13740e0589ef6e5` on `2026-04-23` before issuing the next metadata-only refresh commit.
