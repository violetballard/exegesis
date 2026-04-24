# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/cli.py` and `src/qual/commands/catalog.py`, plus focused regressions in `tests/unit/test_commands_catalog.py`; this slice locks `command_cli_contract()` to the live parser-backed catalog surface and rejects parser drift.
- Scope clarification: this is command-contract hardening only, not new command behavior, persistence or auditability work, or a new workflow capability.
- Canonical MVP flow advanced: `open project/document -> retrieve relevant material -> preview and apply or reject a patch` for the manual CLI smoke flow, via `bootstrap`/`project-open` for open, `context-basket` for retrieval staging, and `diff-preview`/`review-patch` for patch preview.
- Explicit re-review statement: this `feat-commands` CLI-contract hardening slice strengthens the canonical `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch` steps by preserving the operator-facing CLI command catalog contract used by `bootstrap`/`project-open`, `context-basket`, and `diff-preview`/`review-patch` while CLI remains the active first-class surface.
- Demo-path sentence: this change makes the `open project/document -> retrieve relevant material -> preview and apply or reject a patch` loop more real for the CLI-first MVP path because the concrete parser-backed command entrypoints an operator runs now fail fast if parser drift changes the canonical catalog contract.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI contract from the canonical catalog, so an operator could attempt the `open project/document -> retrieve relevant material -> preview and apply or reject a patch` loop through a command surface that no longer matched the expected contract.
- Reviewed implementation commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Shared-file approval reference: `scripts/scope-check.sh` explicitly allowlists both `src/qual/cli.py` and `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`.
- Shared-edit checkpoint reference: `THREAD_PACKET.md` now preserves the high-risk `before risky/shared file edit` checkpoint stating that both shared paths were verified against the branch allowlist before the parser source and handoff metadata were refreshed.

## Reviewed Files

- `src/qual/cli.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Required Gates

- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
