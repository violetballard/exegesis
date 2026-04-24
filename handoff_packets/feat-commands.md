# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the CLI contract reuses the canonical `command_names()` ordering and raises if the parser surface drifts from the command catalog, then added focused regression coverage for canonical-order alignment and drift rejection in `tests/unit/test_commands_catalog.py`.
- Canonical MVP flow advanced: `open project/document -> retrieve relevant material -> preview and apply or reject a patch` for the manual CLI smoke flow, via `bootstrap`/`project-open` for open, `context-basket` for retrieval staging, and `diff-preview`/`review-patch` for patch preview.
- Canonical MVP flow mapping sentence: this `feat-commands` CLI-contract hardening slice strengthens the canonical `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch` steps by preserving the operator-facing CLI command catalog contract used by `bootstrap`/`project-open`, `context-basket`, and `diff-preview`/`review-patch` while CLI remains the active first-class surface.
- Demo-path sentence: this change makes the `preview and apply or reject a patch` step more real for the CLI-first MVP loop because the concrete command entrypoints an operator runs now fail fast if parser drift changes the canonical catalog contract.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI surface from the catalog while leaving the contract seemingly valid, so an operator could attempt the `open project/document -> retrieve relevant material -> preview and apply or reject a patch` loop through a CLI contract that had drifted away from the canonical catalog.
- Traceability note: reviewed implementation commit is `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this refresh updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.

## Tasks Completed
1. Hardened `command_cli_contract()` so it validates canonical command names against `command_names()` instead of rebuilding a divergent list from parser lookup output.
2. Preserved canonical CLI contract ordering by returning the validated catalog-order tuple directly.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and parser/catalog drift rejection.

## Packet Refresh Notes
- Metadata refresh only: this handoff now names the exact canonical demo-path step advanced, narrows the claim to CLI-contract hardening, cites the traceable shared-test approval source, and records the re-run gate results for the command-catalog slice.

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
- Risks: future command-surface edits still need to preserve the parser/catalog lock so the CLI contract for `open project/document -> retrieve relevant material -> preview and apply or reject a patch` stays deterministic.
- Blockers: none.

## Roadmap Item(s) Affected
- `AGENTS.md` handoff readiness and checkpoint rules because this packet now explicitly names the exact roadmap MVP flow advanced, records the shared-file checkpoint, and keeps the claim limited to the blocker removed for that flow.
- `ROADMAP.md` Milestone 3 `Real workflow loop` because this is a narrow `feat-commands` command-catalog hardening slice that keeps the manual CLI smoke flow `open project/document -> retrieve relevant material -> preview and apply or reject a patch` stable while Textual remains disabled.
- `ROADMAP.md` exit criterion `CLI can still execute the MVP loop while Textual remains disabled` because this slice helps lock an intentional user-facing output contract by failing fast when the parser-backed CLI surface drifts from the canonical catalog.

## Vision Capability Affected
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract` because the active CLI operator surface now rejects parser/catalog drift before it can silently change the command contract the operator relies on for `open project/document -> retrieve relevant material -> preview and apply or reject a patch`.
- `PRODUCT_VISION.md` near-term product truth because the CLI remains the current operator path while Textual stays disabled, and this change hardens one real operator flow rather than claiming broader command reachability.

## Routing / Provider Impact Note
- None. This change does not touch routing or provider configuration.

## Scope / Ownership Note
- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Shared-by-approval regression path: `tests/unit/test_commands_catalog.py`
- Approval source: `THREAD_OWNERSHIP.md` marks `tests/unit/test_commands_catalog.py` as shared-by-approval for `codex/feat-commands*`, and `scripts/scope-check.sh` codifies that approval with the branch-specific allowlist entry that explicitly permits the file
- Checkpoint provenance: `THREAD_PACKET.md` preserves the high-risk `before risky/shared file edit` checkpoint showing that the shared regression path was verified against the branch allowlist before shared handoff metadata was refreshed
- Integrator-locked edits: none
- Branch-tip scope note: the implementation under review is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and this handoff file are metadata only.
