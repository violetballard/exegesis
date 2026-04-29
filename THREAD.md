# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: final branch tip after the `20260429T174006Z` fixer, including implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, implementation fixer commit `3f180d67ca82eebdce9da411fc2da5356064d46f`, and subsequent packet refresh commits.
- Latest fixer correction: keeps `3f180d67ca82eebdce9da411fc2da5356064d46f` in scope for reviewer packet `20260429T174006Z`, ties the live argparse parser surface to the command catalog contract, builds top-level CLI commands from catalog tokens, adds parser-only drift regression coverage, and reports normal gate results from the actual branch tip.
- Demo-path mapping: `THREAD_PACKET.md` explicitly maps the reviewed command-catalog work to CLI contract stability for `open project/document`, `retrieve relevant material`, `gather context into basket`, `plan/revise`, `apply/reject patch`, `persist state`, and `continue working`.
- Direct demo-path impact: this slice makes `retrieve relevant material` and `gather context into basket` more real by preventing parser/catalog drift for retrieval command discovery and parsing.
- Reviewed implementation files: `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
- Branch-tip merge file list: `THREAD.md`, `THREAD_PACKET.md`, `scripts/scope-check.sh`, `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`, `tests/unit/test_commands_catalog.py`, and `tests/unit/test_diff_preview.py`.
- Lane-owned implementation file: `src/qual/commands/catalog.py`.
- Approved shared-by-approval test file: `tests/unit/test_commands_catalog.py`.
- Integrator-locked implementation edits in reviewed implementation: `src/qual/cli.py`, limited to the reviewer-required parser/catalog validation path.
- Metadata files changed after reviewed implementation target: `THREAD.md` and `THREAD_PACKET.md`.
- Scope note: owned command file plus approved shared-by-approval test file, with explicit shared-by-approval/integrator-locked approval required for `src/qual/cli.py`; normal `make scope-check` and normal `make ci` pass at the current branch tip without `SCOPE_ALLOW_SHARED=1`.
