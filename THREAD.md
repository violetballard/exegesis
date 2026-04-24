# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py`, plus focused regressions in `tests/unit/test_commands_catalog.py`.
- Canonical demo-path step advanced: `preview and apply or reject a patch`
- Concrete canonical mapping: this slice makes `preview and apply or reject a patch` more reliable by forcing the parser-backed patch-review CLI entrypoints to stay aligned with the canonical catalog before review commands run.
- Scope clarification: this is CLI compatibility hardening for the existing patch-review step while Textual remains disabled. It does not add new commands, new engine behavior, persistence work, or new workflow reachability.
- High-risk framing note: this remains a high-risk handoff because it hardens a public command contract in `src/qual/commands/catalog.py` and uses the explicitly approved shared regression path `tests/unit/test_commands_catalog.py`.
- Reviewed implementation evidence: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`
- Approval basis note: implementation approval remains pinned to those two files only; this pointer file is metadata-only.

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Required Gates

- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
