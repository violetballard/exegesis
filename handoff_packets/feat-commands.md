# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the existing CLI contract validates the full grouped parser-surface projection against the canonical catalog, rejects alias substitution, missing canonical entrypoints, reordered grouped entrypoints, and extra parser-only aliases, and raises if the parser-backed catalog surface drifts, plus focused regression coverage for parser-surface drift rejection in `tests/unit/test_commands_catalog.py`.
- Scope summary: this commit does not add new commands, new workflow coverage, or new engine behavior; it only makes parser/catalog drift fail fast for the existing command surface, including alias-level and ordering drift that would otherwise preserve canonical command names while changing the actual parser surface.
- Canonical demo-path step advanced: CLI compatibility for the already-modeled loop that starts at `open project/document` and continues through `retrieve relevant material` to `preview and apply or reject a patch`, so the CLI can still execute the MVP loop while Textual remains disabled.
- Canonical MVP flow context: `open project/document -> retrieve relevant material -> preview and apply or reject a patch` remains the same manual CLI smoke flow, and this slice only hardens the parser-backed CLI compatibility surface that starts and therefore gates that path while Textual remains disabled.
- Canonical MVP flow mapping sentence: this `feat-commands` slice is migration-safe compatibility hardening only; it tightens the existing command catalog contract so parser/catalog drift cannot silently break the CLI compatibility required while Textual remains disabled for the `open project/document -> retrieve relevant material -> preview and apply or reject a patch` loop, even when the parser surface changes without changing canonical command names.
- Demo-path sentence: this change keeps the operator-facing CLI entry surface aligned with the canonical catalog so the downstream `retrieve relevant material` and `preview and apply or reject a patch` steps remain reachable through the same deterministic CLI loop while Textual remains disabled, even if someone accidentally swaps aliases, reorders grouped entrypoints, or adds parser-only aliases.
- Canonical wording lock: this handoff intentionally uses the exact reviewer-requested framing, namely that the CLI can still execute the MVP loop while Textual remains disabled and that CLI compatibility is required while Textual remains disabled.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the existing CLI surface from the catalog while leaving the contract seemingly valid, so an operator could begin the manual MVP flow through an `open project/document` surface that no longer matched the canonical command catalog.
- Traceability note: reviewed implementation commit is `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, and its implementation scope is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; this follow-up commit refreshes handoff metadata only after a second green rerun of the required gates.
- Final verification note: a metadata-only fixer pass on `2026-04-24` revalidated the reviewer-requested demo-path mapping, aligned the packet wording to the already-landed full parser-surface guardrail, and reran the full required gate set without changing the reviewed implementation files.
- Gate rerun confirmation: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` were rerun successfully from the current branch tip before this metadata-only fixer handoff.

## Tasks Completed
1. Hardened `command_cli_contract()` so it validates the full grouped parser-surface projection against the canonical catalog instead of trusting derived canonical-name order alone.
2. Preserved deterministic CLI contract ordering by rebuilding grouped entrypoints from the public contract and rejecting alias-level or ordering drift that would otherwise keep canonical names stable.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for parser/catalog drift rejection, including alias-level drift that preserves canonical command names.

## Packet Refresh Notes
- This handoff now names the exact canonical demo-path step advanced, locks the CLI/Textual wording to the reviewer-requested phrasing, states why the work is migration-safe compatibility hardening for the existing catalog instead of second-order cleanup, and keeps the approval basis pinned to reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` plus its two implementation files only.

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
- Risks: future command-surface edits still need to preserve the parser/catalog lock so the existing `open project/document` CLI contract stays deterministic.
- Scope clarification: this is command-contract hardening only; it does not add new commands, new engine behavior, new persistence or auditability mechanisms, or a new workflow capability.
- Blockers: none.

## Roadmap Item(s) Affected
- `ROADMAP.md` Milestone 3 lane mapping `feat-commands: CLI compatibility and migration-safe entrypoints` because this slice hardens the existing command catalog contract without adding new workflow reachability.
- `ROADMAP.md` Milestone 3 exit criterion `CLI can still execute the MVP loop while Textual remains disabled` because deterministic parser/catalog alignment keeps the operator-facing `open project/document` entry surface stable for the CLI-first loop.

## Vision Capability Affected
- `PRODUCT_VISION.md` capability 4 `Operator-first control surface` because the existing CLI surface now rejects parser/catalog drift before it can silently change the command contract the operator relies on, and CLI compatibility is required while Textual remains disabled.

## Routing / Provider Impact Note
- None. This change does not touch routing or provider configuration.

## Scope / Ownership Note
- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Focused regression path: `tests/unit/test_commands_catalog.py`
- Approval/source note: the reviewed implementation claim is pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and only the two implementation files it touched: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`
- Shared-test approval owner: the integrator-managed branch policy for `codex/feat-commands`
- Shared-test approved by: the integrator/release ownership gate for `codex/feat-commands`
- Shared-test approval record: `scripts/scope-check.sh` lists `tests/unit/test_commands_catalog.py` under `is_approved_shared_test()` for branch `codex/feat-commands*`, which is the auditable local approval source for the only non-owned implementation path in this handoff.
- Shared-test approval scope: focused regression coverage in `tests/unit/test_commands_catalog.py` only.
- Integrator-locked edits: none
- Branch-tip scope note: the implementation under review is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and this handoff file are metadata only.
