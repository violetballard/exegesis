# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` plus metadata-only packet refresh commits through the final fixer commit.
- Latest fixer correction: restores post-`f8d860ed9f6299f0169c4f21321ac5f37c949fd3` implementation drift in `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`, leaving only packet metadata changes after the reviewed implementation target.
- Demo-path mapping: `THREAD_PACKET.md` explicitly maps the reviewed command-catalog work to CLI contract stability for `open project/document`, `retrieve relevant material`, `gather context into basket`, `plan/revise`, `apply/reject patch`, `persist state`, and `continue working`.
- Direct demo-path impact: this slice makes `retrieve relevant material` more real by preventing parser/catalog drift for retrieval command discovery and parsing.
- Reviewed implementation files: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- Branch-tip merge file list: `THREAD.md`, `THREAD_PACKET.md`, `scripts/scope-check.sh`, `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`, `tests/unit/test_commands_catalog.py`, and `tests/unit/test_diff_preview.py`.
- Lane-owned implementation file: `src/qual/commands/catalog.py`.
- Approved shared-by-approval test file: `tests/unit/test_commands_catalog.py`.
- Integrator-locked implementation edits in reviewed implementation: none.
- Metadata files changed after reviewed implementation target: `THREAD.md` and `THREAD_PACKET.md`.
- Scope note: owned command file plus approved shared-by-approval test file at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; no integrator-locked implementation edits remain after that target.
