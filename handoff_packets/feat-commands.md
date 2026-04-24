# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the CLI contract reuses the canonical `command_names()` ordering and raises if the parser surface drifts from the command catalog, then added focused regression coverage for canonical-order alignment and drift rejection in `tests/unit/test_commands_catalog.py`.
- Canonical MVP flow advanced: `vault -> context -> run -> patch -> export` for the manual CLI smoke flow.
- Canonical MVP flow mapping sentence: this `feat-commands` CLI-contract hardening slice strengthens `vault -> context -> run -> patch -> export` by preserving the operator-facing CLI command catalog contract that the manual smoke flow depends on while CLI remains the active first-class surface.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI surface from the catalog while leaving the contract seemingly valid, so an operator could run `vault -> context -> run -> patch -> export` through a CLI contract that had drifted away from the canonical catalog.
- Traceability note: reviewed implementation commit is `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this refresh updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.

## Tasks Completed
1. Hardened `command_cli_contract()` so it validates canonical command names against `command_names()` instead of rebuilding a divergent list from parser lookup output.
2. Preserved canonical CLI contract ordering by returning the validated catalog-order tuple directly.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and parser/catalog drift rejection.
4. Refreshed the lane handoff metadata so it names the exact canonical demo-path step advanced, narrows the claim to CLI-contract hardening, cites the traceable shared-test approval source, and records the re-run gate results for the command-catalog slice.

## Files Changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Commands Run With Results
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed

## Risks / Blockers
- Risks: future command-surface edits still need to preserve the parser/catalog lock so the CLI contract for `vault -> context -> run -> patch -> export` stays deterministic.
- Blockers: none.

## Roadmap Item(s) Affected
- `AGENTS.md` handoff readiness and checkpoint rules because this packet now explicitly names the exact roadmap MVP flow advanced, records the shared-file checkpoint, and keeps the claim limited to the blocker removed for that flow.
- `ROADMAP.md` Milestone 1 `Bootstrap Flow Stabilization` because this is a narrow `feat-commands` command-catalog contract hardening slice that keeps the manual CLI smoke flow `vault -> context -> run -> patch -> export` stable.
- `ROADMAP.md` Milestone 3 `Product Readiness` because this slice helps lock an intentional user-facing output contract by failing fast when the parser-backed CLI surface drifts from the canonical catalog.

## Vision Capability Affected
- `PRODUCT_VISION.md` capability 4 `Operator-first control surface` because the active CLI operator surface now rejects parser/catalog drift before it can silently change the command contract the operator relies on for `vault -> context -> run -> patch -> export`.
- `PRODUCT_VISION.md` current capability alignments because the CLI remains the current operator path while `Exegesis Console` is still next, and this change hardens one real operator flow rather than claiming broader command reachability.

## Routing / Provider Impact Note
- None. This change does not touch routing or provider configuration.

## Scope / Ownership Note
- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Shared-by-approval regression path: `tests/unit/test_commands_catalog.py`
- Approval source: `THREAD_OWNERSHIP.md` marks `tests/unit/test_commands_catalog.py` as shared-by-approval for `codex/feat-commands*`, and `scripts/scope-check.sh` codifies that approval with the branch-specific allowlist entry that explicitly permits the file
- Checkpoint provenance: `THREAD_PACKET.md` preserves the high-risk `before risky/shared file edit` checkpoint showing that the shared regression path was verified against the branch allowlist before shared handoff metadata was refreshed
- Integrator-locked edits: none
- Branch-tip scope note: the implementation under review is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and this handoff file are metadata only.
