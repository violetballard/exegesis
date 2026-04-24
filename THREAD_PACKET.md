# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa`
- Packet refresh role: `fixer metadata-only resubmission`
- Packet refresh basis: `regenerated on 2026-04-24T08:19:27Z after the reviewer found that the prior packet pointed at a metadata commit instead of the real latest implementation basis; this refresh now approves the actual implementation tip 4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa, carrying forward the earlier parser-surface hardening from f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Post-fixer verification: `2026-04-24T08:19:27Z UTC gate rerun confirmed this packet refresh matches the current branch state; this refresh changes only THREAD.md, THREAD_PACKET.md, and handoff_packets/feat-commands.md`
- Packet-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `handoff_packets/feat-commands.md`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: make the canonical `preview and apply or reject a patch` step more real by keeping the operator-visible `diff-preview` review entrypoint contract locked to the catalog and by exposing stable default current-MVP workflow aliases for the same review/apply-or-reject branch while Textual remains disabled.
- Risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (Completed)

1. Lock the live CLI parser surface to the command catalog so `diff-preview` drift fails closed instead of passing through alias resolution.
2. Add regression coverage for alias-only, missing-token, reordered, and extra-token parser drift, including the `diff-preview` removed / `diff` retained case.
3. Expose default current-MVP workflow and trusted-surface aliases so consumers use one canonical command-contract surface instead of demo-vs-MVP-specific helper names.
4. Regenerate the handoff packet so the approval basis, canonical demo-path mapping, ownership note, and roadmap/vision scope all match the real branch contents.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Exact implementation basis now approved:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
  - `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa` (`feat(commands): expose default workflow aliases`)
- Current packet refresh traceability: this resubmission is metadata-only and updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/__init__.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation summary:
  - `_CLI_ENTRYPOINTS` and the CLI contract helpers now reject parser/catalog drift when the public `diff-preview` review token disappears, reorders, or expands unexpectedly.
  - The public default aliases `command_workflow_contract()`, `command_workflow_tokens()`, `command_workflow_trusted_tokens()`, `command_trusted_surface_contract()`, `command_trusted_surface_catalog()`, and `command_trusted_surface_tokens()` now resolve to the current MVP workflow contract instead of forcing callers to choose demo-only names.
  - Regression coverage proves those default aliases stay pinned to the current MVP contract and that the review-step parser surface still fails fast after cache warmup.

## Scope Completed

- Hardened the review-step CLI contract so the live parser surface for `diff-preview` must match the declared catalog projection.
- Added parser-drift regressions that cover alias substitution, missing canonical review tokens, extra tokens, and warmed-cache drift cases.
- Exposed default current-MVP workflow aliases and trusted-surface aliases so downstream CLI consumers can call one stable engine contract for the review/apply-or-reject branch.
- Kept the slice narrow: command-contract hardening, default alias exposure, and targeted tests only. No provider, routing, persistence, retrieval, or UI-surface behavior changed.

## Canonical Demo-Path Mapping

- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Concrete blocker removed: the branch now has one stable default current-MVP command contract for the review/apply-or-reject branch, and the public `diff-preview` preview entrypoint can no longer silently drift to alias-only parser shapes while still resolving through lookup. That removes a concrete CLI-fallback blocker at the operator-visible patch-review step.
- Scope-tightening statement: this slice claims only review-step command-contract hardening and current-MVP alias stability. It does not claim new retrieval, persistence, audit-path, export, or broader workflow behavior.
- Current CLI smoke route context: `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff`, entered through `bootstrap --project demo`.
- Smoke-test evidence:
  - `tests/unit/test_commands_catalog.py` proves the live parser surface keeps `diff-preview` before `diff` for the review step and fails fast when `diff-preview` disappears while `diff` still resolves to the same canonical command.
  - The same test module proves the public default workflow/trusted-surface aliases stay equal to the current MVP contract, so the review/apply-or-reject branch is exposed through one canonical default helper surface.
- Plan-alignment note: while Textual remains disabled, the CLI fallback still has to carry the operator path. This slice makes the `preview and apply or reject a patch` step more real by locking the review-step token surface and the default workflow aliases to the same current-MVP engine contract.

## Approved Exception Note

- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval owner: the integrator-managed branch policy for `codex/feat-commands`
- Approval source: `scripts/scope-check.sh` `is_approved_shared_test()` branch allowlist for `codex/feat-commands*`
- Additional ownership source: `THREAD_OWNERSHIP.md` keeps lane ownership on `src/qual/commands/**`; no integrator-locked files are part of this slice
- Approval basis: shared regression coverage is required to prove both the review-step parser contract and the public current-MVP alias surface
- Scope-check allowance used: `not required`
- Integrator-locked edits in this slice: `none`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Locked the live review-step parser surface to the command catalog so `diff-preview` drift fails closed.
2. Added parser-drift regression coverage for alias-only, missing-token, extra-token, and cache-warm drift cases in `tests/unit/test_commands_catalog.py`.
3. Added public default current-MVP workflow aliases and trusted-surface aliases in `src/qual/commands/catalog.py`, exported them from `src/qual/commands/__init__.py`, and added tests proving those aliases stay equal to the current MVP contract.
4. Regenerated the handoff packet so the approval basis matches the real branch contents and the ownership / roadmap / vision mapping stays narrow.

### Files Changed

- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
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
- Gate attribution note: these gates were rerun at `2026-04-24T08:19:27Z UTC` against the branch state that includes implementation tip `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa`; the current packet refresh is metadata-only.

### Risks / Blockers

- Risks:
  - future command-surface changes must keep `_CLI_ENTRYPOINTS`, the default current-MVP alias exports, and the shared regression suite aligned or the contract will fail fast by design
- Blockers:
  - none

## Required Handoff Fields

### Canonical demo-path step advanced

- `preview and apply or reject a patch`
- This change makes `preview and apply or reject a patch` more real by exposing one default current-MVP helper surface for the review/apply-or-reject branch and by keeping the public `diff-preview` preview token catalog-locked instead of letting alias-only drift pass silently.
- Concrete blocker removal: downstream CLI fallback consumers no longer need to guess between demo-specific and MVP-specific helper names for the current review/apply-or-reject branch, and they cannot silently accept a parser surface where `diff-preview` vanished but `diff` still resolves.
- Smoke-test evidence for this step is explicit in `tests/unit/test_commands_catalog.py`: the `diff-preview` drift regressions still fail fast, and the new public-alias tests prove the default workflow/trusted-surface exports remain pinned to the current MVP contract.

### Roadmap item(s) affected

- `ROADMAP.md` MVP focus: `feat-commands` remains one of the active implementation lanes in the current MVP push.
- `ROADMAP.md` Milestone 3 `Product Readiness`: this slice contributes only to `Define and lock user-facing output contracts`, specifically by keeping the public command/workflow alias surface intentional and stable.
- `ROADMAP.md` Milestone 5 `A2UI Presentation Layer`: this slice supports the exit criterion that `CLI can execute the MVP flow ...` by keeping the CLI review/apply-or-reject contract deterministic while Textual remains deferred.
- Scope-tightening statement: this is CLI compatibility and engine-contract hardening for the review step, not broader workflow expansion.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: the CLI remains the first-class operator surface while interactive clients are deferred.
- `PRODUCT_VISION.md` current alignment note: `Engine` contracts come first and the future `Exegesis Console` builds on top of them. This slice narrows to one current-MVP command-contract surface for the patch-review branch and does not claim any new audit or persistence capability.

### Routing / Provider Impact Note

- None. This diff only hardens local command-contract behavior and public alias exposure for the current MVP workflow surface.

### Scope-Check / Ownership Note

- Shared-by-approval edits: `YES`
- Shared-by-approval path included: `tests/unit/test_commands_catalog.py`
- Shared-file approval trace: `scripts/scope-check.sh` `is_approved_shared_test()` allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`
- Integrator-locked edits: `NO`
- Integrator-locked paths included: `none`
