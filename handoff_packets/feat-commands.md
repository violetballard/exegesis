# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: wired `src/qual/cli.py` to expose the live parser entrypoint surface from shared command-name constants, then hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the CLI contract reuses the canonical `command_names()` ordering and raises if the live parser surface drifts from the command catalog, plus focused regression coverage for canonical-order alignment and drift rejection in `tests/unit/test_commands_catalog.py`.
- Canonical demo-path step(s) advanced: `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch`
- Canonical MVP flow advanced: `open project/document -> retrieve relevant material -> preview and apply or reject a patch` for the manual CLI smoke flow, via `bootstrap`/`project-open` for open, `context-basket` for retrieval staging, and `diff-preview`/`review-patch` for patch preview.
- Canonical MVP flow mapping sentence: this `feat-commands` CLI-contract hardening slice strengthens the canonical `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch` steps by preserving the operator-facing CLI command catalog contract used by `bootstrap`/`project-open`, `context-basket`, and `diff-preview`/`review-patch` while CLI remains the active first-class surface.
- Demo-path sentence: this change makes the `open project/document -> retrieve relevant material -> preview and apply or reject a patch` loop more real for the CLI-first MVP path because the concrete parser-backed command entrypoints an operator runs now fail fast if parser drift changes the canonical catalog contract.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI surface from the catalog while leaving the contract seemingly valid, so an operator could attempt the `open project/document -> retrieve relevant material -> preview and apply or reject a patch` loop through a CLI contract that had drifted away from the canonical catalog.
- Traceability note: reviewed implementation commit is `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this reviewer-fix follow-up adds parser-surface hardening in `src/qual/cli.py` and `src/qual/commands/catalog.py`, extends regression coverage in `tests/unit/test_commands_catalog.py`, and refreshes the handoff metadata.

## Tasks Completed
1. Wired the live parser entrypoint surface in `src/qual/cli.py` to shared command-name constants so the CLI and contract validation read the same parser source.
2. Hardened `command_cli_contract()` so it validates canonical command names against `command_names()` and the live parser surface instead of duplicated catalog-local entrypoint data.
3. Preserved canonical CLI contract ordering by returning the validated catalog-order tuple directly.
4. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and live parser/catalog drift rejection.

## Packet Refresh Notes
- This handoff now names the exact canonical demo-path step advanced, narrows the claim to CLI-contract hardening, cites the traceable shared-file approval source, and records the re-run gate results for the parser-surface hardening slice.

## Files Changed
- `src/qual/cli.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Commands Run With Results
- `SCOPE_ALLOW_SHARED=1 make scope-check` -> passed
- `SCOPE_ALLOW_SHARED=1 ./quality-format.sh --check` -> passed
- `SCOPE_ALLOW_SHARED=1 ./quality-lint.sh` -> passed
- `SCOPE_ALLOW_SHARED=1 ./quality-test.sh` -> passed
- `SCOPE_ALLOW_SHARED=1 ./typecheck-test.sh` -> passed
- `SCOPE_ALLOW_SHARED=1 make ci` -> passed

## Risks / Blockers
- Risks: future command-surface edits still need to preserve the parser/catalog lock so the CLI contract for `open project/document -> retrieve relevant material -> preview and apply or reject a patch` stays deterministic.
- Scope clarification: this is command-contract hardening only; it does not add new command behavior, new persistence or auditability mechanisms, or a new workflow capability.
- Blockers: none.

## Roadmap Item(s) Affected
- `ROADMAP.md` Milestone 3 `Real workflow loop` because this is a narrow `feat-commands` command-catalog hardening slice that keeps the manual CLI smoke flow `open project/document -> retrieve relevant material -> preview and apply or reject a patch` stable while Textual remains disabled.
- `ROADMAP.md` Milestone 3 exit criterion `CLI can still execute the MVP loop while Textual remains disabled` because this slice helps lock the parser-backed operator command contract by failing fast when the live CLI surface drifts from the canonical catalog.

## Vision Capability Affected
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract` because the active CLI operator surface now rejects parser/catalog drift before it can silently change the command contract the operator relies on for `open project/document -> retrieve relevant material -> preview and apply or reject a patch`.

## Routing / Provider Impact Note
- None. This change does not touch routing or provider configuration.

## Scope / Ownership Note
- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Shared-by-approval parser path: `src/qual/cli.py`
- Shared-by-approval regression path: `tests/unit/test_commands_catalog.py`
- Approval source: `THREAD_OWNERSHIP.md` marks `src/qual/cli.py` and `tests/unit/test_commands_catalog.py` as shared-by-approval for `codex/feat-commands*`, and `scripts/scope-check.sh` codifies those approvals with the branch-specific allowlist entries that explicitly permit the files when `SCOPE_ALLOW_SHARED=1`
- Checkpoint provenance: `THREAD_PACKET.md` preserves the high-risk `before risky/shared file edit` checkpoint showing that both shared paths were verified against the branch allowlist before the parser source and handoff metadata were refreshed
- Integrator-locked edits: none
- Branch-tip scope note: the implementation under review is limited to `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and this handoff file are metadata only.
