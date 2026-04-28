# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: actual submitted branch tip after this fixer commit, not the older `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice.
- Scope: Milestone 3 CLI command-contract hardening for the engine-first MVP loop while Textual lanes remain disabled.
- Roadmap alignment: `ROADMAP.md` Milestone 3 exit criterion `Contract changes documented and intentional`, plus CLI stability for the MVP flow.
- Vision alignment: `PRODUCT_VISION.md` capability 3 `Canonical engine contract`.
- Scope boundary: this handoff claims deterministic CLI command-surface hardening only. It does not claim retrieval, persistence, provider routing, apply/reject engine execution, or Textual UI progress.

## Reviewed Files

- `scripts/scope-check.sh`
- `src/qual/cli.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `src/qual/commands/workflow.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Shared / Approval Notes

- `src/qual/cli.py` is shared-by-approval for `codex/feat-commands*` in `THREAD_OWNERSHIP.md` and is included because the live argparse entrypoint surface must match the command catalog.
- `scripts/scope-check.sh` is included to keep scope enforcement aligned with approved shared command tests.
- `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` are approved shared test coverage for this command-surface handoff.

## Required Gates

- `python -m unittest tests.unit.test_commands_catalog`
- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
