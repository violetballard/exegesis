# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: reviewed command-catalog slice only, not the broader branch-tip command-surface packet
- Verified implementation basis SHA: `0777640324e7d3a54dba191135bd2d867c32d399`
- Submitted tip note: any newer tip created by this handoff refresh is metadata-only packet bookkeeping on top of that verified implementation basis
- Review scope: deterministic `command_cli_contract()` behavior in `src/qual/commands/catalog.py` plus the approved shared regression coverage in `tests/unit/test_commands_catalog.py`
- Implementation commits already on this branch:
  - `beaf91853` for grouped parser-entrypoint contract validation
  - `4a4d47048` for alias-level parser-surface drift rejection
  - `077764032` for explicit shared regression coverage on stable canonical-name ordering with token drift
- Canonical demo-path step advanced: `preview and apply or reject a patch`, because the command catalog is the CLI-facing contract that must stay deterministic before an operator can safely reach patch preview/apply-or-reject while the Textual client remains disabled
- Concrete blocker removed: without this contract hardening, parser/catalog drift could silently reorder, add, or drop the operator-facing CLI tokens that must stay stable for the canonical `preview and apply or reject a patch` step, so the current MVP loop could keep a stale smoke-check contract while the real CLI patch path no longer matches the catalog
- Reviewer fix closure:
  1. `command_cli_contract()` now validates the grouped parser-entrypoint projection, so alias add/remove/reorder drift fails even when canonical-name order stays stable.
  2. `tests/unit/test_commands_catalog.py` covers token-level parser drift that preserves canonical-name order.
  3. This handoff explicitly maps the change to the canonical demo-path step above and names the concrete CLI-fallback blocker it removes.
- MVP focus tie-in: this is CLI-fallback contract hardening for the current `A2UI`-with-CLI-fallback MVP emphasis, not new command-surface expansion
- Roadmap alignment: `ROADMAP.md` Milestone 3 `Real workflow loop` CLI compatibility plus the `AGENTS.md` canonical demo-path `preview and apply or reject a patch` step; this protects but does not expand the existing patch step
- Vision alignment: `PRODUCT_VISION.md` capability 4 `Operator-first control surface` and capability 5 `Agent-to-UI protocol (A2UI)` via the current CLI fallback surface; this is current-surface hardening, not broader command reachability work
- Scope boundary: this handoff claims only the command-catalog contract hardening and the approved shared regression test; it does not claim parser-entrypoint rewrites, diff-preview work, workflow-wrapper additions, provider/routing changes, or storage behavior changes
- Task accounting note: metadata-only packet refreshes are bookkeeping for the handoff and are not counted as implementation tasks

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Required Gates

- Reviewer packet reported these gates as passing on implementation basis SHA `0777640324e7d3a54dba191135bd2d867c32d399`
- This fixer refresh reruns the same required gates on `2026-04-24` in the lane worktree after confirming the live branch already contains the reviewer-requested parser-projection validation and token-drift coverage
- Green implementation evidence on the current branch comes from `beaf91853`, `4a4d47048`, and `077764032`; this handoff refresh only records that evidence and the corrected plan mapping
- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
