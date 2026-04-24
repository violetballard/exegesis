# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `fixer reviewer packet correction`
- Packet refresh basis: `realigned the handoff to the actual reviewed implementation slice after the reviewer flagged inconsistent traceability, overbroad roadmap or vision mapping, and a missing explicit canonical demo-path statement`
- Post-fixer verification: `2026-04-24T09:26:05Z UTC gate rerun confirmed this packet correction matches the current branch state; the current refresh is metadata-only and keeps the reviewed implementation scope pinned to f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `handoff_packets/feat-commands.md`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: make the `patch` segment of the current MVP CLI fallback flow more real by keeping the operator-visible command contract locked to the parser/catalog boundary, so `preview and apply or reject a patch` stays deterministic inside the active `vault -> context -> run -> patch -> export` engine path.
- Risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Lock the live CLI parser surface to the command catalog so canonical-name drift fails closed instead of silently changing the operator-facing contract.
2. Add regression coverage for canonical-order alignment and catalog-drift rejection in the command contract tests.
3. Regenerate the handoff packet so the re-review basis points to the actual implementation commit, the canonical demo-path mapping is explicit, and the roadmap or vision mapping stays narrow.
4. Re-run the required gates and record the outcomes against the unchanged reviewed implementation scope.

### Early Review Triggers

- before first edit to any shared or integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing or config behavior

### Stop Triggers

- unresolved test, lint, or typecheck failure after `2` focused fix attempts
- unresolved `make scope-check`
- budget, size, or time limit hit

### High-Risk Audit Note

- Shared-test exception reason: the regression proving contract drift rejection lives in `tests/unit/test_commands_catalog.py`, which is shared-by-approval rather than lane-owned.
- Command-contract risk reason: this slice hardens the operator-visible parser/catalog boundary in `src/qual/commands/catalog.py`, so the stricter high-risk kickoff template applied even though the code change stayed narrow.
- Auditability result: the risk reason, early review triggers, stop triggers, scope goal, 4-task cap, and approval basis are now all recorded directly in the handoff artifacts for re-review.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Exact implementation basis for re-review:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
- Current packet refresh traceability: later `docs(commands)` commits are metadata-only and update only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation summary:
  - `command_cli_contract()` now validates that the canonical command names derived from the live CLI lookup table stay identical to `command_names()`, and raises `ValueError` when the parser surface drifts from the catalog.
  - Regression coverage proves the command contract stays aligned to canonical catalog order and fails fast if canonical-name drift is introduced.

## Scope Completed

- Hardened `command_cli_contract()` so the canonical command names derived from the live CLI lookup table must match `command_names()`.
- Added focused regressions for canonical-order alignment and command-catalog drift rejection.
- Kept the slice narrow: command-contract hardening and targeted tests only. No provider, routing, persistence, retrieval, or UI-surface behavior changed.

## Canonical Demo-Path Mapping

- Canonical demo-path step advanced: `patch` in the current MVP flow `vault -> context -> run -> patch -> export`.
- Required AGENTS sentence: this change makes the `patch` step more real by forcing `preview and apply or reject a patch` to stay catalog-locked and fail closed before the operator reaches the wrong CLI verb set.
- Concrete blocker removed: canonical command-name drift between the parser lookup table and the declared catalog can no longer pass silently. That removes a concrete CLI-fallback blocker at the operator-visible patch step of the current MVP flow.
- Scope-tightening statement: this slice claims only CLI fallback contract hardening for the `patch` step of the active MVP flow. It preserves the operator-facing command surface required by the current engine plus A2UI-with-CLI-fallback push, and it does not claim new retrieval, persistence, audit-path, export, or broader workflow behavior.
- Current CLI smoke route context: `vault -> context -> run -> patch -> export`.
- Smoke-test evidence:
  - `tests/unit/test_commands_catalog.py` proves `command_cli_contract()` returns the canonical command order from `command_names()` and fails fast when canonical-name drift is introduced.
  - `tests/unit/test_commands_catalog.py` also proves the command route coverage stays pinned to the smoke route entry for patch review: `("patch-review", "diff-preview", ("diff-preview", "diff"))` in `test_command_cli_route_summary_tracks_the_smoke_route()` and `test_command_cli_route_contract_tracks_the_smoke_surface()`.
- Plan-alignment note: the active MVP note targets `A2UI contracts with CLI fallback`, and `ROADMAP.md` requires the CLI to execute the MVP flow `vault -> context -> run -> patch -> export`. This slice makes the `patch` step more real by locking the command contract before the operator reaches `preview and apply or reject a patch`, and it does so without claiming broader workflow progress.

## Approved Exception Note

- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval owner: the integrator-managed branch policy for `codex/feat-commands`
- Approval source: `scripts/scope-check.sh` `is_approved_shared_test()` branch allowlist for `codex/feat-commands*`
- Additional ownership source: `THREAD_OWNERSHIP.md` keeps lane ownership on `src/qual/commands/**`; the non-owned test edit is a shared-by-approval exception with explicit branch allowlist approval, not an integrator-locked edit
- Approval basis: shared regression coverage is required to prove the review-step parser contract
- Scope-check allowance used: `not required`
- Integrator-locked edits in this slice: `none`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. `patch`: locked the live CLI command contract to the command catalog so canonical-name drift fails closed before the operator reaches `preview and apply or reject a patch`.
2. `patch`: added focused regression coverage for canonical-order alignment and command-catalog drift rejection in `tests/unit/test_commands_catalog.py` so the patch-step CLI surface stays smoke-testable.
3. `patch`: regenerated the handoff packet so the re-review basis points to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, the roadmap or vision mapping stays narrow, and the canonical demo-path step is stated explicitly per reviewer request.
4. `patch`: re-ran the required gates and recorded the outcomes against the current reviewed implementation scope so the packet stays tied to a verified command-contract slice.

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
- Gate attribution note: these gates were rerun at `2026-04-24T09:26:05Z UTC` against the current branch state while the reviewed implementation scope remains pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; the current packet refresh itself is metadata-only.

### Risks / Blockers

- Risks:
  - future command-surface changes must keep `_CLI_ENTRYPOINTS` and the shared regression suite aligned or the contract will fail fast by design
- Blockers:
  - none

## Required Handoff Fields

### Canonical demo-path step advanced

- `patch` in the current MVP flow `vault -> context -> run -> patch -> export`
- This change makes the `patch` step more real by keeping `preview and apply or reject a patch` catalog-locked instead of letting canonical-name drift pass silently in the current CLI fallback path.
- Concrete blocker removal: downstream CLI fallback consumers cannot silently accept a contract where the parser-derived canonical command order diverges from the declared command catalog.
- Smoke-test evidence for this step is explicit in `tests/unit/test_commands_catalog.py`: the command contract now matches `command_names()` and raises immediately when canonical-name drift is introduced.

### Roadmap item(s) affected

- `ROADMAP.md` active MVP focus lane: `feat-commands`
- `ROADMAP.md` Milestone 5 exit criterion: `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate`
- `AGENTS.md` active MVP note: `A2UI contracts with CLI fallback`
- Scope-tightening statement: this is CLI contract hardening for the `patch` step of the active MVP flow, preserving the operator-facing command surface during the current A2UI-plus-CLI-fallback push rather than broadening workflow behavior.
- Proven command-surface level only: the claimed support for the CLI-first MVP loop is limited to the tested patch-review route entry `patch-review -> diff-preview/diff`, not to retrieval, persistence, export, or broader workflow behavior.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`
- Exact requirement advanced: `CLI remains a first-class surface for development and reliability.`
- Supporting current-alignment wording: `Current MVP emphasis is on Engine output contracts, FTS-backed retrieval, and A2UI cards/actions that can be rendered in CLI now and Exegesis Console next.`
- This slice narrows to the patch-review command contract only. It does not claim persistence, audit hooks, A2UI payload generation, or broader workflow traceability progress.
- Evidence anchor: the claimed product-surface support is the tested patch-review CLI route coverage in `tests/unit/test_commands_catalog.py`, not an unproven broader engine-loop claim.

### Routing / Provider Impact Note

- None. This diff only hardens local command-contract behavior for the current MVP patch-review surface.

### Scope-Check / Ownership Note

- Shared-by-approval edits: `YES`
- Shared-by-approval path included: `tests/unit/test_commands_catalog.py`
- Shared-file approval basis: `THREAD_OWNERSHIP.md` leaves `tests/unit/test_commands_catalog.py` outside the lane-owned path, and `scripts/scope-check.sh` `is_approved_shared_test()` allowlists that shared test file for `codex/feat-commands*`
- Integrator-locked edits: `NO`
- Integrator-locked paths included: `none`
