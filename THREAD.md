# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Corrected review target: the branch tip produced by this fixer pass, with the corrected four-file merge-target list below.
- Integration instruction: review and merge the corrected branch tip only if its merge diff remains exactly `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`; otherwise cherry-pick the final corrective commit target that preserves only that command-catalog slice.
- Rejected packet reconciled: prior traceability incorrectly classified `ab96cb722094e821105d1cdfd3cae24f4b9184ef` and `2836f5f0e4e0e903acc0e3633e6204be3f982a5d` as metadata-only. They are implementation because they modify `src/qual/commands/catalog.py` and, for `ab96cb722094e821105d1cdfd3cae24f4b9184ef`, `tests/unit/test_commands_catalog.py`.
- Accurate implementation commits under review: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, `ab96cb722094e821105d1cdfd3cae24f4b9184ef`, and `2836f5f0e4e0e903acc0e3633e6204be3f982a5d`. Commit `0492bb2bc00dd03c126789985d9a5f18e5cd8e67` is metadata-only because it refreshes `THREAD.md` and `THREAD_PACKET.md` while documenting the additional implementation commits; `f1931ac437f5f051b397e36ca27560bd1023d975`, `0fe7c8c84e5f65bb0f557d191960ebbcf3946b9ef`, `07a3eeb86c53ae01416569b8806d63d4085e44c1`, `d020227ca44c691f2f8e655762b4465618f1faa5`, and this final fixer-pass commit are also metadata-only.
- Merge base used for file accounting: `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`.
- Risk classification: low-risk lane-owned implementation plus one shared-by-approval unit-test exception and packet metadata; no integrator-locked files are changed in the corrected target.
- Complete corrected file list: `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
- Packet metadata files changed: `THREAD.md` and `THREAD_PACKET.md`.
- Exact canonical demo-path step advanced: `preview/apply/reject patch`.
- Canonical demo-path step advanced: this strengthens the open/retrieve/context-basket/patch-preview CLI control surface needed to execute the engine-first demo path while Textual remains disabled; the exact canonical step made more real by this command-catalog contract hardening is `preview/apply/reject patch`.
- Per-task canonical demo-path mapping uses the current engine-first MVP path from `AGENTS.md`: `Engine stability -> A2UI contracts with CLI fallback -> preview/apply/reject patch`.
- Implementation review basis: the branch tip produced by this fixer pass.
- Implementation slice: `src/qual/commands/catalog.py` and shared-by-approval test exception `tests/unit/test_commands_catalog.py`; no integrator-locked files were changed in the reviewed implementation commits. The implementation fixes tighten the canonical CLI-token contract, add the `diff-preview` alias-replacement and alias-before-canonical regressions, and refresh packet metadata.
- Final fixer validation pass on 2026-04-29: confirms the corrected branch tip still contains only packet metadata, `src/qual/commands/catalog.py`, and the approved shared-test exception `tests/unit/test_commands_catalog.py`; shared-by-approval test edit is `YES`, integrator-locked implementation edit is `NO`, and the final HEAD SHA is reported after this metadata-only validation commit.
- Required gates for the exact corrected target: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all pass.
