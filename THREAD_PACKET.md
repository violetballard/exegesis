## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Canonicalize materialized A2UI action order in `src/qual/ui/a2ui.py` so CLI fallback rendering stays deterministic, with matching assertions in `tests/unit/test_a2ui_contract.py`.
- Roadmap item(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress) -> define `A2UI` output contract for agent-produced presentation artifacts, add deterministic schemas, provide CLI rendering fallback for the same structured payloads, keep the surface client-agnostic, and preserve deterministic materialized action ordering.
- Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`) -> agent emits structured presentation artifacts (cards, sections, actions, metadata) that render in CLI first and remain consumable by `Exegesis Console`.
- Audit anchor: this fix is intentionally narrow and is the concrete reviewer-required mapping for the deterministic action-ordering change.
- Roadmap detail: define `A2UI` output contract for agent-produced presentation artifacts, add deterministic schemas, provide CLI rendering fallback for the same structured payloads, keep the surface client-agnostic, and preserve deterministic materialized action ordering.
- Vision detail: the agent emits structured presentation artifacts (cards, sections, actions, metadata) that can be rendered in CLI first and then consumed by `Exegesis Console`.
- Reviewer-required fix satisfied: the roadmap and vision mappings are now explicit in this packet, so the handoff no longer relies on inference.
- No other roadmap milestones or product-vision capabilities are implicated by this fix.
- These are the reviewer-required plan-alignment mappings for this lane; they replace the prior placeholder form and should remain auditable in the handoff.
- Scope completed: Updated the A2UI materialization path to sort filtered actions by canonical JSON before rendering, with contract tests covering the deterministic ordering behavior.
- Task summary:
  1. Updated the A2UI materialization path in `src/qual/ui/a2ui.py` to sort filtered actions by canonical JSON before terminal rendering.
  2. Added contract coverage in `tests/unit/test_a2ui_contract.py` to assert the canonical ordering behavior for the materialized payloads.
  3. Rewrote the handoff packet to match the actual diff and removed unrelated packet-maintenance, routing, and UI-shell references.
- Changed-files list:
  - `src/qual/ui/a2ui.py`
  - `tests/unit/test_a2ui_contract.py`
- Commands run with results:
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- Risks/blockers:
  - No known blockers. The change is constrained to A2UI action materialization and its contract assertions.
  - The only functional risk is accidental over-sorting of materialized actions; the added test coverage guards against unstable ordering.
- Required handoff fields:
  - Roadmap item(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress) -> preserve deterministic materialized action ordering in the A2UI contract, add deterministic schemas, provide CLI rendering fallback for the same structured payloads, and keep the surface client-agnostic.
  - Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`) -> agent emits structured presentation artifacts (cards, sections, actions, metadata) that render in CLI first and remain consumable by `Exegesis Console`.
  - Canonical plan alignment: this lane maps only to Milestone 5 and Capability 5; no other roadmap milestones or product-vision capabilities are implicated.
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
