# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the existing CLI contract validates the full grouped parser-surface projection against the canonical catalog, rejects alias substitution, missing canonical entrypoints, reordered grouped entrypoints, and extra parser-only aliases, and raises if the parser-backed catalog surface drifts; added focused regression coverage for that parser-surface drift rejection in `tests/unit/test_commands_catalog.py`.
- Scope summary: this is CLI compatibility hardening for the active MVP loop while Textual remains disabled. It does not add new commands, new engine behavior, or new workflow reachability.
- Canonical demo-path step advanced: `preview and apply or reject a patch`
- Concrete canonical mapping: this slice makes `preview and apply or reject a patch` more real by forcing the parser-backed patch-review entrypoints to match the canonical catalog before review commands run, so parser/catalog drift fails fast instead of silently mutating the operator-facing CLI surface.
- Canonical demo-path context: `AGENTS.md` defines the engine-side path as `open project/document` -> `retrieve relevant material` -> `promote or gather context into the basket` -> `produce a plan or revision` -> `preview and apply or reject a patch` -> `persist the updated document/session state` -> `continue working without losing context`.
- Roadmap tie-in: this is Milestone 3 CLI compatibility work for the real workflow loop, specifically at the patch-review step while Textual remains disabled.
- Non-claim boundary: this handoff does not claim progress on persistence, A2UI, Textual activation, or any new command reachability.
- High-risk framing note: this remains a high-risk handoff because it hardens a public command contract in `src/qual/commands/catalog.py` and uses the explicitly approved shared regression path `tests/unit/test_commands_catalog.py`.

## Tasks completed (numbered)
1. Hardened `command_cli_contract()` so it validates the full grouped parser-surface projection against the canonical catalog instead of trusting derived canonical-name order alone.
2. Preserved deterministic patch-review CLI entrypoint ordering by rebuilding grouped entrypoints from the public contract and rejecting alias-level or ordering drift that would otherwise keep canonical names stable.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for parser/catalog drift rejection, including alias-level drift that preserves canonical command names and direct mutation of the live CLI parser entrypoint constant.

## Packet Scope Notes
- Packet refresh work is intentionally excluded from the numbered task list above; the counted lane work is command-contract hardening plus regression coverage only.
- The re-review claim is limited to CLI compatibility hardening for the existing patch-review step, not generic command-catalog maintenance.

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
- Risks: future command-surface edits still need to preserve the parser/catalog lock so the patch-review CLI contract stays deterministic throughout the active Milestone 3 workflow.
- Blockers: none.

## Roadmap Item(s) Affected
- `ROADMAP.md` Milestone 3 `Real workflow loop`: this slice keeps the patch-review entry surface deterministic for the CLI-first MVP loop while the package/layout migration lands.
- `ROADMAP.md` lane mapping for `feat-commands`: this slice hardens migration-safe CLI entrypoints only and does not claim broader workflow reachability.

## Vision Capability Affected
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract`: the existing CLI surface now rejects parser/catalog drift before it can silently change the engine-facing command contract that must remain stable while Textual remains disabled.

## Routing / Provider Impact Note
- None. This change does not touch routing or provider configuration.

## Scope / Ownership Note
- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Focused regression path: `tests/unit/test_commands_catalog.py`
- Approval/source note: the reviewed implementation claim is pinned to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and this handoff file are metadata-only refreshes.
- Shared-test approval record: `scripts/scope-check.sh` lists `tests/unit/test_commands_catalog.py` under `is_approved_shared_test()` for branch `codex/feat-commands*`.
- Integrator-locked edits: none.
