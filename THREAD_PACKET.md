# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa`
- Packet refresh role: `fixer re-review packet refresh`
- Packet refresh basis: `regenerated after the reviewer requested parser-surface validation for the public diff-preview entrypoint, matching shared regressions, and a packet scope statement that matches the actual implementation now on this branch`
- Post-fixer verification: `2026-04-24T08:37:05Z UTC gate rerun confirmed this packet refresh matches the current branch state; later docs-only packet refresh commits remain metadata-only`
- Packet-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `handoff_packets/feat-commands.md`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: make the canonical `preview and apply or reject a patch` step more real by keeping the operator-visible `diff-preview` review entrypoint contract locked to the parser/catalog boundary during the current engine-first CLI loop while Textual remains disabled.
- Risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file, and the current implementation basis also exposes default workflow aliases in the same files.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (Completed)

1. Lock the live CLI parser surface to the command catalog so `diff-preview` drift fails closed instead of passing through alias resolution.
2. Add regression coverage for alias-only, missing-token, reordered, and extra-token parser drift, including the `diff-preview` removed / `diff` retained case.
3. Regenerate the handoff packet so the re-review basis points to the current implementation commit, the canonical demo-path mapping is explicit, and the ownership note stays precise.
4. Re-run the required gates and record the outcomes against the unchanged reviewed implementation scope.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Exact implementation basis for re-review:
  - `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa` (`feat(commands): expose default workflow aliases`)
- Reviewer-requested parser-surface fixes included in that reviewed ancestry:
  - `dbb8e0156f3520c759d4d29e2cbbb186013f6df7` (`fix(commands): harden parser surface drift checks`)
  - `6890b8c6d81c7700e84b6cbf9402177d0bafab4f` (`test(commands): lock parser drift regressions to live entrypoints`)
  - `bd118a6c0d7693d58882f74efc8066387bc82189` (`test(commands): cover cached parser surface drift`)
- Current packet refresh traceability: later `docs(commands)` commits are metadata-only and update only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation summary:
  - `_authoritative_cli_entrypoint_projection()` and `_validate_command_cli_contract()` now reject parser/catalog drift when the public `diff-preview` review token disappears, is replaced by alias-only exposure, reorders, or expands unexpectedly.
  - Regression coverage proves the review-step parser surface still fails fast after cache warmup and stays tied to the live parser entrypoints.
  - The current tip also adds direct default-workflow and trusted-surface alias helpers that forward to the current MVP contracts without changing provider or UI behavior.

## Scope Completed

- Hardened the review-step CLI contract so the live parser surface for `diff-preview` must match the declared catalog projection.
- Added parser-drift regressions that cover alias substitution, missing canonical review tokens, extra tokens, and warmed-cache drift cases.
- Exposed the default workflow/trusted-surface alias helpers as thin forwards to the current MVP contract helpers.
- Kept the slice narrow: command-contract hardening, targeted tests, and alias-forwarding helpers only. No provider, routing, persistence, retrieval, or UI-surface behavior changed.

## Canonical Demo-Path Mapping

- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Required AGENTS sentence: this change makes `preview and apply or reject a patch` more real by forcing the review-step public command surface to stay catalog-locked and fail closed before the operator reaches the wrong CLI verb set.
- Concrete blocker removed: the public `diff-preview` preview entrypoint can no longer silently drift to alias-only parser shapes, reordered live parser surfaces, or extra unexpected entrypoints while still resolving through lookup. That removes a concrete CLI-fallback blocker at the operator-visible patch-review step.
- Scope-tightening statement: this slice claims only review-step command-contract hardening. It does not claim new retrieval, persistence, audit-path, export, or broader workflow behavior.
- Current CLI smoke route context: `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff`, entered through `bootstrap --project demo`.
- Smoke-test evidence:
  - `tests/unit/test_commands_catalog.py` proves the live parser surface keeps `diff-preview` before `diff` for the review step and fails fast when `diff-preview` disappears, reorders, or expands while `diff` still resolves to the same canonical command.
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
3. Added thin public alias helpers that forward the default workflow and trusted-surface contract accessors to the current MVP contract helpers.
4. Regenerated the handoff packet so the re-review basis points to commit `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa`, the ownership note stays narrow, and the canonical demo-path step is stated explicitly.
5. Re-ran the required gates and recorded the outcomes against the current reviewed implementation scope.

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
- Gate attribution note: these gates were rerun at `2026-04-24T08:37:05Z UTC` against the current branch state while the reviewed implementation scope is pinned to `4cd1d6b4857ce3da125bb32ae2c76d4b9c41defa`; the current packet refresh itself is metadata-only.

### Risks / Blockers

- Risks:
  - future command-surface changes must keep `_CLI_ENTRYPOINTS` and the shared regression suite aligned or the contract will fail fast by design
- Blockers:
  - none

## Required Handoff Fields

### Canonical demo-path step advanced

- `preview and apply or reject a patch`
- This change makes `preview and apply or reject a patch` more real by keeping the public `diff-preview` preview token catalog-locked instead of letting alias-only drift pass silently in the current engine-first Milestone 3 CLI loop.
- Concrete blocker removal: downstream CLI fallback consumers cannot silently accept a parser surface where `diff-preview` vanished, reordered, or expanded unexpectedly while `diff` still resolves.
- Smoke-test evidence for this step is explicit in `tests/unit/test_commands_catalog.py`: the `diff-preview` drift regressions still fail fast after parser cache warmup.

### Roadmap item(s) affected

- `ROADMAP.md` MVP focus: `feat-commands` remains one of the active implementation lanes in the current MVP push.
- `ROADMAP.md` Milestone 3 `Product Readiness`: this slice contributes to `Define and lock user-facing output contracts`, specifically by keeping the patch-review command surface intentional and stable inside the current CLI loop `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff`.
- Scope-tightening statement: this is engine-contract hardening for the review step plus thin alias forwards for the default workflow/trusted-surface accessors, not broader workflow expansion.

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
