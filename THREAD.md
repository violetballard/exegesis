# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- This branch is not a metadata-only resubmission.
- Reviewer-visible implementation anchor remains `3e0be5cbf94ff74cc192e88c239aebc9fb98982a` (`feat(commands): add trusted surface lookup helpers`).
- The current fixer commit on top of that anchor is a metadata refresh so the handoff packet matches the real live scope.
- Regenerated packet scope is the live `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD` diff, not the earlier narrow-slice claim.
- Files in scope:
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/canonical.py`
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
  - `THREAD.md`
  - `THREAD_PACKET.md`
- The protected canonical demo-path step is `open project/document`.
- AGENTS alignment: this work strengthens the Milestone 3 CLI-first loop by keeping the bootstrap command surface deterministic and explicitly traced to the current branch tip.
