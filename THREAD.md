# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: final branch tip after the `20260429T183949Z` fixer, including implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, implementation fixer commit `3f180d67ca82eebdce9da411fc2da5356064d46f`, smoke-plan implementation commit `c320dafa67733469fac8c60aa1ec3b54d2ef6c97`, packet/test correction commit `153c1271575ee1ea4256378f560c255254fef2c6a`, parser-drift test correction commit `2aef59c6d4fe888a238bd0b696adf6b4cd720382`, and this required-fix commit.
- Latest fixer correction: keeps `3f180d67ca82eebdce9da411fc2da5356064d46f`, `c320dafa67733469fac8c60aa1ec3b54d2ef6c97`, `153c1271575ee1ea4256378f560c255254fef2c6a`, and `2aef59c6d4fe888a238bd0b696adf6b4cd720382` in scope for reviewer packet `20260429T183949Z`; ties the live argparse parser surface to the command catalog contract; builds top-level CLI commands from catalog tokens; exercises parser-only added, missing, and alias-rename drift through real argparse parser choices; documents the exported MVP command smoke plan; and reports required gate results from the actual branch tip.
- Demo-path mapping: `THREAD_PACKET.md` explicitly maps each numbered task to the CLI fallback steps it advances across `open project/document`, `retrieve relevant material`, `gather context into basket`, `plan/revise`, `apply/reject patch`, `persist state`, and `continue working`.
- Direct demo-path impact: this slice makes `retrieve relevant material` and `gather context into basket` more real by preventing parser/catalog drift for retrieval command discovery and parsing, and makes `open project/document`, `apply/reject patch`, and `persist state` more concrete through catalog-owned smoke argv.
- Roadmap/vision mapping: `Milestone 1: Bootstrap Flow Stabilization`, `Milestone 2: Test Hardening`, MVP `feat-commands`, and the `Operator-first control surface` plus `Retrieval-first context handling` product capabilities.
- Reviewed implementation files: `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
- Branch-tip merge file list: `THREAD.md`, `THREAD_PACKET.md`, `scripts/scope-check.sh`, `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`, `tests/unit/test_commands_catalog.py`, and `tests/unit/test_diff_preview.py`.
- Lane-owned implementation files: `src/qual/commands/__init__.py` and `src/qual/commands/catalog.py`.
- Approved shared-by-approval test file: `tests/unit/test_commands_catalog.py`.
- Integrator-locked implementation edits in reviewed implementation: `src/qual/cli.py`, limited to the reviewer-required parser/catalog validation path.
- Metadata files changed after reviewed implementation target: `THREAD.md` and `THREAD_PACKET.md`; the reviewer-flagged `c320dafa67733469fac8c60aa1ec3b54d2ef6c97`, `153c1271575ee1ea4256378f560c255254fef2c6a`, and `2aef59c6d4fe888a238bd0b696adf6b4cd720382` are not metadata-only because they modify command implementation and/or tests, and all are included as implementation/test scope.
- Scope note: owned command file plus approved shared-by-approval test file, with explicit shared-by-approval/integrator-locked approval required for `src/qual/cli.py`; normal `make scope-check` and normal `make ci` pass at the current branch tip without `SCOPE_ALLOW_SHARED=1`.
