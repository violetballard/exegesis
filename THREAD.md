# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: reviewed command-catalog slice only, not the broader branch-tip command-surface packet
- Verified implementation basis SHA: `3ede0bbf814cbee26464fa671be67b2e3293ab93`
- Submitted tip note: any newer tip created by this handoff refresh is metadata-only packet bookkeeping on top of that verified implementation basis
- Review scope: deterministic `command_cli_contract()` behavior in `src/qual/commands/catalog.py` plus the repo-policy-allowlisted shared regression coverage in `tests/unit/test_commands_catalog.py`
- Final validated packet tip before this metadata-only refresh: `171a6c810`
- Implementation commits already on this branch:
  - `beaf91853` for grouped parser-entrypoint contract validation
  - `4a4d47048` for alias-level parser-surface drift rejection
  - `077764032` for explicit shared regression coverage on stable canonical-name ordering with token drift
  - `3ede0bbf8` for direct live parser contract coverage and additional stable-name drift regressions
- Canonical demo-path step advanced: `preview and apply or reject a patch` via the existing CLI fallback surface while Textual remains disabled
- Explicit handoff sentence: This work makes `preview and apply or reject a patch` more real on the current engine-first demo path by locking the parser-facing command contract for the existing patch-review CLI entrypoints so that parser/catalog drift fails fast instead of silently mutating that operator surface; it does not add a new workflow step
- Concrete blocker removed: without this contract hardening, parser/catalog drift could silently reorder, add, or drop the patch-review CLI tokens that must stay stable for `preview and apply or reject a patch`, so the current MVP CLI fallback could drift away from the real engine contract at the exact step where operators inspect and accept or reject a change
- Reviewer fix closure:
  1. `command_cli_contract()` now validates the grouped parser-entrypoint projection, so alias substitution, add/remove, and reorder drift fail even when canonical-name order stays stable.
  2. `tests/unit/test_commands_catalog.py` covers the live parser `diff` -> `diff-preview` alias, the `context-basket list` path, and token-level parser drift that preserves canonical-name order.
  3. This handoff explicitly maps the change to the canonical demo-path step above and names the concrete CLI-fallback blocker it removes.
- Verified re-review tip before this packet refresh: `3ede0bbf8`
- Final validated handoff tip before this packet refresh: `171a6c810`
- Verified token-drift coverage on that tip includes alias substitution, extra parser token, removed parser token, and reordered parser tokens within the same canonical command group while canonical-name order stays stable
- MVP focus tie-in: this is Milestone 3 CLI-compatibility hardening for one concrete CLI-fallback step in the current engine-first demo path, not new workflow capability or command-surface expansion
- Shared-test approval record: `scripts/scope-check.sh` allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands`; the allowlist line was added by Violet Ballard in commit `c3a66bb580` (`fix(commands): tighten feat-commands packet and policy`, `2026-03-28`) and is still present on the current tip
- Scope-check handling: `make scope-check` passed without `SCOPE_ALLOW_SHARED=1` because the current scope gate already treats `tests/unit/test_commands_catalog.py` as an approved shared regression test for this lane
- Roadmap alignment: `ROADMAP.md` Milestone 3 exit criterion `Contract changes documented and intentional` plus the `AGENTS.md` rule that contract/infra work only counts when it removes a concrete blocker on the canonical demo path; this protects the canonical engine contract and CLI compatibility for the existing `preview and apply or reject a patch` step while Textual remains disabled and does not claim broader product progress
- Vision alignment: `PRODUCT_VISION.md` capability 4 `Operator-first control surface` only; this handoff hardens the current parser/catalog contract that the CLI fallback depends on for the patch-review step and does not claim audit-state or broader workflow progress
- Scope boundary: this handoff claims only the command-catalog contract hardening and the allowlisted shared regression test; it does not claim parser-entrypoint rewrites, diff-preview work, workflow-wrapper additions, provider/routing changes, or storage behavior changes
- Task accounting note: metadata-only packet refreshes are bookkeeping for the handoff and are not counted as implementation tasks

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Required Gates

- Reviewer packet reported these gates as passing on implementation basis SHA `3ede0bbf814cbee26464fa671be67b2e3293ab93`
- This fixer refresh reruns the same required gates on `2026-04-24` in the lane worktree after confirming the current tip `171a6c810` keeps the reviewer-requested parser-projection validation, direct live parser coverage, canonical demo-path mapping, and narrowed implementation task accounting
- Green implementation evidence on the current branch comes from `beaf91853`, `4a4d47048`, `077764032`, and `3ede0bbf8`, while the final validated packet tip is `171a6c810`; this handoff refresh only records that evidence and the corrected plan mapping
- Verified gate rerun on tip `171a6c810`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed
- Gate execution note: bare `python -m pytest` was unavailable in this shell (`No module named pytest`), so verification used the repo-required gate scripts as the source of truth
- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
