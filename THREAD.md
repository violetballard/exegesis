# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: reviewed command-catalog slice only, not the broader branch-tip command-surface packet
- Verified implementation basis SHA: `0777640324e7d3a54dba191135bd2d867c32d399`
- Submitted tip note: any newer tip created by this handoff refresh is metadata-only packet bookkeeping on top of that verified implementation basis
- Review scope: deterministic `command_cli_contract()` behavior in `src/qual/commands/catalog.py` plus the repo-policy-allowlisted shared regression coverage in `tests/unit/test_commands_catalog.py`
- Implementation commits already on this branch:
  - `beaf91853` for grouped parser-entrypoint contract validation
  - `4a4d47048` for alias-level parser-surface drift rejection
  - `077764032` for explicit shared regression coverage on stable canonical-name ordering with token drift
- Canonical demo-path step advanced: the roadmap `patch` step inside `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate`, specifically the canonical CLI demo-path tokens `patch-review`, `apply-patch`, and `reject-patch`
- Explicit handoff sentence: This work makes the roadmap `patch` step more real by keeping the parser-facing CLI contract deterministic for `patch-review`, `apply-patch`, and `reject-patch`, so token drift fails before an operator reaches the current CLI-first review/apply-or-reject loop while Textual remains disabled
- Concrete blocker removed: without this contract hardening, parser/catalog drift could silently reorder, add, or drop the operator-facing CLI tokens that must stay stable for the roadmap `patch` step, so the current MVP loop could keep a stale smoke-check contract while the real CLI review/apply-or-reject path no longer matches the catalog
- Reviewer fix closure:
  1. `command_cli_contract()` now validates the grouped parser-entrypoint projection, so alias add/remove/reorder drift fails even when canonical-name order stays stable.
  2. `tests/unit/test_commands_catalog.py` covers token-level parser drift that preserves canonical-name order.
  3. This handoff explicitly maps the change to the canonical demo-path step above and names the concrete CLI-fallback blocker it removes.
- Verified re-review tip before this packet refresh: `c68289723`
- Verified token-drift coverage on that tip includes alias substitution, extra parser token, removed parser token, and reordered parser tokens within the same canonical command group while canonical-name order stays stable
- MVP focus tie-in: this is CLI-fallback contract hardening for the current `A2UI`-with-CLI-fallback MVP emphasis, not new command-surface expansion
- Shared-test approval record: `scripts/scope-check.sh` allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands`; the allowlist line was added by Violet Ballard in commit `c3a66bb580` (`fix(commands): tighten feat-commands packet and policy`, `2026-03-28`) and is still present on the current tip
- Scope-check handling: `make scope-check` passed without `SCOPE_ALLOW_SHARED=1` because the current scope gate already treats `tests/unit/test_commands_catalog.py` as an approved shared regression test for this lane
- Roadmap alignment: `ROADMAP.md` Milestone 5 exit criterion `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate` plus `AGENTS.md` active MVP note `A2UI contracts with CLI fallback`; this protects the existing CLI-first `patch` step in that loop, concretely the canonical `patch-review` -> `apply-patch`/`reject-patch` contract, and does not claim broader product progress
- Vision alignment: primarily `PRODUCT_VISION.md` capability 4 `Operator-first control surface`, because this handoff only hardens the current CLI contract while Textual remains disabled; `PRODUCT_VISION.md` capability 5 `Agent-to-UI protocol (A2UI)` is relevant only secondarily through the existing CLI fallback surface, not through any new workflow or audit behavior
- Scope boundary: this handoff claims only the command-catalog contract hardening and the allowlisted shared regression test; it does not claim parser-entrypoint rewrites, diff-preview work, workflow-wrapper additions, provider/routing changes, or storage behavior changes
- Task accounting note: metadata-only packet refreshes are bookkeeping for the handoff and are not counted as implementation tasks

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Required Gates

- Reviewer packet reported these gates as passing on implementation basis SHA `0777640324e7d3a54dba191135bd2d867c32d399`
- This fixer refresh reruns the same required gates on `2026-04-24` in the lane worktree after confirming the current tip `c68289723` already contains the reviewer-requested parser-projection validation and token-drift coverage
- Green implementation evidence on the current branch comes from `beaf91853`, `4a4d47048`, and `077764032`; this handoff refresh only records that evidence and the corrected plan mapping
- Verified gate rerun on tip `c68289723`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed
- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
