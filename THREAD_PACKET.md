# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Reviewed implementation commit: `972a3cfa`
- Packet refresh role: `reviewer-fix resubmission refresh 6`
- Review scope: narrow command-contract hardening in `src/qual/commands/catalog.py`, plus focused regression coverage in `tests/unit/test_commands_catalog.py`, with the guardrail explicitly enforcing full parser-surface projection consistency rather than only canonical-name/order consistency.
- Canonical demo-path step advanced: primarily `open project/document` in the active AGENTS demo path, with direct protection for the downstream CLI handoff into `retrieve relevant material`, `preview and apply or reject a patch`, and export-oriented command surfaces because the same contract lock covers `project-open`, `retrieval`, `patch-review`, and `export-handoff` while Textual remains disabled.
- Concrete canonical mapping sentence: this slice makes the existing CLI path `open project/document` -> `retrieve relevant material` -> `preview and apply or reject a patch` more reliable by forcing the parser-backed `project-open` gateway and the downstream grouped entrypoints it feeds to stay aligned with the canonical catalog before the operator starts that loop.
- Non-claim boundary: this resubmission does not claim progress on persistence, A2UI, Textual activation, or any new command reachability; it is limited to command-surface determinism and parser-drift rejection.
- Canonical demo-path context: `AGENTS.md` currently defines the engine-side path as `open project/document` -> `retrieve relevant material` -> `promote or gather context into the basket` -> `produce a plan or revision` -> `preview and apply or reject a patch` -> `persist the updated document/session state` -> `continue working without losing context`.
- Causal link: the Milestone 3 CLI loop cannot begin unless `open project/document` still resolves through the canonical command surface, and the same deterministic catalog contract must remain stable for the later `retrieval`, `patch-review`, and `export-handoff` CLI steps that the operator uses in the same loop while Textual remains disabled.
- Downstream CLI preservation sentence: because Textual remains disabled, the existing CLI-only path from `project-open` into `retrieval`, `patch-review`, and `export-handoff` depends on the `open project/document` gateway staying deterministic; this slice removes the silent parser-drift failure mode that could otherwise break that loop before the operator reaches those later steps.
- AGENTS.md alignment note: this packet explicitly names the exact canonical demo-path step protected by the reviewed slice and ties the claim to the current AGENTS handoff packet and checkpoint requirements.
- Required mapping statement: this `feat-commands` slice is not claiming new workflow reachability; it is migration-safe compatibility hardening for the existing command catalog because `command_cli_contract()` now fails fast when parser/catalog drift would otherwise silently change the operator-facing CLI contract through alias substitution, missing canonical entrypoints, reordered grouped entrypoints, or extra parser-only aliases across the CLI-first MVP loop surfaces for `project-open`, `retrieval`, `patch-review`, and `export-handoff`, preserving the Milestone 3 CLI compatibility requirement while Textual remains disabled.
- Step-1 strengthening sentence: deterministic CLI contract validation makes the `open project/document` step more real because the exact parser-backed entrypoints the operator uses to start project or document state are now forced to match the canonical catalog before the CLI loop begins.
- Demo-path sentence: this change makes the existing CLI path safer to rely on because the concrete parser-backed command entrypoints an operator already uses to open project or document state can no longer silently drift away from the canonical catalog through alias-level or ordering changes.
- Concrete blocker removed: before this slice, parser drift could change the accepted CLI surface without a hard failure, so an operator or smoke check could invoke `project-open`, `retrieval`, `patch-review`, or `export-handoff` through parser-backed aliases or grouped entrypoints that no longer matched the canonical command catalog even though canonical command names still looked correct.
- Review basis scope: keep implementation and approval claims pinned to the live review basis on `codex/feat-commands`, limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`, with the latest implementation evidence coming from the broader parser-surface hardening and direct live-parser regression commits already on this branch.
- Final fixer note: this packet refresh aligns the handoff scope language with the already-landed full parser-surface guardrail, confirms the direct regression coverage against the live CLI parser entrypoint constant remains part of the review basis, and records the green rerun of the required gates from this pass.
- Final verification note: this packet refresh revalidated the corrected handoff packet, confirmed the shipped broader parser-surface validation still matches the stated scope, and reran the full required gate set on branch tip `2e4f68ab` without widening implementation scope.
- Latest implementation evidence note: after reloading the reviewer packet against the live worktree on `2026-04-24`, the parser-surface guardrail remained present on `codex/feat-commands`, including the direct `_CLI_PARSER_ENTRYPOINTS` regression that exercises live parser drift.
- Current fixer pass note: this follow-up pass is metadata-only; it rechecked the live `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py` state, confirmed the reviewer-requested parser-surface guardrail and tests were already committed, and refreshed the handoff wording to match that shipped scope exactly before another required-gates rerun on `2e4f68ab`.
- Reviewer-fix closure note: this refresh exists specifically to satisfy the reviewer-requested handoff field by stating the exact canonical demo-path step advanced, tying that step to the active Milestone 3 CLI-first loop, and keeping the resubmission scoped to packet alignment rather than new implementation work.
- Resubmission note: this pass is metadata-only and exists to regenerate the handoff packet after the reviewer packet reload, keeping the claims pinned to the already-landed parser-surface implementation while recording a fresh full gate rerun on branch tip `2e4f68ab` before re-review.
- Gate rerun confirmation: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` were rerun in this packet-refresh pass.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the existing Milestone 3 CLI gateway deterministic by locking the parser-backed `open project/document` command surface to the canonical catalog without adding new commands or new engine behavior.
- Risk reason: this touches a public command contract in `src/qual/commands/catalog.py` and one focused regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Harden `command_cli_contract()` so the full grouped parser-surface projection is validated against the canonical catalog instead of trusting derived canonical-name order alone.
2. Add regression coverage proving live parser/catalog drift raises a hard failure, including alias-level drift that preserves canonical command names and direct mutation of the live parser entrypoint constant.
3. Refresh the handoff packet so it names the exact canonical demo-path step protected by this contract, explains why the work is migration-safe compatibility hardening rather than second-order cleanup, and makes the alias-level parser-surface-drift scope explicit even when canonical names stay stable.
4. Re-run the required gates and record the results.

### Early Review Triggers

- Before first edit to any shared or integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing or config behavior.

### Stop Triggers

- Unresolved test, lint, or typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (Short Updates)

- Plan complete: scope stayed pinned to the reviewed implementation slice in `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`, with no expansion beyond deterministic CLI-contract hardening for the existing command surface.
- First green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed for this handoff slice.
- Before risky/shared file edit: scope was rechecked against the live review basis on `codex/feat-commands` so the refreshed handoff only describes `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- Ready for handoff: this packet now carries the reviewer-requested exact demo-path mapping using the current Milestone 3 and AGENTS wording, names both the primary `open project/document` step and the downstream CLI loop surfaces it protects, and records the migration-safe compatibility justification without implying any broader lane scope.

## Review Basis

- Implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`

## Commands Run and Outcomes

- `make scope-check`: `PASSED`
- `./quality-format.sh --check`: `PASSED`
- `./quality-lint.sh`: `PASSED`
- `./quality-test.sh`: `PASSED`
- `./typecheck-test.sh`: `PASSED`
- `make ci`: `PASSED`

## Ownership Note

- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Focused regression path: `tests/unit/test_commands_catalog.py`
- Approval/source note: the reviewed implementation claim is pinned to the live branch review basis and only the two implementation files it touched.
- Shared-test approval owner: the integrator-managed branch policy for `codex/feat-commands`.
- Shared-test approved by: the integrator/release ownership gate for `codex/feat-commands`.
- Shared-test approval record: `scripts/scope-check.sh` lists `tests/unit/test_commands_catalog.py` under `is_approved_shared_test()` for branch `codex/feat-commands*`, which is the auditable local approval source for this handoff's only non-owned implementation path.
- Shared-test approval scope: the exception is limited to focused regression coverage in `tests/unit/test_commands_catalog.py`; no other shared or integrator-locked implementation paths are claimed in this slice.
- Integrator-locked edits: `none`
- Scope note: the implementation under review is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` are metadata only.
- Scope clarification: this is command-contract hardening only; it does not add new commands, new engine behavior, new persistence or auditability mechanisms, or a new workflow capability.

## Roadmap and Vision Mapping

- `ROADMAP.md` Milestone 3 `Real workflow loop`: this slice stays within the CLI-compatibility requirement by keeping the existing `project-open`, `retrieval`, `patch-review`, and `export-handoff` entry surfaces deterministic while the package/layout migration lands.
- `ROADMAP.md` lane mapping for `feat-commands`: this slice hardens migration-safe CLI entrypoints only and does not claim broader workflow reachability.
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract`: the active CLI surface now rejects parser/catalog drift before it can silently change the deterministic engine-facing command contract that must remain stable while Textual stays disabled.
