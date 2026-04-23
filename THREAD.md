# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Reviewer-visible implementation anchors are:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
  - `1e04f9633c4abc4988dcb991944680b86f94f753` (`Fix command shim subcommand routing`)
- Intermediate handoff-refresh commits between those implementation anchors are metadata-only for this re-review.
- Review scope stays narrow:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
  - `THREAD.md`
  - `THREAD_PACKET.md`
- The canonical demo-path steps advanced by this reviewed slice are the `vault` and `context` steps inside the current MVP exit criterion `vault -> context -> run -> patch -> export`, concretely through the existing `bootstrap` / `project-open` entrypoint for the `vault` step and the routed `context-basket search` surface for the `context` step while Textual remains disabled.
- Explicit handoff statement: this change makes the canonical demo path more real for `A2UI contracts with CLI fallback` by hardening the existing CLI operator surface for `vault` (`bootstrap` / `project-open`) and `context` (`context-basket search` via the retrieval shim), without claiming that this patch implements `run`, later `patch` / `export` steps, or any new audit/traceability behavior.
- Scope-tightening note: this fixer remains CLI contract hardening only for the existing `bootstrap` / `project-open` and routed retrieval command surfaces that implement the CLI fallback `vault` and `context` steps; for the default catalog it validates full parser-surface token membership and order, while custom-spec helpers still only require canonical coverage/order. It does not add new user-facing command breadth or imply broader workflow progress beyond those steps.
- Concrete blockers removed:
- without validating that the CLI parser entrypoint resolves to the canonical catalog in canonical order, the `bootstrap` / `project-open` surface for the CLI fallback `vault` step could drift silently from the catalog contract and break deterministic smoke tests for that already-in-scope path
- without preserving explicit subcommands when a flow-step shim resolves through the retrieval surface, the CLI fallback `context` step could silently collapse `context-basket search` back to the default list behavior instead of preserving the intended routed action
- Regression proof note: `test_command_cli_contract_rejects_alias_substitution_in_parser_surface_when_canonical_order_still_matches` and `test_command_cli_contract_rejects_extra_alias_entrypoint_when_canonical_order_still_matches` cover the default-catalog token-surface drift guarantee directly.
- Vision capability affected is intentionally narrow: `Canonical engine contract` only.
- This fixer pass stays metadata-only, is limited to `THREAD.md` and `THREAD_PACKET.md`, and re-ran `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` on `2026-04-23` before re-review.
