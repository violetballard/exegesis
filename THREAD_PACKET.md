## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Canonicalize materialized A2UI action order in `src/qual/ui/a2ui.py` so CLI fallback rendering stays deterministic, with matching assertions in `tests/unit/test_a2ui_contract.py`. This handoff explicitly maps to `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress) and `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`) for auditability.
- Roadmap item(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress)
  - Scope bullet: `Add agent-side card/section/action payload generation with deterministic schemas`
  - Exit criterion: `A2UI schema/versioning is documented and stable`
  - This deterministic action-ordering fix is the concrete implementation of that milestone work.
- Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`)
  - Agent emits structured presentation artifacts that are consumable by CLI first, then `Exegesis Console`, then future Studio UI.
  - CLI fallback rendering uses the same structured artifacts.
- Required handoff fields:
  - Roadmap item(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress)
    - Scope bullet: `Add agent-side card/section/action payload generation with deterministic schemas`
    - Exit criterion: `A2UI schema/versioning is documented and stable`
  - Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`)
    - Agent emits structured presentation artifacts that are consumable by CLI first, then `Exegesis Console`, then future Studio UI.
    - CLI fallback rendering uses the same structured artifacts.
- Audit anchor: this fix is intentionally narrow and is the concrete reviewer-required mapping for the deterministic action-ordering change.
- Plan alignment: this lane maps only to `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress), specifically the deterministic schema/payload-generation scope bullet, and `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`); no other roadmap milestones or vision capabilities are implicated.
- Reviewer-required fields are now explicit in this packet, so the handoff no longer depends on inference.
- Roadmap detail: preserve deterministic agent-side card/section/action payload generation while keeping the `A2UI` output contract stable and client-agnostic.
- Vision detail: structured presentation artifacts remain CLI-first and consumable by `Exegesis Console` with the same underlying artifacts.
- Reviewer-required fix satisfied: the roadmap and vision mappings are now explicit in this packet, so the handoff no longer relies on inference.
- No other roadmap milestones or product-vision capabilities are implicated by this fix.
- Scope completed: Updated the A2UI materialization path to sort filtered actions by canonical JSON before rendering, with contract tests covering the deterministic ordering behavior.
- Task summary:
  1. Updated the A2UI materialization path in `src/qual/ui/a2ui.py` to sort filtered actions by canonical JSON before terminal rendering.
  2. Added contract coverage in `tests/unit/test_a2ui_contract.py` to assert the canonical ordering behavior for the materialized payloads.
  3. Rewrote the handoff packet to match the actual diff, removed unrelated packet-maintenance, routing, and UI-shell references, and made the required roadmap/vision anchors explicit for re-review.
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
  - Roadmap item(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress) -> define `A2UI` output contract for agent-produced presentation artifacts, add deterministic agent-side card/section/action payload generation, and provide CLI rendering fallback for the same structured payloads; this deterministic action-ordering fix is the concrete implementation of that item.
  - Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`) -> agent emits structured presentation artifacts that are consumable by CLI first, then `Exegesis Console`, then future Studio UI, including the CLI fallback rendering path used by this fix.
- Canonical plan alignment: this lane maps only to `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress) and `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`); no other roadmap milestones or product-vision capabilities are implicated.
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
