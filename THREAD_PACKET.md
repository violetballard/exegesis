# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Verified implementation basis SHA: `3ede0bbf814cbee26464fa671be67b2e3293ab93`
- Submitted tip note: any newer tip created by this handoff refresh is metadata-only packet bookkeeping on top of that verified implementation basis
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: submit the reviewed command-catalog slice only, keeping the handoff limited to deterministic `command_cli_contract()` behavior in `src/qual/commands/catalog.py` plus the repo-policy-allowlisted shared regression coverage in `tests/unit/test_commands_catalog.py`.
- Risk reason: this is a high-risk command-contract handoff because it touches the operator-facing CLI contract and uses a repo-policy-allowlisted shared test file outside the lane-owned path.
- Final validated packet tip before this metadata-only refresh: `c9da1617d`
- Implementation commits already on this branch:
  - `beaf91853` for grouped parser-entrypoint contract validation
  - `4a4d47048` for alias-level parser-surface drift rejection
  - `077764032` for explicit shared regression coverage on stable canonical-name ordering with token drift
  - `3ede0bbf8` for direct live parser contract coverage and additional stable-name drift regressions

### Scope / Plan Alignment

- Canonical demo-path step advanced: `preview and apply or reject a patch` via the existing CLI fallback surface while Textual remains disabled.
- Explicit handoff sentence: This work makes `preview and apply or reject a patch` more real on the current engine-first demo path by locking the parser-facing command contract for the existing patch-review CLI entrypoints so that parser/catalog drift fails fast instead of silently mutating that operator surface; it does not add a new workflow step.
- MVP focus tie-in: this is Milestone 3 CLI-compatibility hardening for one concrete CLI-fallback step in the current engine-first demo path, not new workflow capability or surface-area expansion.
- Concrete blocker removed: without this guard, parser/catalog drift could silently reorder, add, or drop the patch-review CLI tokens that must stay stable for `preview and apply or reject a patch`, so the current MVP CLI fallback could drift away from the real engine contract at the exact step where operators inspect and accept or reject a change.
- Reviewer fix closure:
  1. `command_cli_contract()` validates the full grouped parser-entrypoint projection, not only the deduplicated canonical-name sequence.
  2. `tests/unit/test_commands_catalog.py` exercises the reviewer-requested token-level parser drift cases where canonical-name order still matches: alias substitution, extra parser token, removed parser token, and reordered token within the same canonical command group, plus direct live-parser coverage for `diff` -> `diff-preview` and `context-basket list`.
  3. This packet explicitly names the single canonical demo-path step advanced and states how deterministic command-catalog validation removes a concrete blocker for that step.
- Verified re-review tip before this packet refresh: `3ede0bbf8`
- Final validated handoff tip before this packet refresh: `c9da1617d`
- Verified token-drift coverage on that tip includes alias substitution, extra parser token, removed parser token, and reordered parser tokens within the same canonical command group while canonical-name order stays stable.
- Roadmap alignment: `ROADMAP.md` Milestone 3 exit criterion `Contract changes documented and intentional` plus the `AGENTS.md` rule that contract/infra work only counts when it removes a concrete blocker on the canonical demo path; this handoff is a narrow canonical engine contract and CLI-compatibility hardening change for the existing `preview and apply or reject a patch` step while Textual remains disabled and without claiming new workflow coverage.
- Vision alignment: `PRODUCT_VISION.md` capability 4 `Operator-first control surface` only; this change hardens the current parser/catalog contract that the CLI fallback depends on for the patch-review step and does not claim audit-state or broader workflow progress.
- Non-claim boundary: this handoff claims only deterministic CLI catalog ordering and fail-fast parser-surface drift detection for the existing patch-review command surface; it does not claim parser-entrypoint rewrites, workflow-wrapper additions, diff-preview output work, provider routing changes, storage changes, reachability expansion, or UI-console work.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep `command_cli_contract()` aligned to the canonical command order by reusing the canonical parser projection directly.
2. Reject full parser-surface drift with a fail-fast validation when added, removed, or reordered CLI entrypoint tokens diverge from the catalog.
3. Add focused regression coverage in the allowlisted shared test file for canonical-order alignment plus alias-level parser-surface drift rejection.
4. Refresh the handoff packet so review scope, roadmap mapping, and file list match the reviewed implementation slice exactly.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)

- plan complete: the handoff is narrowed to the reviewed `command_cli_contract()` slice and explicitly mapped to Milestone 3 CLI-compatibility hardening for the existing `preview and apply or reject a patch` step
- first green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` are rerun on this branch after confirming the live parser-projection validation and token-drift coverage remain present
- before risky/shared file edit: the only non-owned path is the repo-policy-allowlisted shared test file `tests/unit/test_commands_catalog.py`
- ready for handoff: the packet names the exact reviewed files, includes the missing canonical demo-path step mapping, and records the concrete scope-gate approval evidence for the only non-owned test path

### Handoff Packet

- branch name: `codex/feat-commands`
- scope completed:
  - hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so deterministic CLI catalog ordering is rebuilt from the grouped parser-entrypoint projection instead of trusting only the deduplicated canonical-name sequence
  - added fail-fast validation in `src/qual/commands/catalog.py` so added, removed, or reordered CLI entrypoint tokens and alias drift raise `ValueError` instead of silently changing the current command surface
  - added focused regression coverage in the allowlisted shared test file `tests/unit/test_commands_catalog.py` for canonical-order alignment plus alias substitution, extra parser token, removed parser token, and reordered token drift rejection on the current parser surface
  - refreshed the handoff packet so the review claim, single-step demo-path mapping, and file list match the reviewed command-catalog slice exactly
- tasks completed (numbered implementation work only; metadata-only packet refreshes excluded):
  1. Hardened `command_cli_contract()` to validate the full grouped parser-entrypoint projection against the catalog.
  2. Preserved canonical command ordering in the returned CLI contract while rejecting added, removed, or reordered parser tokens that would otherwise preserve canonical-name order.
  3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and alias-level parser-surface drift rejection.
- files changed:
  - reviewed implementation: `src/qual/commands/catalog.py`
  - reviewed implementation: `tests/unit/test_commands_catalog.py`
  - metadata-only handoff refresh: `THREAD.md`
  - metadata-only handoff refresh: `THREAD_PACKET.md`
  - metadata-only handoff refresh: `handoff_packets/feat-commands.md`
- commands run + outcomes:
  - reviewed implementation basis SHA `3ede0bbf814cbee26464fa671be67b2e3293ab93` on `2026-04-24`
  - implementation evidence already on this branch:
    - `beaf91853` -> grouped parser-entrypoint contract validation in `src/qual/commands/catalog.py`
    - `4a4d47048` -> alias-level parser-surface drift rejection in `src/qual/commands/catalog.py`
    - `077764032` -> explicit shared regression coverage for stable canonical-name ordering with token drift in `tests/unit/test_commands_catalog.py`
    - `3ede0bbf8` -> direct live parser contract coverage and stable-name parser drift regressions in `tests/unit/test_commands_catalog.py`
  - fixer refresh reruns the required gates on `2026-04-24` in the lane worktree on validated packet tip `c9da1617d`; this refresh updates the handoff evidence, shared-test approval traceability, and single-step plan mapping without widening the reviewed implementation scope
  - verified re-review tip before this packet refresh: `3ede0bbf8`
  - final validated handoff tip before this packet refresh: `c9da1617d`
  - focused reviewer-fix rerun on tip `c9da1617d`: `python -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_extra_accepted_entrypoint_drift tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_removed_expected_alias_entrypoint tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_alias_substitution_in_live_parser_entrypoints tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_reordered_parser_surface tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_lookup_table_matches_the_live_parser_surface tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_matches_the_catalog_order` -> passed
  - targeted reviewer-fix evidence on that tip:
    - live parser alias coverage -> `test_live_parser_diff_alias_matches_catalog_contract`
    - live parser context-basket coverage -> `test_live_parser_context_basket_path_matches_catalog_contract`
    - alias substitution drift rejection -> `test_command_cli_contract_rejects_exported_parser_alias_substitution_with_stable_canonical_names`
    - extra parser token drift rejection -> `test_command_cli_contract_rejects_extra_alias_entrypoint_when_canonical_order_still_matches`
    - removed parser token drift rejection -> `test_command_cli_contract_rejects_missing_canonical_token_when_alias_still_resolves`
    - reordered token-in-group drift rejection -> `test_command_cli_contract_rejects_reordered_parser_projection_when_tokens_change_but_names_do_not`
  - `make scope-check` -> passed without `SCOPE_ALLOW_SHARED=1` because `scripts/scope-check.sh` already allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands`
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
  - gate execution note: bare `python -m pytest` was unavailable in this shell (`No module named pytest`), so verification used the repo-required gate scripts as the source of truth
- risks/blockers:
  - risk: future parser token or alias changes must keep the grouped parser-entrypoint projection aligned with the catalog, or the fail-fast contract will reject the patch-review surface
  - blockers: none
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 3 exit criterion `Contract changes documented and intentional`: preserve the deterministic CLI contract for the existing patch-review operator surface by failing fast when parser/catalog drift mutates the `diff-preview`/`apply-patch`/`reject-patch` command surface
  - `AGENTS.md` contracts/infra rule: this packet names the concrete blocker removed from the canonical demo path instead of claiming broad cross-step progress
- vision capability affected:
  - primary: `PRODUCT_VISION.md` capability 4 `Operator-first control surface`
- routing/provider impact note:
  - none; this change only hardens local command-catalog validation and focused command-catalog tests
- approved exception note:
  - approval record for `tests/unit/test_commands_catalog.py`: `scripts/scope-check.sh` allowlists that file for `codex/feat-commands`; the allowlist entry was added by Violet Ballard in commit `c3a66bb580` (`fix(commands): tighten feat-commands packet and policy`, `2026-03-28`)
  - scope-check handling for this handoff: `make scope-check` passed on the current tip without `SCOPE_ALLOW_SHARED=1` because the repo policy already treats `tests/unit/test_commands_catalog.py` as an approved shared regression test for this lane
  - no other non-owned implementation paths are part of this handoff
- reviewer-fix satisfaction note:
  - required fix 1 is satisfied in `src/qual/commands/catalog.py` by rebuilding and validating the full grouped parser-entrypoint projection against the live parser exported by `src/qual/cli.py` instead of trusting only deduplicated canonical names
  - required fix 2 is satisfied in `tests/unit/test_commands_catalog.py` by explicit live-parser coverage for `diff` -> `diff-preview` and `context-basket list`, plus token-level drift regressions for alias substitution, extra parser token, removed parser token, and reordered token within the same canonical command group while canonical-name order stays stable
  - required fix 3 is satisfied by the explicit single-step demo-path mapping, the concrete patch-review blocker statement, the traced shared-test approval record, and the Milestone 3 CLI-contract framing recorded in this packet
