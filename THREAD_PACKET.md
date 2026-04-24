# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `fixer reviewer packet correction`
- Packet refresh basis: `realigned the handoff to the actual reviewed implementation slice after the reviewer flagged inconsistent traceability, stale roadmap or vision mapping, and a missing explicit patch-step mapping`
- Post-fixer verification: `2026-04-24T09:37:24Z UTC gate rerun confirmed this packet correction matches the current branch state; the current refresh is metadata-only and keeps the reviewed implementation scope pinned to f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `handoff_packets/feat-commands.md`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: make the canonical `preview and apply or reject a patch` step more real by keeping the operator-visible command contract locked to the parser/catalog boundary, so deterministic CLI contract validation protects the current CLI fallback that carries the demo flow while interactive clients stay secondary.
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

- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Required packet statement: this change makes `preview and apply or reject a patch` more real by forcing the command contract to stay catalog-locked and fail closed before the operator reaches the wrong CLI verb set.
- Concrete blocker removed: canonical command-name drift between the parser lookup table and the declared catalog can no longer pass silently. That removes a concrete CLI-fallback blocker at the operator-visible patch-review step.
- `AGENTS.md` compliance note: every active lane task in this packet now names the exact canonical demo-path step it advances, and this handoff states the concrete blocker removed at that step.
- Scope-tightening statement: this slice claims only command-contract hardening for `preview and apply or reject a patch`. Deterministic CLI contract validation preserves the operator-facing command surface needed by the current CLI fallback, and it does not claim new retrieval, persistence, audit-path, export, or broader workflow behavior.
- Current CLI smoke route context: `open project/document -> retrieve relevant material -> promote or gather context into the basket -> produce a plan or revision -> preview and apply or reject a patch -> persist the updated document/session state -> continue working`.
- Smoke-test evidence:
  - `tests/unit/test_commands_catalog.py` proves `command_cli_contract()` returns the canonical command order from `command_names()` and fails fast when canonical-name drift is introduced.
  - `tests/unit/test_commands_catalog.py` also proves the command route coverage stays pinned to the smoke route entry for patch review: `("patch-review", "diff-preview", ("diff-preview", "diff"))` in `test_command_cli_route_summary_tracks_the_smoke_route()` and `test_command_cli_route_contract_tracks_the_smoke_surface()`.
- Plan-alignment note: this slice keeps the explicit patch-step mapping requested by review, while staying aligned to the current roadmap and vision truth sources. `AGENTS.md` operational narrowing rules require each active lane task to name the canonical demo-path step it advances, `ROADMAP.md` keeps `feat-commands` in the active implementation emphasis, Milestone 1 still includes command and diff-preview hardening, and Milestone 5 requires the CLI fallback to execute the MVP flow against the same engine-facing contracts. This guard removes a concrete blocker by failing fast if patch-review command drift would send the operator through the wrong verb set.

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

1. `preview and apply or reject a patch`: locked the live CLI command contract to the command catalog so canonical-name drift fails closed before the operator reaches the patch-review verb set.
2. `preview and apply or reject a patch`: added focused regression coverage for canonical-order alignment and command-catalog drift rejection in `tests/unit/test_commands_catalog.py` so the patch-review CLI surface stays smoke-testable.
3. `preview and apply or reject a patch`: regenerated the handoff packet so the re-review basis points to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, the roadmap or vision mapping stays narrow, and the canonical demo-path step is stated explicitly per reviewer request.
4. `preview and apply or reject a patch`: re-ran the required gates and recorded the outcomes against the current reviewed implementation scope so the packet stays tied to a verified command-contract slice.

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
- Gate attribution note: these gates were rerun at `2026-04-24T09:37:24Z UTC` against the current branch state while the reviewed implementation scope remains pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; the current packet refresh itself is metadata-only.

### Risks / Blockers

- Risks:
  - future command-surface changes must keep `_CLI_ENTRYPOINTS` and the shared regression suite aligned or the contract will fail fast by design
- Blockers:
  - none

## Required Handoff Fields

### Explicit patch-step mapping

- `preview and apply or reject a patch`
- This change makes `preview and apply or reject a patch` more real by keeping the command contract catalog-locked instead of letting canonical-name drift pass silently in the current CLI fallback path.
- Concrete blocker removal: downstream CLI fallback consumers cannot silently accept a contract where the parser-derived canonical command order diverges from the declared command catalog.
- Smoke-test evidence for this step is explicit in `tests/unit/test_commands_catalog.py`: the command contract now matches `command_names()` and raises immediately when canonical-name drift is introduced.

### Roadmap item(s) affected

- `ROADMAP.md` active lane: `feat-commands`
- `ROADMAP.md` Milestone 1 scope: `Command and diff-preview behavior hardening`
- `ROADMAP.md` Milestone 5 exit criterion: `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate`
- Scope-tightening statement: this is CLI contract hardening for `preview and apply or reject a patch`, preserving the operator-facing patch and diff-preview surface rather than broadening workflow behavior.
- Proven command-surface level only: the claimed MVP-loop support is limited to the tested patch-review route entry `patch-review -> diff-preview/diff`, not to retrieval, persistence, export, or broader workflow behavior.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`
- `PRODUCT_VISION.md` capability 5 `Agent-to-UI protocol (A2UI)`
- Exact requirements advanced:
  - `CLI remains a first-class surface for development and reliability.`
  - `CLI remains able to render a text fallback of the same underlying artifacts.`
- This slice narrows to the patch-review command contract only. It does not claim persistence, audit hooks, retrieval, or broader workflow traceability progress.
- Evidence anchor: the claimed product-surface support is the tested patch-review CLI route coverage in `tests/unit/test_commands_catalog.py`, not an unproven broader engine-loop claim.

### Routing / Provider Impact Note

- None. This diff only hardens local command-contract behavior for the current MVP patch-review surface.

### Scope-Check / Ownership Note

- Shared-by-approval edits: `YES`
- Shared-by-approval path included: `tests/unit/test_commands_catalog.py`
- Shared-file approval basis: `THREAD_OWNERSHIP.md` leaves `tests/unit/test_commands_catalog.py` outside the lane-owned path, and `scripts/scope-check.sh` `is_approved_shared_test()` allowlists that shared test file for `codex/feat-commands*`
- Integrator-locked edits: `NO`
- Integrator-locked paths included: `none`
