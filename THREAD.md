# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow `feat-commands` CLI-contract hardening in `src/qual/commands/catalog.py`, plus focused regressions in `tests/unit/test_commands_catalog.py`; this slice locks `command_cli_contract()` to the existing canonical catalog surface, rejects alias-level and ordering drift across the grouped parser surface, and preserves the deterministic entrypoint projection the operator already uses.
- Scope clarification: this is migration-safe compatibility hardening for the existing CLI-first loop while Textual remains disabled; it does not add new commands, new engine behavior, persistence or auditability work, or any new workflow capability.
- Canonical demo-path step advanced: `open project/document` via stable CLI entrypoints in the active AGENTS demo path.
- Concrete canonical mapping sentence: this slice makes the existing `open project/document` CLI gateway more real by forcing the parser-backed `project-open` entrypoints to stay aligned with the canonical catalog before the operator starts the loop, with downstream protection for later CLI-only steps if that gateway would otherwise drift.
- Non-claim boundary: this resubmission does not claim progress on persistence, A2UI, Textual activation, or any new command reachability; it is limited to deterministic CLI compatibility and parser-drift rejection for the existing command surface.
- Canonical demo-path context: `AGENTS.md` currently defines the engine-side path as `open project/document` -> `retrieve relevant material` -> `promote or gather context into the basket` -> `produce a plan or revision` -> `preview and apply or reject a patch` -> `persist the updated document/session state` -> `continue working without losing context`.
- Causal link: if the `open project/document` command surface drifts away from the canonical catalog without a hard failure, the operator cannot reliably start the Milestone 3 CLI-first loop while Textual remains disabled.
- Downstream CLI preservation sentence: because Textual remains disabled, preserving deterministic compatibility at the `open project/document` gateway also protects later CLI-only steps from inheriting parser drift that starts at the gateway.
- Explicit re-review statement: this `feat-commands` slice is not claiming new workflow reachability; it is migration-safe compatibility hardening for the existing command catalog because `command_cli_contract()` now fails fast when parser/catalog drift would otherwise silently change the operator-facing CLI contract through alias substitution, missing canonical entrypoints, reordered grouped entrypoints, or extra parser-only aliases at the existing `project-open` gateway, preserving the deterministic CLI compatibility Milestone 3 requires while Textual remains disabled.
- Step strengthening sentence: deterministic CLI contract validation makes the `open project/document` step more real because the exact parser-backed entrypoints the operator uses to start the workflow are now forced to match the canonical catalog before the rest of the loop begins.
- Demo-path sentence: this change makes the existing CLI path safer to rely on because the concrete parser-backed command entrypoints an operator already uses to open project or document state can no longer silently drift away from the canonical catalog through alias-level or ordering changes.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI contract from the canonical catalog, so an operator or smoke check could invoke `project-open`, `retrieval`, `patch-review`, or `export-handoff` through parser-backed aliases or grouped entrypoints that no longer matched the expected contract even though canonical command names still looked correct.
- Final fixer note: this pointer remains implementation-scoped to the live reviewed implementation files on `codex/feat-commands`; the broader parser-surface guardrail and the direct live-parser regression already landed, and this packet refresh keeps the handoff aligned to that branch state.
- Final verification note: this packet refresh rechecked the corrected handoff mapping against the current Milestone 3 CLI-compatibility wording, confirmed the broader parser-surface validation plus direct live-parser drift coverage remain present, and reran the full required gate set on the current branch tip without widening the reviewed implementation slice.
- Latest implementation evidence note: the live worktree was re-read from the reviewer packet on `2026-04-24`, and the branch still contains the parser-surface guardrail plus the direct `_CLI_PARSER_ENTRYPOINTS` regression that proves alias-level parser drift fails even when canonical names stay stable.
- Current fixer pass note: this follow-up pass is metadata-only; it rechecked the live reviewed implementation files, confirmed that the reviewer-requested parser-surface validation and tests were already committed, and refreshed the packet language to match that shipped scope exactly before another required-gates rerun on the current branch tip.
- Reviewer-fix closure note: this refresh explicitly answers the reviewer by naming the canonical `open project/document` demo-path step, tightening the claim to deterministic CLI compatibility hardening while Textual remains disabled, anchoring the product mapping to `PRODUCT_VISION.md` capability 3 `Canonical engine contract`, and keeping the resubmission metadata-only.
- Resubmission note: the implementation basis remains the already-landed parser-surface guardrail plus live parser-entrypoint regression, while this pass only regenerates the handoff packet so re-review is anchored to refreshed branch metadata and a new full gate rerun from the current branch tip.
- Gate rerun confirmation: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` were rerun in this packet-refresh pass.
- Current revalidation note: this fixer pass re-read the reviewer packet from `fixer__feat-commands__20260424T180716Z.prompt.txt`, confirmed the exact `open project/document` demo-path mapping is present in the live handoff metadata, reran the full required gates on the current branch tip, and keeps this pointer aligned to the new metadata-only resubmission commit.
- Shared-test approval provenance: the only non-owned implementation path, `tests/unit/test_commands_catalog.py`, is covered by the integrator-managed `codex/feat-commands` branch policy and the integrator/release ownership gate recorded locally in `scripts/scope-check.sh` under `is_approved_shared_test()` for `codex/feat-commands*`.
- Reviewed implementation evidence: `14cb4cde`, `beaf9185`, and `2446deb4` on `codex/feat-commands`
- Reviewed implementation files: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`
- Approval basis note: implementation approval remains pinned to those two reviewed files only; this pointer file is metadata-only for the packet refresh.

## Reviewed Files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

## Required Gates

- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
