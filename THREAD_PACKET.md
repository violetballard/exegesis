## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Fresh fixer packet for the A2UI contract integration-block response.
- Fresh review target: branch tip after this fixer commit.

## Integration Failure Reproduction

1. Reviewed the rejected approval context for `R__APPROVED__codex-feat-a2ui-contract__3e8b7be73d7f77d804c69fd9e2b409337db3e565__20260514T115741Z.md`.
2. Confirmed the stale selected integration target in this packet was `b929fe6c7a1159c7882acedd247aca31a93cd123`.
3. Confirmed the integrator failure mode: `main` already contains the deterministic A2UI action-order behavior, so cherry-picking only `b929fe6c7a1159c7882acedd247aca31a93cd123` becomes empty after conflict resolution and performs no integration.
4. Attempted a non-mutating `git merge-tree main b929fe6c7a1159c7882acedd247aca31a93cd123` reproduction in this sandbox with a writable temp root; Git could not create its temporary merge file here (`Operation not permitted`). The captured integrator output remains the source of truth for the empty cherry-pick failure.

## Required Fix Applied

- Replaced the stale cherry-pick-only handoff instructions that routed integration back to already-applied commit `b929fe6c7a1159c7882acedd247aca31a93cd123`.
- This packet now submits the current branch tip after the fixer commit as the fresh review target.
- The selected integration target is no longer `b929fe6c7a1159c7882acedd247aca31a93cd123`.

## Scope Completed

- Canonicalized materialized A2UI action order in `src/qual/ui/a2ui.py` so equivalent supported action payloads render deterministically in CLI fallback output.
- Updated unit coverage in `tests/unit/test_a2ui_contract.py` to assert the full canonicalized action list instead of only action ids.
- Preserved CLI fallback behavior as the active renderer path while keeping action handling typed, allowlisted, and engine-authored.
- Fixed the handoff packet routing that caused the integrator to retry an empty cherry-pick.
- Did not add Textual, Exegesis Console, Studio renderer, provider routing, or core engine entrypoint work.

## Files Changed For This Fixer Target

Packet:
- `THREAD_PACKET.md`

Prior A2UI implementation/test work already present on the lane branch:
- `src/qual/ui/a2ui.py`
- `tests/unit/test_a2ui_contract.py`

## Plan Alignment

- Roadmap item(s) affected: `ROADMAP.md` Milestone 3: Real workflow loop.
- MVP task anchor: `AGENTS.md` active MVP item `A2UI contracts with CLI fallback`.
- Vision capability affected: `PRODUCT_VISION.md` Capability 4: Shared UI contract / operator-first control surface.
- Canonical demo-path step advanced: deterministic A2UI action ordering keeps the CLI fallback demo path stable when equivalent engine-authored action payloads arrive in different input orders.
- Budget classification: high-risk-compatible fixer packet with `3` completed tasks, under the `4` task cap.
- Explicitly deferred: Textual implementation, Exegesis Console renderer work, Studio renderer work, provider routing changes, and core engine policy changes.

## Tasks Completed

1. Reproduced the integration blocker from the lane packet and captured integrator output: stale cherry-pick target `b929fe6c7a1159c7882acedd247aca31a93cd123` resolved empty against current `main`.
2. Verified the deterministic materialized action-order code path is present in `src/qual/ui/a2ui.py`.
3. Updated this handoff packet so re-review targets the fresh branch tip after the fixer commit instead of retrying the empty cherry-pick.

## Required Handoff Fields

- Roadmap item(s) affected: `ROADMAP.md` Milestone 3: Real workflow loop; current MVP `A2UI contracts with CLI fallback` canonical path.
- Vision capability affected: `PRODUCT_VISION.md` Capability 4: Shared UI contract / operator-first control surface.
- Canonical demo-path step advanced: deterministic A2UI action ordering for the CLI fallback demo path, preserving stable action rendering for equivalent engine-authored payloads.
- Routing/provider impact note: None.
- Size-budget status: Within fixer scope. This fixer commit changes only `THREAD_PACKET.md`.
- Scope / approval note: This packet requests re-review of the branch tip after this fixer commit because the prior cherry-pick-only target is already empty against `main`.
- Selected integration target: merge/review current `codex/feat-a2ui-contract` branch tip after this fixer commit.
- Shared/integrator-locked impact: None for this fixer commit; it changes handoff packet text only.

## Commands Run And Outcomes

- `git status --short --branch`: PASS; branch `codex/feat-a2ui-contract`.
- `rg -n "materialized|action order|terminal|cards|_render_terminal|Action" shared tests src -S`: PASS with expected matches; `shared` path absent in this worktree.
- `rg -n "def _normalize_card_actions|filtered.append|seen.add|_canonical|materializes_supported_cards_with_canonical|keeps_action_order_deterministic" src/qual/ui/a2ui.py tests/unit/test_a2ui_contract.py src/qual/ui/test_a2ui_fallback_safety.py`: PASS; deterministic action-order implementation and coverage present.
- `git log --oneline --decorate -12`: PASS; inspected current branch tip and recent fixer commits.
- `git branch --contains b929fe6c7a1159c7882acedd247aca31a93cd123`: PASS; commit exists on `codex/feat-a2ui-contract`.
- `git rev-parse main HEAD`: PASS; `main` is `4c5268b3ea0ba62aaac4956b5238d2721c750116`, pre-fix HEAD was `3e8b7be73d7f77d804c69fd9e2b409337db3e565`.
- `git merge-base main HEAD`: PASS; merge base is `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27`.
- `git diff --stat main...HEAD`: PASS; inspected branch range size.
- `git diff --name-only main...HEAD`: PASS; inspected changed paths.
- `TMPDIR=/private/tmp git merge-tree main b929fe6c7a1159c7882acedd247aca31a93cd123 | rg -n "<<<<<<<|>>>>>>>|changed in both|src/qual/ui/a2ui.py|tests/unit/test_a2ui_contract.py|Auto-merging|CONFLICT|_filter_supported_actions|_render_terminal_block"`: BLOCKED by sandbox temp-file creation (`Operation not permitted`); captured integrator output remains authoritative for this reproduction.
- `make scope-check`: PASS (`[devex] scope-check: passed for branch 'codex/feat-a2ui-contract'`).
- `./quality-format.sh --check`: PASS (`[format] check passed`).
- `./quality-lint.sh`: PASS (`[lint] passed`).
- `./quality-test.sh`: PASS (smoke passed; all 11 unit modules passed, including 101 A2UI contract tests).
- `./typecheck-test.sh`: PASS (`[typecheck] compiling Python sources in src/`).
- `make ci`: PASS (scope, format, lint, typecheck, and tests passed; `[devex] CI entrypoint completed`).

## Risks / Blockers

- Risk: `LOW` for this fixer commit because it changes only the handoff packet.
- Residual integration risk: the lane branch has substantial historical A2UI work; this packet fixes the stale selected-target blocker but does not shrink the existing branch history.
- Blockers: none.
