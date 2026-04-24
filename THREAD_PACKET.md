# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `fixer metadata-only resubmission`
- Packet refresh basis: `regenerated on 2026-04-24T08:29:45Z after the reviewer requested three packet corrections: state the canonical demo-path step explicitly, describe the test edit as shared-by-approval rather than integrator-locked, and keep re-review pinned to commit f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Post-fixer verification: `2026-04-24T08:29:45Z UTC gate rerun confirmed this packet refresh matches the current branch state; this refresh changes only THREAD.md, THREAD_PACKET.md, and handoff_packets/feat-commands.md while keeping re-review scope pinned to f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `handoff_packets/feat-commands.md`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: make the canonical `preview and apply or reject a patch` step more real by keeping the operator-visible `diff-preview` review entrypoint contract locked to the catalog during the current engine-first CLI loop while Textual remains disabled.
- Risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (Completed)

1. Lock the live CLI parser surface to the command catalog so `diff-preview` drift fails closed instead of passing through alias resolution.
2. Add regression coverage for alias-only, missing-token, reordered, and extra-token parser drift, including the `diff-preview` removed / `diff` retained case.
3. Regenerate the handoff packet so the re-review basis stays pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, the canonical demo-path mapping is explicit, and the ownership note stays precise.
4. Re-run the required gates and record the outcomes against the unchanged reviewed implementation scope.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Exact implementation basis now approved:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
- Current packet refresh traceability: this resubmission is metadata-only and updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` while keeping re-review pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation summary:
  - `_CLI_ENTRYPOINTS` and the CLI contract helpers now reject parser/catalog drift when the public `diff-preview` review token disappears, reorders, or expands unexpectedly.
  - Regression coverage proves the review-step parser surface still fails fast after cache warmup.

## Scope Completed

- Hardened the review-step CLI contract so the live parser surface for `diff-preview` must match the declared catalog projection.
- Added parser-drift regressions that cover alias substitution, missing canonical review tokens, extra tokens, and warmed-cache drift cases.
- Kept the slice narrow: command-contract hardening and targeted tests only. No provider, routing, persistence, retrieval, or UI-surface behavior changed.

## Canonical Demo-Path Mapping

- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Required AGENTS sentence: this change makes `preview and apply or reject a patch` more real by forcing the review-step public command surface to stay catalog-locked and fail closed before the operator reaches the wrong CLI verb set.
- Concrete blocker removed: the public `diff-preview` preview entrypoint can no longer silently drift to alias-only parser shapes while still resolving through lookup. That removes a concrete CLI-fallback blocker at the operator-visible patch-review step.
- Scope-tightening statement: this slice claims only review-step command-contract hardening. It does not claim new retrieval, persistence, audit-path, export, or broader workflow behavior.
- Current CLI smoke route context: `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff`, entered through `bootstrap --project demo`.
- Smoke-test evidence:
  - `tests/unit/test_commands_catalog.py` proves the live parser surface keeps `diff-preview` before `diff` for the review step and fails fast when `diff-preview` disappears while `diff` still resolves to the same canonical command.
  - The same test module proves the drift checks still fail fast after parser cache warmup.
- Plan-alignment note: while Textual remains disabled, the CLI fallback still has to carry the operator path. This slice makes the `preview and apply or reject a patch` step more real by locking the review-step token surface to the same current engine-first Milestone 3 loop.

## Approved Exception Note

- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval owner: the integrator-managed branch policy for `codex/feat-commands`
- Approval source: `scripts/scope-check.sh` `is_approved_shared_test()` branch allowlist for `codex/feat-commands*`
- Additional ownership source: `THREAD_OWNERSHIP.md` keeps lane ownership on `src/qual/commands/**`; the non-owned test edit is a shared-by-approval exception, not an integrator-locked edit
- Approval basis: shared regression coverage is required to prove the review-step parser contract
- Scope-check allowance used: `not required`
- Integrator-locked edits in this slice: `none`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Locked the live review-step parser surface to the command catalog so `diff-preview` drift fails closed.
2. Added parser-drift regression coverage for alias-only, missing-token, extra-token, and cache-warm drift cases in `tests/unit/test_commands_catalog.py`.
3. Regenerated the handoff packet so the re-review basis stays pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, the ownership note stays narrow, and the canonical demo-path step is stated explicitly.
4. Re-ran the required gates and recorded the outcomes against the unchanged reviewed implementation scope.

### Files Changed

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

### Commands Run and Outcomes

- `make scope-check`: `PASSED`
- `./quality-format.sh --check`: `PASSED`
- `./quality-lint.sh`: `PASSED`
- `./quality-test.sh`: `PASSED`
- `./typecheck-test.sh`: `PASSED`
- `make ci`: `PASSED`
- Gate attribution note: these gates were rerun at `2026-04-24T08:29:45Z UTC` against the current branch state while the reviewed implementation scope remains pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; the current packet refresh is metadata-only.

### Risks / Blockers

- Risks:
  - future command-surface changes must keep `_CLI_ENTRYPOINTS` and the shared regression suite aligned or the contract will fail fast by design
- Blockers:
  - none

## Required Handoff Fields

### Canonical demo-path step advanced

- `preview and apply or reject a patch`
- This change makes `preview and apply or reject a patch` more real by keeping the public `diff-preview` preview token catalog-locked instead of letting alias-only drift pass silently in the current engine-first Milestone 3 CLI loop.
- Concrete blocker removal: downstream CLI fallback consumers cannot silently accept a parser surface where `diff-preview` vanished but `diff` still resolves.
- Smoke-test evidence for this step is explicit in `tests/unit/test_commands_catalog.py`: the `diff-preview` drift regressions still fail fast after parser cache warmup.

### Roadmap item(s) affected

- `ROADMAP.md` MVP focus: `feat-commands` remains one of the active implementation lanes in the current MVP push.
- `ROADMAP.md` Milestone 3 `Product Readiness`: this slice contributes only to `Define and lock user-facing output contracts`, specifically by keeping the patch-review command surface intentional and stable inside the current CLI loop `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff`.
- Scope-tightening statement: this is engine-contract hardening for the review step, not broader workflow expansion.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: the CLI remains the first-class operator surface while interactive clients are deferred.
- `PRODUCT_VISION.md` current alignment note: `Engine` contracts come first and the future `Exegesis Console` builds on top of them. This slice narrows to the patch-review command-contract surface and does not claim any new audit or persistence capability.

### Routing / Provider Impact Note

- None. This diff only hardens local command-contract behavior for the current MVP patch-review surface.

### Scope-Check / Ownership Note

- Shared-by-approval edits: `YES`
- Shared-by-approval path included: `tests/unit/test_commands_catalog.py`
- Shared-file approval trace: `scripts/scope-check.sh` `is_approved_shared_test()` allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`
- Integrator-locked edits: `NO`
- Integrator-locked paths included: `none`
