# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py`, plus focused regressions in `tests/unit/test_commands_catalog.py`.
- Canonical demo-path step advanced: canonical step `5 of 7`, `preview and apply or reject a patch`
- Concrete canonical mapping: this slice advances canonical step `5 of 7`, `preview and apply or reject a patch`, by locking the parser-backed patch-review CLI entrypoints to the canonical catalog so operators can move from `produce a plan or revision` into patch review on a deterministic CLI surface instead of silently accepting parser/catalog drift.
- Current MVP loop note: by hard-failing parser/catalog drift at the patch-review boundary, this change keeps the CLI side of the manual smoke flow stable at review/apply time so operators can complete the current `vault -> context -> run -> patch -> export` loop without silent command-surface drift.
- Concrete canonical-path blocker removed: deterministic CLI ordering and fast-fail parser/catalog drift detection are now enforced at the patch-review boundary, removing the concrete blocker where review/apply commands could silently diverge from the canonical catalog before the operator can safely continue to `persist the updated document/session state` while Textual remains disabled.
- Roadmap alignment note: this is not second-order work because `ROADMAP.md` Milestone 1 calls for command behavior hardening and manual CLI smoke-flow stability, while Milestone 2 explicitly calls out missing parser-edge tests; this slice hardens that command boundary and adds the targeted regression coverage.
- Scope clarification: this is CLI compatibility hardening for the existing patch-review step in the current manual operator flow. It does not add new commands, new engine behavior, persistence work, or new workflow reachability.
- Risk reason: this is a high-risk/shared-file handoff because it hardens the public command contract in `src/qual/commands/catalog.py` and uses the explicitly approved shared regression path `tests/unit/test_commands_catalog.py`, so parser drift at patch-review entrypoints would directly weaken the current manual CLI smoke flow.
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
