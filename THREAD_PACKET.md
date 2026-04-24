# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `dbb8e0156f3520c759d4d29e2cbbb186013f6df7`
- Packet refresh role: `reviewer-fix packet refresh`
- Packet refresh basis: `regenerated on 2026-04-24 for re-review against the fixer delta that locks the live parser surface to the command catalog, proves the reviewer-called-out diff-preview-to-diff token drift now fails fast, states the canonical demo-path step explicitly, and narrows roadmap/vision mapping to the current CLI-first command surface in ROADMAP Milestone 1 and PRODUCT_VISION capability 4`
- Packet-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: make the canonical `project-open` bootstrap step in the current CLI smoke route more real by locking the live parser surface to the command catalog and failing fast if canonical CLI entrypoints drift to alias-only or reordered shapes.
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

- Reviewed implementation commit: `dbb8e0156f3520c759d4d29e2cbbb186013f6df7` (`fix(commands): harden parser surface drift checks`).
- Packet refresh traceability: the current branch tip for re-review is a packet-only refresh above `dbb8e0156f3520c759d4d29e2cbbb186013f6df7`; no implementation files beyond the reviewed slice changed in this refresh.
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation summary:
  - `_CLI_ENTRYPOINTS` now locks the live default parser token surface independently from `COMMAND_SPECS`, so default CLI drift can be detected instead of re-derived from the same spec source.
  - `_validated_cli_entrypoints_for()` and `command_cli_contract()` now validate the actual parser surface against the declared catalog projection before exposing canonical names, tokens, or lookup tables.
  - focused regression tests now patch `_CLI_ENTRYPOINTS` into alias-substituted, reordered, missing-canonical-token, and extra-entrypoint shapes to prove the contract fails fast even when lookup resolution still lands on the same canonical commands.

## Scope Completed

- Locked the default parser surface to `_CLI_ENTRYPOINTS` so `command_cli_contract()` checks the live parser token contract instead of comparing only spec-derived canonical-name order.
- Hardened validation so alias substitution, parser reordering, or extra accepted tokens fail fast even when the drifted tokens still resolve back to the same canonical commands.
- Added live parser-drift regression coverage by patching `_CLI_ENTRYPOINTS` into drifted-but-still-resolvable shapes, including the exact case where `diff-preview` disappears while `diff` still resolves to the same canonical command.
- Kept the slice narrow: command-surface contract hardening plus targeted tests only, with no provider, routing, storage, retrieval, or terminal workflow behavior changes.

## Canonical Demo-Path Mapping

- Primary canonical demo-path step advanced now: `project-open` (`bootstrap` the session).
- Explicit canonical demo-path statement required for re-review: this slice advances the canonical `project-open` bootstrap step first, and no other demo-path step is claimed as newly implemented here.
- Primary-step scope note: this packet advances `project-open` first while hardening the parser contract reused by later loop steps.
- Current CLI smoke route statement: the current operator-visible route is `project-open -> retrieval -> patch-review -> apply-patch/reject-patch -> persist -> export-handoff`, entered through parser-ready `bootstrap --project demo`.
- One-line plan alignment: this change makes `project-open` more real by ensuring the operator-facing bootstrap verb for that smoke route cannot silently drift to alias-only entrypoints while still resolving through lookup.
- Active MVP operator path strengthened: the existing CLI smoke route entrypoint into `project-open -> retrieval -> patch-review -> apply-patch/reject-patch -> persist -> export-handoff`.
- Concrete blocker removed: before this guard, the live parser surface for the current CLI smoke route could drift from `bootstrap` to an alias such as `open` and still resolve through lookup, leaving automation, operator runbooks, and CLI fallback consumers pointed at a changed public surface without any fail-fast signal.
- Concrete reviewer-example blocker removed: the parser surface can no longer silently drop the public `diff-preview` token while leaving only `diff`, even though that remaining alias still resolves to the same canonical command and preserves canonical ordering.
- Direct plan-alignment statement: this change makes the `project-open` bootstrap step more real by failing closed when the parser-facing entrypoint contract no longer matches the cataloged command surface.
- Concrete smoke-test evidence already in the reviewed slice: `tests/unit/test_commands_catalog.py` proves the canonical smoke contract keeps `project-open` on `("bootstrap", "--project", "demo")` and that the trusted MVP workflow tables still start from the same parser-ready bootstrap argv for both apply and reject branches.
- Scope-tightening note: this handoff claims only parser-surface drift detection plus focused regression coverage for the primary `project-open` entrypoint contract; it does not claim new retrieval quality, patch semantics, persistence behavior, or export behavior.
- Traceability note: `dbb8e0156f3520c759d4d29e2cbbb186013f6df7` is the implementation tip for this reviewed slice. `THREAD.md` and `THREAD_PACKET.md` are packet refresh companions that capture the updated reviewer-fix mapping and gate results.
- Why this is milestone-worthy now instead of second-order cleanup: `ROADMAP.md` Milestone 1 already includes command and diff-preview hardening and requires the manual CLI smoke flow to remain stable. This guard removes a concrete operator-surface contract risk at the `project-open` entrypoint before the loop even starts.

## Approved Exception Note

- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval owner: the integrator-managed branch policy for `codex/feat-commands`
- Approved by: the integrator/release ownership gate for `codex/feat-commands`
- Approval recorded in: `scripts/scope-check.sh` under `is_approved_shared_test()` for branch `codex/feat-commands*`, plus the approval-only rule in `THREAD_OWNERSHIP.md`
- Approval basis: shared test coverage is required to prove the bootstrap-facing parser contract and remains the only non-lane-owned path in the reviewed slice.
- Scope-check allowance used: `not required`
- Integrator-locked edits in this slice: `none`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Added `_CLI_ENTRYPOINTS` so the default parser surface is locked independently from the catalog specs.
2. Tightened the CLI contract path to validate actual parser entrypoints against the declared catalog projection before publishing command tokens and lookup tables.
3. Reworked parser-drift regression coverage in `tests/unit/test_commands_catalog.py` to patch `_CLI_ENTRYPOINTS` into drifted-but-still-resolvable shapes, including the exact `diff-preview` removed / `diff` retained drift.
4. Regenerated the handoff packet so the reviewer-requested canonical demo-path step, narrowed engine-first CLI alignment, and shared-test approval source are explicit.

### Files Changed

- `src/qual/commands/catalog.py`
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
- Gate attribution note: these gates were rerun on 2026-04-24 against the packet-refresh workspace state whose only changed files above `dbb8e0156f3520c759d4d29e2cbbb186013f6df7` are `THREAD.md` and `THREAD_PACKET.md`.

### Risks / Blockers

- Risks:
  - future command-surface additions must update `_CLI_ENTRYPOINTS` and parser-drift coverage together or the contract will fail fast by design
- Blockers:
  - none

## Required Handoff Fields

### Canonical demo-path step advanced

- `project-open` (`bootstrap` the session)
- This change makes `project-open` more real by keeping the operator-facing bootstrap command surface for the current CLI smoke route catalog-locked instead of allowing alias-only parser drift to pass silently.
- Concrete blocker removal: the contract now fails fast if the live parser entrypoint for bootstrap drifts to a different accepted token set while still resolving through lookup, preventing the current CLI smoke route from silently changing at its first operator-visible step.
- Smoke-test evidence for this step is explicit in the shared regression suite: `test_command_smoke_contract_bundles_the_mvp_invocation_surface` keeps `project-open` mapped to `("bootstrap", "--project", "demo")`, and the trusted workflow-table tests keep both apply and reject branches rooted at that same bootstrap argv.

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 1 `Bootstrap Flow Stabilization`: this slice hardens the CLI-first `project-open` entrypoint used to start the current smoke route.
- `ROADMAP.md` Milestone 1 scope: `Command and diff-preview behavior hardening`; this packet narrows that to parser-surface drift detection for the public command tokens only.
- `ROADMAP.md` Milestone 1 exit criteria: `Manual CLI smoke flow remains stable`; this slice protects the first operator-visible step in that flow by failing closed when the parser entrypoint surface drifts from the catalog.
- `ROADMAP.md` MVP focus: `feat-commands` remains an active lane while `feat-console` stays deferred, so no UI-lane scope is claimed here.
- This diff contributes only the `project-open` entrypoint of the current engine-first CLI smoke route by hardening the public parser surface before the operator proceeds into retrieval, patch-review, persist, and export-handoff.
- Scope-tightening statement: this is operator-surface support for the current CLI smoke route, not new UI work and not broader demo-path expansion beyond the bootstrap contract.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: the bootstrap parser contract for `project-open` must stay deterministic and catalog-locked because CLI remains a first-class operator surface.

### Routing / Provider Impact Note

- None. This diff only hardens local command/demo workflow validation and focused shared test coverage.

### Scope-Check / Ownership Note

- Shared-by-approval edits: `YES`
- Shared-by-approval implementation path included: `tests/unit/test_commands_catalog.py`
- Shared-file approval trace: see the `Approved Exception Note` above; the auditable source in this worktree is the `codex/feat-commands*` shared-test allowlist in `scripts/scope-check.sh` together with the approval-only ownership rule in `THREAD_OWNERSHIP.md`
- Integrator-locked edits: `NO`
- Integrator-locked implementation paths included: `none`
