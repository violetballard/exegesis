# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Corrected review target: the current branch tip after this fixer commit only, with the corrected four-file merge-target list below.
- Integration instruction: review and merge the corrected branch tip only if its merge diff remains exactly `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`; otherwise cherry-pick the final corrective commit target that preserves only that command-catalog slice.
- Rejected packet reconciled: prior traceability incorrectly classified `ab96cb722094e821105d1cdfd3cae24f4b9184ef` as metadata-only. It is implementation because it modifies `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- Implementation commits under review: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, `ab96cb722094e821105d1cdfd3cae24f4b9184ef`, and this final packet-refresh commit.
- Merge base used for file accounting: `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`.
- Risk classification: low-risk lane-owned implementation plus one shared-by-approval unit-test exception and packet metadata; no integrator-locked files are changed in the corrected target.
- Complete corrected file list: `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
- Packet metadata files changed: `THREAD.md` and `THREAD_PACKET.md`.
- Exact canonical demo-path step advanced: preserving the CLI surface for open/retrieve/patch/save loop execution.
- Canonical demo-path steps advanced: command-catalog hardening strengthens the CLI path for `open project/document`, `retrieve relevant material`, and `preview/apply/reject patch` by keeping command tokens and canonical command names deterministic.
- Implementation review basis: the current branch tip after this fixer commit only.
- Implementation slice: `src/qual/commands/catalog.py` and shared-by-approval test exception `tests/unit/test_commands_catalog.py`; this fixer tightens the canonical CLI-token contract, adds the `diff-preview` alias-replacement and alias-before-canonical regressions, and refreshes packet metadata.
- Required gates for the exact corrected target: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all pass.
