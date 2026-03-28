## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Canonicalize materialized A2UI action order in `src/qual/ui/a2ui.py` so CLI fallback rendering stays deterministic, with matching assertions in `tests/unit/test_a2ui_contract.py`.
- Runtime change commit: `b929fe6c7a1159c7882acedd247aca31a93cd123`
- Handoff scope: metadata-only resubmission on the current branch tip so the roadmap and vision mapping are explicit and reviewer-auditable, including the saved planner handoff state used for future packet emissions.
- Reviewer mapping: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress) and `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`), including the exact requirement that CLI remains able to render a text fallback of the same underlying artifacts.
- Reviewer fix status: required fix `#1` is satisfied on this branch tip because the exact roadmap milestone/scope bullets and product-vision capability are cited directly in the reviewer-facing packets.
- Canon note: the labels above are taken from the current `ROADMAP.md` and `PRODUCT_VISION.md` in this worktree, so the handoff uses the branch's authoritative plan wording rather than older example labels from the review thread.
- Missing handoff fields after reviewer fix `#1`: none; both required plan-alignment fields are populated below for direct audit.

## Plan Alignment

- Roadmap item(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress)
- Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`)
- Roadmap scope bullets: `Add agent-side card/section/action payload generation with deterministic schemas` and `Provide CLI rendering fallback for the same structured payloads`
- Roadmap exit criterion: `A2UI schema/versioning is documented and stable`
- Roadmap task anchor: `ROADMAP.md` `MVP Focus Through 2026-05-04` lists `feat-a2ui-contract` as a current active implementation emphasis under this milestone.
- Vision anchor: `PRODUCT_VISION.md` calls out current MVP emphasis on `A2UI` cards/actions that can be rendered in CLI now and `Exegesis Console` next.
- Audit mapping: the deterministic action-ordering fix stabilizes materialized A2UI action payloads for CLI fallback rendering, which is the concrete Milestone 5 scope-bullet and the Capability 5 requirement that CLI remains able to render a text fallback of the same underlying artifacts.
- Source-of-truth note: reviewer examples were illustrative; the authoritative mapping for this branch tip is the Milestone 5 / Capability 5 pair quoted above from the checked-in plan docs.
- This lane only clarifies the handoff mapping for the A2UI ordering fix; it does not expand scope beyond CLI fallback determinism and the matching contract assertions.
- Tasks completed:
  1. Updated the A2UI materialization path in `src/qual/ui/a2ui.py` to sort filtered actions by canonical JSON before terminal rendering.
  2. Added contract coverage in `tests/unit/test_a2ui_contract.py` for the canonical ordering behavior.
  3. Cleaned up the feature packet and thread packet so the required roadmap and product-vision mappings are explicit and auditable.
  4. Synced `.codex/packet_planner/state.json` and `tests/unit/test_packet_planner.py` so saved and re-emitted packets preserve the same explicit Milestone 5 / Capability 5 mapping.

## Reviewer Required Fix Coverage

1. Required fix `#1`: explicitly name the specific `ROADMAP.md` milestone/task and `PRODUCT_VISION.md` capability for the deterministic action-ordering change.
   Coverage: the `Plan Alignment` section above cites `ROADMAP.md` Milestone 5 scope bullets `Add agent-side card/section/action payload generation with deterministic schemas` and `Provide CLI rendering fallback for the same structured payloads`, plus `PRODUCT_VISION.md` Capability 5 `Agent-to-UI protocol (`A2UI`)`.
   Audit result: the reviewer can verify plan alignment directly from this packet without relying on older example labels or inference.

## Required Handoff Fields

- Roadmap item(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress)
  - Scope bullets: `Add agent-side card/section/action payload generation with deterministic schemas` and `Provide CLI rendering fallback for the same structured payloads`
  - Exit criterion: `A2UI schema/versioning is documented and stable`
  - This fix is the deterministic action-ordering step that keeps the CLI fallback rendering of the same A2UI payloads stable.
- Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`)
  - Agent emits structured presentation artifacts that are consumable by CLI first, then `Exegesis Console`, then future Studio UI.
  - CLI remains able to render a text fallback of the same underlying artifacts.
  - This fix supports that capability by making the materialized action payload deterministic for that CLI text fallback path over the same artifacts.
- Audit mapping: the same ordering fix is the explicit bridge between the Milestone 5 deterministic-schema plus CLI-fallback scope bullets and the Capability 5 requirement that the CLI text fallback render the same underlying A2UI artifacts.
- The roadmap and vision mapping are explicit enough for reviewer audit without relying on inference.
- No other roadmap milestones or product-vision capabilities are implicated by this fix.
- Routing/provider impact note: None.

## Handoff Notes

- The change is intentionally narrow and limited to A2UI action materialization plus its contract assertions.
- CLI fallback rendering remains preserved.
- No routing, provider, or shared/integrator-locked files were changed by this fix.
- Reviewer-response note: this metadata-only follow-up pins the required audit mapping directly to `ROADMAP.md` Milestone 5 scope bullets `Add agent-side card/section/action payload generation with deterministic schemas` and `Provide CLI rendering fallback for the same structured payloads`, plus `PRODUCT_VISION.md` Capability 5 `Agent-to-UI protocol (A2UI)`.
- Reviewer-required plan alignment fields are explicit above and auditable without inference: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress) and `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`).
- This thread packet mirrors the reviewer-facing feature packet so the resubmission is explicit in both places.
- The saved planner handoff state and its regression coverage now use the same explicit mapping as the reviewer-facing packets, so a future re-emission will not drift back to a shortened mapping.
- The matching feature packet lives at `.codex/packets/lanes/feat-a2ui-contract/inbox/feature/F__codex-feat-a2ui-contract__aa875cd03ea2a8e092f527610640827baa7b7b5a__20260320T210541Z.md`.
- This is the final handoff packet for the reviewer-required mapping fix and does not introduce any new scope.
- This closes the reviewer-required mapping fix without changing the scope of the A2UI ordering change.

## Commands Run And Outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS
- Validation was run on the current branch tip during this handoff update.
