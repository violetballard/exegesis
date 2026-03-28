# Lane Kickoff: feat-a2ui-contract

- Branch: `codex/feat-a2ui-contract`
- Lane/owned paths: `src/qual/ui/a2ui.py`, `tests/unit/test_a2ui_contract.py`
- Scope goal: Canonicalize materialized A2UI action order in `src/qual/ui/a2ui.py` so CLI fallback rendering stays deterministic, with matching assertions in `tests/unit/test_a2ui_contract.py`. This lane maps to `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress), specifically `Add agent-side card/section/action payload generation with deterministic schemas` and `A2UI schema/versioning is documented and stable`, and `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`), specifically CLI-first rendering of structured artifacts with `Exegesis Console` reuse.

## Plan Alignment

- Roadmap item(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress)
  - Scope bullet: `Add agent-side card/section/action payload generation with deterministic schemas`
  - Exit criterion: `A2UI schema/versioning is documented and stable`
- Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`)
  - Agent emits structured presentation artifacts that are consumable by CLI first, then `Exegesis Console`, then future Studio UI.
  - CLI fallback rendering uses the same structured artifacts.

- Audit anchor: this fix is intentionally narrow and is the concrete reviewer-required mapping for the deterministic action-ordering change.
- Scope note: This is a narrow A2UI ordering and contract-coverage update. It does not expand into fallback manifest redesign or broader UI behavior changes.
- Roadmap item(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress)
  - Scope bullet: `Add agent-side card/section/action payload generation with deterministic schemas`
  - Exit criterion: `A2UI schema/versioning is documented and stable`
  - This deterministic action-ordering fix is the concrete implementation of that milestone work.
- Roadmap exit criteria affected: A2UI schema/versioning is documented and stable; core workflows can emit A2UI payloads and CLI fallback views; output contracts are test-covered and backward-compatible by policy.
- No other roadmap milestones are implicated by this fix.
- Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`)
  - Agent emits structured presentation artifacts that are consumable by CLI first, then `Exegesis Console`, then future Studio UI.
  - CLI fallback rendering uses the same structured artifacts.
- No other product-vision capabilities are implicated by this fix.
- These are the reviewer-required plan-alignment mappings for this lane; they replace the prior placeholder form and should remain auditable in the handoff.
- The handoff is intentionally explicit about `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress), specifically its deterministic schema/payload-generation scope bullet, and `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`).
- Canonical plan alignment: this lane maps only to `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress), specifically the deterministic schema/payload-generation scope bullet and stable schema/versioning exit criterion, and `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`).

### Required handoff fields
- Roadmap item(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress) -> scope bullet `Add agent-side card/section/action payload generation with deterministic schemas` and exit criteria `A2UI schema/versioning is documented and stable`; this deterministic action-ordering fix is the concrete implementation of that item.
- Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`) -> agent emits structured presentation artifacts that are consumable by CLI first, then `Exegesis Console`, then future Studio UI, including the CLI fallback rendering path used by this fix.

### Priority outcomes
1. Keep A2UI action ordering canonical in the source path and preserve deterministic CLI fallback rendering.
2. Keep the reviewed file list limited to `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`.
3. Keep the packet language aligned with the canonical ordering change and matching assertions.
4. Keep the handoff mapping explicit so reviewers can audit the roadmap and vision alignment without inference.

### Guardrails
- No unsupported source-code or test-code claims in this kickoff packet.
- Keep the file list auditable against the actual code diff.
- Favor a small, stable A2UI metadata-versioning change over broader fallback or canonicalization work.
- Required-review mapping is explicit: this lane satisfies `ROADMAP.md` Milestone 5: A2UI Presentation Layer (In Progress), specifically the deterministic schema/payload-generation scope bullet, and `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`), including the output-contract stabilization work, deterministic schemas, and CLI fallback contract.
