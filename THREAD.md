# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Corrected review target: the full current branch tip produced by this fixer pass, not the earlier `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice.
- Current fixer packet validated: `fixer__feat-commands__20260429T234430Z`.
- Integration instruction: review the full branch-tip merge diff exactly as reported in `THREAD_PACKET.md`; this packet no longer narrows the review basis to four implementation commits.
- Accurate implementation basis: `git log --reverse --format='%H %s' main..HEAD -- src/qual/commands/catalog.py tests/unit/test_commands_catalog.py` reports `340` implementation commits for the current branch-tip target. This includes `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, `ab96cb722094e821105d1cdfd3cae24f4b9184ef`, `2836f5f0e4e0e903acc0e3633e6204be3f982a5d`, `e72c69d75446e3ad10de3d3d0c7c30b4957c4baa`, and `594c21819dfa534f51eb2af784630e21b0acff48`, but is not limited to them.
- Merge base used for file accounting: `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`.
- Complete corrected file list: `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
- Exact final merge diff name-status: `M THREAD.md`, `A THREAD_PACKET.md`, `A src/qual/commands/catalog.py`, and `A tests/unit/test_commands_catalog.py`.
- Exact final merge diff size: `1917` insertions, `2` deletions, `1915` net LOC across `4` files.
- Budget and size compliance: `NOT COMPLIANT` with the normal AGENTS size limits. This branch-tip target requires explicit integrator acceptance of an over-budget branch tip or a follow-up split/cherry-pick instruction; this handoff explicitly requests that acceptance if review continues on the full branch tip.
- Packet metadata files changed: `THREAD.md` and `THREAD_PACKET.md`.
- Exact canonical demo-path step advanced: `preview and apply/reject patch`.
- Canonical demo-path step advanced before handoff: this strengthens the CLI control surface needed to execute the engine-first demo path while Textual remains disabled; the exact canonical step made more real by this command-catalog contract hardening is `preview and apply/reject patch`, with supporting coverage for `open project/document`, `retrieve relevant material`, `promote or gather context`, and `save and continue` command routes.
- Scope-tightening blocker removed: parser/catalog drift could silently change the CLI smoke surface used to prove the engine-first loop while Textual remains disabled, especially the `diff-preview` / `patch-review` route operators use to preview, apply, or reject patch work through the CLI fallback instead of Textual. This is concrete blocker-removal rather than second-order contract cleanup because it protects the exact CLI fallback route needed while Textual remains disabled.
- Per-task canonical demo-path mapping uses the current engine-first MVP path from `AGENTS.md` and is expanded in `THREAD_PACKET.md` across `open project/document`, `retrieve relevant material`, `promote or gather context`, `preview and apply/reject patch`, and `save and continue`.
- Implementation review basis: the full branch tip produced by this fixer pass, including `594c21819dfa534f51eb2af784630e21b0acff48` and its command-catalog smoke-token API changes.
- Implementation slice in final diff: owned runtime edit `src/qual/commands/catalog.py` plus approved shared-by-approval test edit `tests/unit/test_commands_catalog.py`; no integrator-locked files were edited in the reviewed implementation diff.
- Final fixer validation pass on 2026-04-29 for reviewer packet `fixer__feat-commands__20260429T234430Z`: confirms the corrected branch tip still contains only packet metadata, the owned runtime edit `src/qual/commands/catalog.py`, and the approved shared-by-approval test edit `tests/unit/test_commands_catalog.py`; shared-by-approval test edit is `YES`, integrator-locked implementation edit is `NO`, and the final HEAD SHA is reported after this final fixer-pass commit.
- Required gates for the exact corrected target after `fixer__feat-commands__20260429T234430Z`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all pass on 2026-04-29. Focused reviewer regression check `python -m unittest tests.unit.test_commands_catalog` also passes.
