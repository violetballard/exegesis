# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Authoritative review target: isolated command-catalog slice `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` plus this fixer pass.
- Current fixer packet satisfied: `fixer__feat-commands__20260429T234833Z`.
- Integration instruction: review cannot proceed yet. The intended review surface is only `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`, but protected `.agents/**` and `.codex/**` metadata still remains in `main..HEAD`.
- Intended corrected file list: `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
- Out-of-lane branch-tip scope partially removed: unrelated writable engine, router, docs, config, automation, and disabled Textual lane changes are restored to `main`; protected `.agents/**` and `.codex/**` metadata could not be rewritten from this sandbox.
- Exact canonical demo-path step advanced: `preview and apply/reject patch`.
- Canonical demo-path mapping: this command contract hardening preserves the CLI fallback route for `diff-preview` / `patch-review`, so operators can preview patch output and keep the apply/reject step reachable while Textual remains disabled. It also keeps adjacent smoke tokens stable for `open project/document`, `retrieve relevant material`, `promote or gather context`, and `save and continue`.
- Ownership: lane-owned implementation edit is `src/qual/commands/catalog.py`; shared-by-approval test edit is `tests/unit/test_commands_catalog.py`; packet metadata edits are `THREAD.md` and `THREAD_PACKET.md`; integrator-locked edits are none in the corrected review target.
- Gate status for this fixer pass: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, focused `python -m unittest tests.unit.test_commands_catalog`, and `./typecheck-test.sh` pass. `./quality-test.sh` and `make ci` fail because protected `.codex/packet_router/config.json` still has the rejected local-provider config.
