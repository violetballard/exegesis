# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Corrected review target: the current branch tip after this fixer commit only, with the corrected four-file target listed below.
- Integration instruction: review and merge the corrected branch tip only if its merge diff remains exactly `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`; otherwise cherry-pick the final corrective commit target that preserves only that command-catalog slice.
- Rejected packet reconciled: `f5a35438c2808b247cb70a86da7e0e9b19f82f67` incorrectly described a full branch-tip review basis and modified both `THREAD.md` and `THREAD_PACKET.md`.
- Merge base used for file accounting: `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`.
- Risk classification: low-risk lane-owned implementation plus one shared-by-approval unit-test exception and packet metadata; no integrator-locked files are changed in the corrected target.
- Complete corrected file list: `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
- Metadata-only handoff files changed: `THREAD.md` and `THREAD_PACKET.md`.
- Canonical demo-path step advanced: command-catalog hardening strengthens the CLI path for `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch` by keeping command tokens and canonical command names deterministic.
- Implementation review basis: the current branch tip after this fixer commit only.
- Implementation slice: `src/qual/commands/catalog.py` and shared-by-approval test exception `tests/unit/test_commands_catalog.py`; this fixer tightens the canonical CLI-token contract, adds the `diff-preview` alias-replacement regression, and refreshes packet metadata.
- Required gates for the exact corrected target: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all pass.
