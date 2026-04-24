# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `1efa1c47e775e47b2aa4cb7619ea5cc499687448`
- Packet refresh role: `reviewer-fix final verification refresh`
- Packet refresh basis: `regenerated on 2026-04-24T07:33:10Z after rerunning the required gates on the pre-refresh branch tip 1efa1c47e775e47b2aa4cb7619ea5cc499687448 to satisfy the reviewer's numbered handoff fixes for explicit canonical demo-path mapping, concrete blocker removal, narrowed roadmap and vision mapping, and current branch-tip traceability`
- Post-fixer verification: `2026-04-24T07:33:10Z UTC gate rerun confirmed the packet still matches the branch state during this final verification refresh; no implementation files changed in this packet-only refresh`
- Packet-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `handoff_packets/feat-commands.md`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: make the canonical `preview and apply or reject a patch` step more real by keeping the public `diff-preview` preview entrypoint catalog-locked and failing fast if the parser drifts to alias-only, reordered, missing-token, or extra-token shapes.
- Risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (Completed)

1. Lock the default parser surface behind a dedicated `_CLI_ENTRYPOINTS` contract so the command catalog can detect drift independently from spec-derived lookup resolution.
2. Tighten CLI contract validation so live parser entrypoints must match the declared catalog projection, including token-level drift that preserves canonical command order.
3. Replace helper-only regression coverage with live `_CLI_ENTRYPOINTS` drift tests that stay resolvable through lookup but still fail fast, including the exact `diff-preview` removed / `diff` retained case.
4. Regenerate the handoff packet with one concrete canonical demo-path step and an explicit shared-test approval source.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Reviewed implementation commit: `1efa1c47e775e47b2aa4cb7619ea5cc499687448` (`docs(commands): finalize reviewer handoff packet`), carrying forward the command helper implementation from `3e1e7d7f9ebce3001ebe941133b00e145e79cb7b` (`Add command demo branch contract helpers`) and the parser-surface regression coverage from `bd118a6cbb417005bb793b3d784372ba6c1452a1` (`test(commands): cover cached parser surface drift`).
- Packet refresh traceability: the pre-refresh branch tip for this final verification pass was `1efa1c47e775e47b2aa4cb7619ea5cc499687448`; this refresh updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.
- Reviewed implementation files:
  - `src/qual/commands/__init__.py`
  - `tests/unit/test_commands_catalog.py`
  - implementation basis retained on branch: `src/qual/commands/catalog.py`
- Reviewed implementation summary:
  - `_CLI_ENTRYPOINTS` now locks the live default parser token surface independently from `COMMAND_SPECS`, so default CLI drift can be detected instead of re-derived from the same spec source.
  - `CommandDemoBranchContract` and its public exports now expose the trusted and parser-ready review-step apply/reject branch through explicit contract helpers without widening the lane into routing or provider work.
  - `_validated_cli_entrypoints_for()` and `command_cli_contract()` now validate the actual parser surface against the declared catalog projection before exposing canonical names, tokens, or lookup tables.
- focused regression tests now patch `_CLI_ENTRYPOINTS` into alias-substituted, reordered, missing-canonical-token, and extra-entrypoint shapes to prove the contract fails fast even when lookup resolution still lands on the same canonical commands, including after `command_cli_tokens()` has already warmed its cache.

## Scope Completed

- Locked the default parser surface to `_CLI_ENTRYPOINTS` so `command_cli_contract()` checks the live parser token contract instead of comparing only spec-derived canonical-name order.
- Hardened validation so alias substitution, parser reordering, or extra accepted tokens fail fast even when the drifted tokens still resolve back to the same canonical commands.
- Added live parser-drift regression coverage by patching `_CLI_ENTRYPOINTS` into drifted-but-still-resolvable shapes, including the exact case where `diff-preview` disappears while `diff` still resolves to the same canonical command and the cache-warm helper path still has to fail closed.
- Kept the slice narrow: command-surface contract hardening plus targeted tests only, with no provider, routing, storage, retrieval, or terminal workflow behavior changes.

## Canonical Demo-Path Mapping

- Canonical demo-path step advanced: `preview and apply or reject a patch` (`diff-preview` on the public CLI surface).
- Concrete blocker removed: the parser can no longer silently drop the public `diff-preview` token and leave only the still-resolvable alias `diff`, which would otherwise change the operator-visible review step without any fail-fast signal.
- Scope-tightening statement: this slice claims only review-step command-contract hardening plus focused regression coverage. It does not claim new retrieval, patch application, persistence, export, or broader CLI-surface work.
- Current CLI smoke route context: `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff`, entered through `bootstrap --project demo`.
- Smoke-test evidence: `tests/unit/test_commands_catalog.py` proves the live parser surface keeps `diff-preview` before `diff` for `preview and apply or reject a patch` and fails fast when `diff-preview` disappears while `diff` still resolves to the same canonical command, including after `command_cli_tokens()` has already been warmed.
- Plan-alignment note: `ROADMAP.md` Milestone 3 calls out locking user-facing output contracts, so this removes a concrete blocker in the current `preview and apply or reject a patch` stage of the CLI smoke route rather than claiming a broader release-readiness step.

## Approved Exception Note

- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval owner: the integrator-managed branch policy for `codex/feat-commands`
- Approved by: the integrator/release ownership gate for `codex/feat-commands`
- Approval recorded in: `scripts/scope-check.sh` under `is_approved_shared_test()` for branch `codex/feat-commands*`, plus the approval-only rule in `THREAD_OWNERSHIP.md`
- Approval basis: shared test coverage is required to prove the review-facing parser contract and remains the only non-lane-owned path in the reviewed slice.
- Scope-check allowance used: `not required`
- Integrator-locked edits in this slice: `none`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Added `_CLI_ENTRYPOINTS` so the default parser surface is locked independently from the catalog specs.
2. Tightened the CLI contract path to validate actual parser entrypoints against the declared catalog projection before publishing command tokens and lookup tables.
3. Reworked parser-drift regression coverage in `tests/unit/test_commands_catalog.py` to patch `_CLI_ENTRYPOINTS` into drifted-but-still-resolvable shapes, including the exact `diff-preview` removed / `diff` retained drift and the cache-warm helper path.
4. Added explicit review-step branch-contract exports so the current apply/reject branch can be consumed through stable helper surfaces in the command catalog API.
5. Regenerated the handoff packet so the reviewer-requested canonical demo-path step, narrowed engine-first CLI alignment, and shared-test approval source are explicit.

### Files Changed

- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`

### Commands Run and Outcomes

- `make scope-check`: `PASSED`
- `./quality-format.sh --check`: `PASSED`
- `./quality-lint.sh`: `PASSED`
- `./quality-test.sh`: `PASSED`
- `./typecheck-test.sh`: `PASSED`
- `make ci`: `PASSED`
- Gate attribution note: these gates were rerun at 2026-04-24T07:33:10Z against the reviewer-fix packet-refresh workspace state at `1efa1c47e775e47b2aa4cb7619ea5cc499687448`; this refresh updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.

### Risks / Blockers

- Risks:
  - future command-surface additions must update `_CLI_ENTRYPOINTS` and parser-drift coverage together or the contract will fail fast by design
- Blockers:
  - none

## Required Handoff Fields

### Canonical demo-path step advanced

- `preview and apply or reject a patch` (`diff-preview` on the public CLI surface)
- This change makes `preview and apply or reject a patch` more real by keeping the operator-facing `diff-preview` command surface for the current CLI smoke route catalog-locked instead of allowing alias-only parser drift to pass silently.
- Concrete blocker removal: the contract now fails fast if the live parser entrypoint for `preview and apply or reject a patch` drops `diff-preview`, substitutes alias-only ordering, or adds extra accepted tokens while still resolving through lookup, preventing the current CLI smoke route from silently changing at its operator-visible review step.
- Smoke-test evidence for this step is explicit in the shared regression suite: `test_command_cli_contract_matches_the_catalog_order`, `test_command_cli_contract_rejects_parser_surface_drift_when_diff_token_disappears`, `test_command_cli_tokens_rejects_parser_surface_drift_after_cache_warm`, and the alias/reorder drift tests all assert the live `_CLI_ENTRYPOINTS` contract for `diff-preview`.

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 3 `Real workflow loop`: this slice narrows to the existing CLI smoke route and its `preview and apply or reject a patch` step rather than claiming broader workflow coverage.
- `ROADMAP.md` Milestone 3 scope: `preserve CLI compatibility while the package/layout migration lands`; this packet applies that only to the operator-visible parser token contract for the `diff-preview` preview entrypoint in `preview and apply or reject a patch`.
- `ROADMAP.md` Milestone 3 contract note: this slice makes unexpected `diff-preview` parser-surface drift fail fast instead of silently changing the accepted public command tokens in that smoke route.
- This diff contributes only the `preview and apply or reject a patch` step of the current CLI smoke route by hardening the public parser surface used at the review command boundary.
- Scope-tightening statement: this is CLI contract hardening for the current smoke route, not new UI work and not broader demo-path expansion beyond the review-step contract.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: this slice is narrow CLI contract hardening for the operator-visible preview entrypoint. It keeps the public `diff-preview` parser surface deterministic, stable, and catalog-locked so the CLI compatibility surface does not silently drift at the review-step boundary, rather than claiming broader workflow progress or any audit-path change.

### Routing / Provider Impact Note

- None. This diff only hardens local command/demo workflow validation and focused shared test coverage.

### Scope-Check / Ownership Note

- Shared-by-approval edits: `YES`
- Shared-by-approval implementation path included: `tests/unit/test_commands_catalog.py`
- Shared-file approval trace: see the `Approved Exception Note` above; the auditable source in this worktree is the `codex/feat-commands*` shared-test allowlist in `scripts/scope-check.sh` together with the approval-only ownership rule in `THREAD_OWNERSHIP.md`
- Integrator-locked edits: `NO`
- Integrator-locked implementation paths included: `none`
