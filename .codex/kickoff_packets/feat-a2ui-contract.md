# Lane Kickoff: feat-a2ui-contract

- Branch: `codex/feat-a2ui-contract`
- Lane/owned paths: `src/qual/ui/a2ui.py`, `tests/unit/test_a2ui_contract.py`
- Scope goal: Canonicalize materialized A2UI action order in `src/qual/ui/a2ui.py` so CLI fallback rendering stays deterministic, with matching assertions in `tests/unit/test_a2ui_contract.py`.

## Plan Alignment

- Roadmap item(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress) -> task `Add agent-side card/section/action payload generation with deterministic schemas` and exit criterion `A2UI schema/versioning is documented and stable`.
- Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`) -> agent emits structured presentation artifacts that are consumable by CLI first, then `Exegesis Console`, then future Studio UI, including the CLI fallback rendering path used by this fix.
- These are the reviewer-required handoff mappings for this lane and are now explicit in the kickoff packet as well as the review packet.

## Handoff Requirements

- CLI rendering fallback must remain preserved for all A2UI changes.
- Action handling must remain typed, allowlisted, and engine-authoritative.
- Required gate results must be reported before integration.

## Notes

- This lane is intentionally narrow and does not change routing or provider configuration.
- The required roadmap task and vision capability are explicit above so the handoff can be audited without inference.
