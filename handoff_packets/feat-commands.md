# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the existing CLI contract validates the full grouped parser-surface projection against the canonical catalog, rejects alias substitution, missing canonical entrypoints, reordered grouped entrypoints, and extra parser-only aliases, and raises if the parser-backed catalog surface drifts, plus focused regression coverage for parser-surface drift rejection in `tests/unit/test_commands_catalog.py`.
- Scope summary: this commit does not add new commands, new workflow coverage, or new engine behavior; it only makes parser/catalog drift fail fast for the existing command surface, including alias-level and ordering drift that would otherwise preserve canonical command names while changing the actual parser surface.
- Canonical demo-path step advanced: `open project/document` in the active AGENTS demo path, with this slice keeping the operator-facing CLI entry surface deterministic at the point where the Milestone 3 loop begins.
- Canonical demo-path context: `AGENTS.md` currently defines the engine-side path as `open project/document` -> `retrieve relevant material` -> `promote or gather context into the basket` -> `produce a plan or revision` -> `preview and apply or reject a patch` -> `persist the updated document/session state` -> `continue working without losing context`.
- Causal link: the Milestone 3 CLI loop cannot begin unless `open project/document` still resolves through the canonical command surface, so making parser/catalog drift fail fast hardens that gateway without claiming broader workflow advancement.
- Deterministic validation sentence: deterministic CLI contract validation directly strengthens the `open project/document` step because it fails fast before the operator starts the workflow through a parser surface that no longer matches the canonical catalog.
- Canonical MVP flow mapping sentence: this `feat-commands` slice is migration-safe compatibility hardening only; it tightens the existing command catalog contract so parser/catalog drift cannot silently break the CLI gateway operators use at `open project/document`, even when the parser surface changes without changing canonical command names.
- Step-1 strengthening sentence: deterministic CLI contract validation makes the `open project/document` step more real because the exact parser-backed entrypoints the operator uses to open project or document state are now forced to match the canonical catalog before the CLI loop begins.
- Demo-path sentence: this change keeps the operator-facing CLI entry surface aligned with the canonical catalog at `open project/document`, even if someone accidentally swaps aliases, reorders grouped entrypoints, or adds parser-only aliases.
- Canonical wording lock: this handoff intentionally uses the current Milestone 3 and AGENTS wording for the active engine-side demo path rather than older CLI MVP flow terminology.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the existing CLI surface from the catalog while leaving the contract seemingly valid, so an operator could begin the CLI workflow through an `open project/document` surface that no longer matched the canonical command catalog.
- Traceability note: reviewed implementation commit is `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, and its implementation scope is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; this follow-up commit refreshes handoff metadata only after another green rerun of the required gates from this fixer pass.
- Final verification note: this metadata-only fixer rerun on `2026-04-24` revalidated the reviewer-requested demo-path mapping, aligned the packet wording to the already-landed full parser-surface guardrail, and reran the full required gate set without changing the reviewed implementation files.
- Latest fixer rerun note: after the reviewer-fixer prompt was reloaded against the live worktree on `2026-04-24`, the packet was checked again and the same demo-path mapping plus explicit high-risk rationale remained intact before another full required gate rerun.
- Current fixer pass note: this follow-up pass rechecked the live `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py` state, verified that the reviewer-requested parser-surface guardrail and alias-drift regressions were already present, and limited the new work to another metadata refresh plus a fresh rerun of the required gates.
- Gate rerun confirmation: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed again in this metadata-only fixer handoff.

## Tasks completed (numbered)
1. Hardened `command_cli_contract()` so it validates the full grouped parser-surface projection against the canonical catalog instead of trusting derived canonical-name order alone.
2. Preserved deterministic CLI contract ordering by rebuilding grouped entrypoints from the public contract and rejecting alias-level or ordering drift that would otherwise keep canonical names stable.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for parser/catalog drift rejection, including alias-level drift that preserves canonical command names.

## Packet Refresh Notes
- This handoff now names the single roadmap step advanced using the current canonical roadmap wording, states why the work is migration-safe compatibility hardening for the existing catalog instead of second-order cleanup, makes the alias-level parser-surface-drift scope explicit even when canonical names stay stable, and keeps the approval basis pinned to reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` plus its two implementation files only.
- Packet regeneration and metadata refresh remain here for traceability and are intentionally excluded from the numbered implementation task list above.
- This revalidation pass confirmed the packet still satisfies the reviewer-requested demo-path mapping, explicit high-risk rationale, and AGENTS-compliant task framing after a fresh green rerun of the required gates from the current branch tip.
- This fixer execution re-checked the live worktree, confirmed the parser-surface guardrail and regression coverage were already present, and therefore limited this follow-up to another metadata-only verification refresh instead of inventing additional implementation churn.

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
- Risks: future command-surface edits still need to preserve the parser/catalog lock so the existing `open project/document` CLI contract stays deterministic at the start of the active Milestone 3 workflow.
- Scope clarification: this is command-contract hardening only; it does not add new commands, new engine behavior, new persistence or auditability mechanisms, or a new workflow capability.
- Blockers: none.

## Roadmap Item(s) Affected
- `ROADMAP.md` Milestone 3 `Real workflow loop`: this slice stays within the CLI-compatibility requirement by keeping the existing `open project/document` entry surface deterministic while the package/layout migration lands.
- `ROADMAP.md` lane mapping for `feat-commands`: this slice hardens migration-safe CLI entrypoints only and does not claim broader workflow reachability.

## Vision Capability Affected
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract` because the existing CLI surface now rejects parser/catalog drift before it can silently change the command contract the operator relies on while Textual remains disabled.

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
