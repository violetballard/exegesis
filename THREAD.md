# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Reviewer Fix Alignment

- Re-review is anchored to the live branch tip `07bec2928350f3e1a69d9f93a05b2f431e94ee4b`, not the stale `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice.
- The implementation range currently being handed off is `eda0197b..07bec292`, which is the unreviewed `feat-commands` work after the previously consumed `feat-commands` merge.
- In-scope implementation files are:
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/canonical.py`
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- This fixer pass is packet-only. It does not change command implementation; it corrects traceability, scope, and gate reporting for the current tree.
- The explicit canonical demo-path step for re-review is `open project/document`: the packet now states that the `bootstrap` parser surface must fail fast on catalog drift so the CLI loop keeps a stable starting point.
- The reviewer-observed import failure does not reproduce on this worktree: `python -m unittest tests.unit.test_commands_catalog -q` passes at the current branch tip.
- The required gates were rerun against the exact tree being handed off on `2026-04-18`, and `THREAD_PACKET.md` records those results as the source of truth.
