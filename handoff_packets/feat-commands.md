# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: remove the parser/catalog drift blocker on the canonical `preview and apply or reject a patch` demo-path step by locking the parser-backed review/apply command surface to the canonical catalog and exposing the stable public workflow next-action lookup wrappers that the CLI-first MVP can consume, without adding new engine behavior.
- Risk reason: this is a high-risk/shared-file handoff because it hardens the public command contract in `src/qual/commands/catalog.py`, adds public wrapper exports in `src/qual/commands/workflow.py` and `src/qual/commands/__init__.py`, and uses the explicitly approved shared regression path `tests/unit/test_commands_catalog.py`, so drift at patch-review entrypoints or their published next-action lookup surface would directly weaken the current manual CLI smoke flow.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Harden `command_cli_contract()` so it validates the full grouped parser-surface projection against the canonical catalog instead of trusting derived canonical-name order alone.
2. Expose the stable current-MVP workflow next-action lookup/surface wrappers from `src/qual.commands.workflow` and re-export them from `src.qual.commands` so callers can resolve deterministic follow-up verbs for the manual review/apply/persist/export loop.
3. Add regression coverage for both the parser/catalog drift hard-failure path and the new public workflow next-action lookup surface.
4. Re-run the required gates and record the results for the patch-review CLI compatibility slice.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)

- plan complete: scope stayed pinned to the reviewed implementation slice in `src/qual/commands/catalog.py`, `src/qual/commands/workflow.py`, `src/qual/commands/__init__.py`, and `tests/unit/test_commands_catalog.py`
- first green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed for this handoff slice
- before risky/shared file edit: the only shared path in scope was the approved regression file `tests/unit/test_commands_catalog.py`
- ready for handoff: this packet explicitly maps the reviewed slice to the canonical `preview and apply or reject a patch` step, states that parser/catalog drift plus missing public next-action wrappers on the review/apply loop were the direct blockers removed for that step, and keeps the claim narrowed to CLI compatibility while Textual remains disabled

### Handoff Packet

- branch name: `codex/feat-commands`
- tasks completed (numbered implementation work only; metadata-only packet refreshes excluded):
  1. Hardened `command_cli_contract()` so it validates the full grouped parser-surface projection against the canonical catalog instead of trusting derived canonical-name order alone.
  2. Preserved deterministic patch-review CLI entrypoint ordering by rebuilding grouped entrypoints from the public contract and rejecting alias-level or ordering drift that would otherwise keep canonical names stable.
  3. Added public workflow next-action wrappers in `src/qual/commands/workflow.py` for the current MVP loop so callers can ask the command surface for the stable next actions, lookup table, compatibility table, preferred surface tokens, and parser-ready argv after workflow steps like `review`, `apply`, and `save`.
  4. Re-exported the workflow next-action wrapper surface from `src/qual/commands/__init__.py` so the lane-owned `src.qual.commands` compatibility layer remains the single import surface for CLI/A2UI callers.
  5. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for parser/catalog drift rejection and the new next-action wrapper surface, including alias-level drift that preserves canonical command names, direct mutation of the live CLI parser entrypoint constant, canonical-token replacement with a valid alias in that exported parser surface, and deterministic preferred-surface lookups like `review -> apply-patch|reject-patch` and `save -> export-handoff|export`.
- files changed:
  - reviewed implementation: `src/qual/commands/catalog.py`
  - reviewed implementation: `src/qual/commands/workflow.py`
  - reviewed implementation: `src/qual/commands/__init__.py`
  - reviewed implementation: `tests/unit/test_commands_catalog.py`
  - metadata-only handoff refresh: `THREAD.md`
  - metadata-only handoff refresh: `THREAD_PACKET.md`
  - metadata-only handoff refresh: `handoff_packets/feat-commands.md`
- commands run + outcomes:
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
  - revalidation note: all required gates were rerun on `2026-04-24` for reviewer packet `fixer__feat-commands__20260424T211318Z`, and the reviewer's alias-substitution repro still raises `ValueError: Command CLI catalog entrypoint projection is inconsistent`, confirming the packet stays narrowed to CLI compatibility and the branch includes explicit exported-parser alias-substitution regression coverage for the exact drift concern raised there
- traceability:
  - reviewed implementation slice: `src/qual/commands/catalog.py`, `src/qual/commands/workflow.py`, `src/qual/commands/__init__.py`, and `tests/unit/test_commands_catalog.py`
  - latest runtime command-surface commit included in scope: `de2841102f2cd7c7b3954b3b58abf85d21cdf9b0` (`feat(commands): expose workflow next-action surface lookup`)
  - docs-only refresh commit in branch history: `8391bf07914fffd6fcd29867dc6f21ed25a56ea1` (`docs(thread): pin feat-commands demo-path step`)
  - metadata-only file changed by `8391bf07914fffd6fcd29867dc6f21ed25a56ea1`: `THREAD.md`
  - current packet refresh files: `THREAD_PACKET.md` and `handoff_packets/feat-commands.md`
  - gate rerun verification for this handoff pass was repeated for the current reviewer packet before the metadata refresh commit in this turn
- risks/blockers:
  - risk: future command-surface edits still need to preserve deterministic ordering, fast-fail parser/catalog drift detection, and the preferred next-action wrapper mappings so the patch-review CLI contract stays stable throughout the current manual operator flow
  - blockers: none
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 3 `Product Readiness`: this slice hardens the current manual CLI-first loop specifically at the `preview and apply or reject a patch` step by keeping both the review/apply entrypoints and their immediate public next-action lookups deterministic and migration-safe while `feat-console` stays disabled and the MVP continues to rely on the CLI fallback surface
- canonical demo-path step advanced: `preview and apply or reject a patch` on the active MVP engine-first path (`Engine stability`, `FTS-first retrieval`, `A2UI contracts with CLI fallback`)
- concrete canonical mapping: this slice advances the canonical `preview and apply or reject a patch` step in the current engine-first MVP path `project-open/bootstrap -> retrieval -> plan-or-revise -> apply-or-reject -> export-handoff` by hardening the exact `patch-review -> apply-patch|reject-patch` command surface the operator must use before `persist -> export-handoff` and by exporting the stable public next-action lookup wrappers that tell CLI/A2UI callers which preferred verb is valid next after `review`, `apply`, and `save`, while `feat-console` stays disabled and the MVP continues to depend on `A2UI contracts with CLI fallback`
- concrete canonical-path blocker removed: before this change, alias or token drift could let the operator reach the `preview`, `apply`, or `reject` entrypoints through parser surfaces that no longer matched the canonical catalog even though canonical command names still looked stable, and the public command surface did not expose a stable helper for the immediate next actions on that loop; this slice removes that direct blocker on `preview and apply or reject a patch` by forcing the CLI fallback review/apply step to fail fast on parser/catalog drift and by publishing deterministic next-action wrappers instead of leaving callers to re-derive the follow-up verbs
- lane-fit justification for `de284110`: the new next-action helpers belong in `feat-commands` because they stay entirely inside lane-owned command paths, add no new engine behavior, and only publish wrappers over the existing command catalog/workflow contract so the current CLI-first MVP can resolve follow-up verbs from the canonical commands surface instead of duplicating that mapping elsewhere
- non-claim boundary: this handoff does not claim broader CLI polish, new workflow branches, persistence progress, auditable-state/workflow progress, A2UI contract work, provider routing work, or any new engine behavior beyond exporting the existing canonical next-action command mappings
- vision capability affected:
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface` (`CLI remains a first-class surface` / `engine contracts come first`) and capability 5 `Agent-to-UI protocol (A2UI)` (`CLI remains able to render a text fallback of the same underlying artifacts`): this slice is limited to CLI compatibility for the existing engine-facing review/apply contract at `preview`, `apply`, and `reject`, plus the public next-action wrappers that let CLI/A2UI callers consume the same canonical follow-up verbs, so parser/catalog drift fails fast and the current fallback surface can resolve deterministic next steps while `feat-console` stays disabled; it does not claim auditable-state/workflow progress or broader operator-surface expansion
- routing/provider impact note:
  - none; this change does not touch routing or provider configuration
- traceability note:
  - reviewed implementation approval stays pinned to `src/qual/commands/catalog.py`, `src/qual/commands/workflow.py`, `src/qual/commands/__init__.py`, and `tests/unit/test_commands_catalog.py`
  - runtime command-surface commit `de2841102f2cd7c7b3954b3b58abf85d21cdf9b0` is implementation scope, not docs-only scope
  - docs-only refresh commit `8391bf07914fffd6fcd29867dc6f21ed25a56ea1` changed `THREAD.md` only
  - packet metadata files `THREAD_PACKET.md` and `handoff_packets/feat-commands.md` were refreshed in earlier docs-only commits on this branch and are regenerated here to keep the written handoff aligned with that history
- scope/ownership note:
  - lane-owned implementation path: `src/qual/commands/catalog.py`
  - lane-owned implementation path: `src/qual/commands/workflow.py`
  - lane-owned implementation path: `src/qual/commands/__init__.py`
  - focused regression path: `tests/unit/test_commands_catalog.py`
  - approval/source note: the reviewed implementation claim is pinned to `src/qual/commands/catalog.py`, `src/qual/commands/workflow.py`, `src/qual/commands/__init__.py`, and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` are metadata-only refreshes and do not broaden the approval basis beyond deterministic CLI contract hardening and public next-action wrapper exposure for migration-safe entrypoints
  - shared-test approval record: `scripts/scope-check.sh` lists `tests/unit/test_commands_catalog.py` under `is_approved_shared_test()` for branch `codex/feat-commands*`
  - integrator-locked edits: none
