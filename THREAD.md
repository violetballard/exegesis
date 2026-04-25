# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: reviewed command-catalog slice only, not the broader branch-tip command-surface packet
- Verified implementation basis SHA: `3ede0bbf814cbee26464fa671be67b2e3293ab93`
- Submitted tip note: any newer tip created by this handoff refresh is metadata-only packet bookkeeping on top of that verified implementation basis
- Review scope: deterministic `command_cli_contract()` behavior in `src/qual/commands/catalog.py` plus the repo-policy-allowlisted shared regression coverage in `tests/unit/test_commands_catalog.py`
- Final validated packet tip before this metadata-only refresh: `7e2ecb220`
- Implementation commits already on this branch:
  - `beaf91853` for grouped parser-entrypoint contract validation
  - `4a4d47048` for alias-level parser-surface drift rejection
  - `077764032` for explicit shared regression coverage on stable canonical-name ordering with token drift
  - `3ede0bbf8` for direct live parser contract coverage and additional stable-name drift regressions
- Canonical demo-path step(s) advanced: Milestone 3 CLI-compatibility hardening for the existing CLI operator surface that covers `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and `continue working`
- Explicit handoff sentence: This work strengthens the existing Milestone 3 CLI operator surface for `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and `continue working` by keeping the parser-facing command contract deterministic for those already-supported smoke-route entrypoints while Textual remains disabled; it does not add new engine workflow capability
- Concrete blocker removed: without this contract hardening, parser/catalog drift could silently reorder, add, or drop the existing operator-facing CLI tokens that must stay stable across `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and `continue working`, so the current MVP smoke-route surface could drift away from the real CLI contract
- Reviewer fix closure:
  1. `command_cli_contract()` now validates the grouped parser-entrypoint projection, so alias add/remove/reorder drift fails even when canonical-name order stays stable.
  2. `tests/unit/test_commands_catalog.py` covers the live parser `diff` -> `diff-preview` alias, the `context-basket list` path, and token-level parser drift that preserves canonical-name order.
  3. This handoff explicitly maps the change to the canonical demo-path step above and names the concrete CLI-fallback blocker it removes.
- Verified re-review tip before this packet refresh: `3ede0bbf8`
- Final validated handoff tip before this packet refresh: `7e2ecb220`
- Verified token-drift coverage on that tip includes alias substitution, extra parser token, removed parser token, and reordered parser tokens within the same canonical command group while canonical-name order stays stable
- MVP focus tie-in: this is Milestone 3 CLI-compatibility hardening for the current `A2UI`-with-CLI-fallback MVP emphasis, not new workflow capability or command-surface expansion
- Shared-test approval record: `scripts/scope-check.sh` allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands`; the allowlist line was added by Violet Ballard in commit `c3a66bb580` (`fix(commands): tighten feat-commands packet and policy`, `2026-03-28`) and is still present on the current tip
- Scope-check handling: `make scope-check` passed without `SCOPE_ALLOW_SHARED=1` because the current scope gate already treats `tests/unit/test_commands_catalog.py` as an approved shared regression test for this lane
- Roadmap alignment: `ROADMAP.md` Milestone 3 exit criterion `Contract changes documented and intentional` plus `AGENTS.md` active MVP note `A2UI contracts with CLI fallback`; this protects the deterministic CLI contract for the existing `open`, `retrieve`, `patch-review`/`apply-patch`/`reject-patch`, and `continue` command surface while Textual remains disabled and does not claim broader product progress
- Vision alignment: primarily `PRODUCT_VISION.md` capability 4 `Operator-first control surface`, because this handoff only hardens the current CLI contract while Textual remains disabled; `PRODUCT_VISION.md` capability 5 `Agent-to-UI protocol (A2UI)` is relevant only secondarily through the existing CLI fallback surface, not through any new workflow or audit behavior
- Scope boundary: this handoff claims only the command-catalog contract hardening and the allowlisted shared regression test; it does not claim parser-entrypoint rewrites, diff-preview work, workflow-wrapper additions, provider/routing changes, or storage behavior changes
- Task accounting note: metadata-only packet refreshes are bookkeeping for the handoff and are not counted as implementation tasks

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Required Gates

- Reviewer packet reported these gates as passing on implementation basis SHA `3ede0bbf814cbee26464fa671be67b2e3293ab93`
- This fixer refresh reruns the same required gates on `2026-04-25` in the lane worktree after confirming the current tip `7e2ecb220` keeps the reviewer-requested parser-projection validation, direct live parser coverage, canonical demo-path mapping, and narrowed implementation task accounting
- Green implementation evidence on the current branch comes from `beaf91853`, `4a4d47048`, `077764032`, and `3ede0bbf8`, while the final validated packet tip is `7e2ecb220`; this handoff refresh only records that evidence and the corrected plan mapping
- Verified gate rerun on tip `7e2ecb220`: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed
- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
