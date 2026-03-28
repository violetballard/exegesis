## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Canonicalize materialized A2UI action order in `src/qual/ui/a2ui.py` so CLI fallback rendering stays deterministic, with matching assertions in `tests/unit/test_a2ui_contract.py`.
- Roadmap task(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress) -> `Define A2UI output contract for agent-produced presentation artifacts`, `Add agent-side card/section/action payload generation with deterministic schemas`, and `Provide CLI rendering fallback for the same structured payloads`.
- Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`) -> structured presentation artifacts (cards, sections, actions, metadata) must be consumable by CLI first, then `Exegesis Console`, then future Studio UI.
- Required handoff fields:
  - Roadmap item(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress) -> deterministic materialized action ordering, stable `A2UI` schemas, and CLI rendering fallback for agent-produced presentation artifacts
  - Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`) -> CLI-first rendering of structured presentation artifacts with `Exegesis Console` reuse
- Audit anchor: this fix is intentionally narrow and is the concrete reviewer-required mapping for the deterministic action-ordering change.
- Plan alignment: this lane maps to `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress) and `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`), with no other roadmap milestones or vision capabilities implicated.
- Roadmap detail: preserve deterministic materialized action ordering while keeping the `A2UI` output contract stable and client-agnostic.
- Vision detail: structured presentation artifacts remain CLI-first and consumable by `Exegesis Console` with stable action ordering.
- Reviewer-required fix satisfied: the roadmap and vision mappings are now explicit in this packet, so the handoff no longer relies on inference.
- Required handoff fields, stated explicitly for re-review:
  - Roadmap task(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress) -> deterministic materialized action ordering, stable `A2UI` schemas, and CLI rendering fallback for agent-produced presentation artifacts.
  - Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`) -> CLI-first rendering of structured presentation artifacts with `Exegesis Console` reuse.
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
  - Roadmap task(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress) -> deterministic agent-side card/section/action payload generation and CLI fallback rendering.
  - Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`) -> structured presentation artifacts rendered in CLI first and reused by `Exegesis Console`.
  - Canonical plan alignment: this lane maps only to Milestone 5 and Capability 5; no other roadmap milestones or product-vision capabilities are implicated.
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
