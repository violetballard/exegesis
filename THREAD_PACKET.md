# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `aef67223fb2ea280860de95d2a860880630a84dd`
- Packet refresh role: `reviewer-fix packet refresh`
- Packet refresh basis: `regenerated on 2026-04-24 for re-review against the fixer delta that locks the live parser surface to the command catalog, replaces helper-only drift coverage with live _CLI_ENTRYPOINTS drift checks, and states the canonical demo-path step explicitly`
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
2. Tighten CLI contract validation so live parser entrypoints must match the declared catalog projection, including alias substitution and reordered token failures.
3. Replace helper-only regression coverage with live `_CLI_ENTRYPOINTS` drift tests that stay resolvable through lookup but still fail fast.
4. Regenerate the handoff packet with one concrete canonical demo-path step and an explicit shared-test approval source.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Reviewed implementation commit: `aef67223fb2ea280860de95d2a860880630a84dd` (`fix(commands): lock parser surface contract`).
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation summary:
  - `_CLI_ENTRYPOINTS` now locks the live default parser token surface independently from `COMMAND_SPECS`, so default CLI drift can be detected instead of re-derived from the same spec source.
  - `_validated_cli_entrypoints_for()` and `command_cli_contract()` now validate the actual parser surface against the declared catalog projection before exposing canonical names, tokens, or lookup tables.
  - focused regression tests now patch `_CLI_ENTRYPOINTS` into alias-substituted, reordered, and extra-entrypoint shapes to prove the contract fails fast even when lookup resolution still lands on the same canonical commands.

## Scope Completed

- Locked the default parser surface to `_CLI_ENTRYPOINTS` so `command_cli_contract()` checks the live parser token contract instead of comparing only spec-derived canonical-name order.
- Hardened validation so alias substitution, parser reordering, or extra accepted tokens fail fast even when the drifted tokens still resolve back to the same canonical commands.
- Added live parser-drift regression coverage by patching `_CLI_ENTRYPOINTS` into drifted-but-still-resolvable shapes.
- Kept the slice narrow: command-surface contract hardening plus targeted tests only, with no provider, routing, storage, retrieval, or terminal workflow behavior changes.

## Canonical Demo-Path Mapping

- Primary canonical demo-path step advanced now: `project-open` (`bootstrap` the session).
- Explicit canonical demo-path statement required for re-review: this slice advances the canonical `project-open` bootstrap step first, and no other demo-path step is claimed as newly implemented here.
- Primary-step scope note: this packet advances `project-open` first while hardening the parser contract reused by later loop steps.
- Current engine-first MVP path statement: while Textual remains disabled, the active operator path stays `vault -> context -> run -> patch -> export` through the CLI fallback against the same engine PolicyGate.
- One-line plan alignment: this change makes `project-open` more real by ensuring the operator-facing bootstrap verb cannot silently drift to alias-only entrypoints while still resolving through lookup.
- Active MVP operator path strengthened: the existing CLI smoke route entrypoint into `project-open -> retrieval -> patch -> export` while Textual remains disabled.
- Concrete blocker removed: before this guard, the live parser surface for the current CLI smoke route could drift from `bootstrap` to an alias such as `open` and still resolve through lookup, leaving automation and operator runbooks pointed at a changed public surface without any fail-fast signal.
- Direct plan-alignment statement: this change makes the `project-open` bootstrap step more real by failing closed when the parser-facing entrypoint contract no longer matches the cataloged command surface.
- Scope-tightening note: this handoff claims only parser-surface drift detection plus focused regression coverage for the primary `project-open` entrypoint contract; it does not claim new retrieval quality, patch semantics, persistence behavior, or export behavior.
- Traceability note: `aef67223fb2ea280860de95d2a860880630a84dd` is the implementation tip for this reviewed slice. `THREAD.md` and `THREAD_PACKET.md` are packet refresh companions that capture the updated reviewer-fix mapping and gate results.
- Why this is milestone-worthy now instead of second-order cleanup: the roadmap requires the CLI to execute the MVP `vault -> context -> run -> patch -> export` loop while Textual remains disabled. This guard removes a concrete reliability blocker at the loop entrypoint by preventing silent parser-surface drift before the operator even starts the bootstrap step.

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
3. Reworked parser-drift regression coverage in `tests/unit/test_commands_catalog.py` to patch `_CLI_ENTRYPOINTS` into drifted-but-still-resolvable shapes.
4. Regenerated the handoff packet so the reviewer-requested canonical demo-path step, roadmap/vision tie-in, and shared-test approval source are explicit.

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

### Risks / Blockers

- Risks:
  - future command-surface additions must update `_CLI_ENTRYPOINTS` and parser-drift coverage together or the contract will fail fast by design
- Blockers:
  - none

## Required Handoff Fields

### Canonical demo-path step advanced

- `project-open` (`bootstrap` the session)
- This change makes `project-open` more real by keeping the operator-facing bootstrap command surface catalog-locked instead of allowing alias-only parser drift to pass silently.
- Concrete blocker removal: the contract now fails fast if the live parser entrypoint for bootstrap or its peers drifts to a different accepted token set while still resolving through lookup.

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 3 exit criterion: `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate`.
- This diff contributes the `project-open` entrypoint of that exact loop by hardening the public parser surface before the operator proceeds into retrieval, patch, and export.
- `feat-commands`: keep migration-safe command entrypoints deterministic so the active Milestone 3 lane can still exercise the reviewed CLI loop through its cataloged bootstrap surface while Textual remains disabled.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: the CLI remains a first-class reliability surface, so the bootstrap parser surface must stay deterministic instead of depending on alias fallback drift.
- `PRODUCT_VISION.md` capability 5 `Agent-to-UI protocol (A2UI)`: artifacts must be consumable by CLI first, so the parser-ready command contract needs to stay stable for both CLI fallback rendering and later Console consumption.

### Routing / Provider Impact Note

- None. This diff only hardens local command/demo workflow validation and focused shared test coverage.

### Scope-Check / Ownership Note

- Shared-by-approval edits: `YES`
- Shared-by-approval implementation path included: `tests/unit/test_commands_catalog.py`
- Shared-file approval trace: see the `Approved Exception Note` above; the auditable source in this worktree is the `codex/feat-commands*` shared-test allowlist in `scripts/scope-check.sh` together with the approval-only ownership rule in `THREAD_OWNERSHIP.md`
- Integrator-locked edits: `NO`
- Integrator-locked implementation paths included: `none`
