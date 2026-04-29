# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Corrected review target: the full current branch tip containing this packet refresh commit, superseding rejected target `e76d7de06e11109e40237b8b447110043cbe7621` and predecessor `0fb860a1c160321585d711911bfce0c2f2242d07`.
- Merge base used for file accounting: `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`.
- Risk classification: high-risk because `src/qual/cli.py` is shared-by-approval and integrator-locked.
- Explicit approval note: `src/qual/cli.py` remains in scope only for the parser/catalog contract fix and requires integrator approval before merge.
- Tasks completed: branch-truthful review basis, high-risk shared-file accounting, post-`f8d860ed9f6299f0169c4f21321ac5f37c949fd3` implementation/test ledger, and canonical demo-path/gate traceability.
- Demo-path impact: this branch makes `retrieve relevant material` and `gather context into basket` more real by preventing parser/catalog drift for retrieval and `context-basket` CLI fallback commands; it also makes `open document`, `apply/reject patch`, and `persist state` more concrete through catalog-owned MVP smoke argv.
- Roadmap/vision mapping: `Milestone 1: Bootstrap Flow Stabilization`, `Milestone 2: Test Hardening`, active MVP `feat-commands`, `Operator-first control surface`, and `Retrieval-first context handling`.
- Complete branch-tip merge file list: `THREAD.md`, `THREAD_PACKET.md`, `scripts/scope-check.sh`, `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`, `tests/unit/test_commands_catalog.py`, and `tests/unit/test_diff_preview.py`.
- Required gates for the exact full-branch-tip tree submitted for review: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all pass.
