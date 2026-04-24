# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py`, plus focused regressions in `tests/unit/test_commands_catalog.py`.
- Canonical demo-path step advanced: `preview and apply or reject a patch`
- Concrete canonical mapping: this slice advances canonical step 5, `preview and apply or reject a patch`, by locking the parser-backed patch-review CLI entrypoints to the canonical catalog so operators can move from `produce a plan or revision` into patch review on a deterministic CLI surface instead of silently accepting parser/catalog drift.
- Concrete canonical-path blocker removed: deterministic CLI ordering and fast-fail parser/catalog drift detection are now enforced at the patch-review boundary, removing the blocker where review/apply commands could silently diverge from the canonical catalog while Textual remains disabled.
- Scope clarification: this is CLI compatibility hardening for the existing patch-review step while Textual remains disabled. It does not add new commands, new engine behavior, persistence work, or new workflow reachability.
- Risk reason: this is a high-risk/shared-file handoff because it hardens the public command contract in `src/qual/commands/catalog.py` and uses the explicitly approved shared regression path `tests/unit/test_commands_catalog.py`, so parser drift at canonical patch-review entrypoints would directly weaken the active Milestone 3 CLI compatibility surface.
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
