# Lane Kickoff: feat-a2ui-contract

- Branch: `codex/feat-a2ui-contract`
- Lane/owned paths: `src/qual/ui/a2ui.py`, `tests/unit/test_a2ui_contract.py`
- Scope goal: Canonicalize materialized A2UI action order in `src/qual/ui/a2ui.py` so CLI fallback rendering stays deterministic, with matching assertions in `tests/unit/test_a2ui_contract.py`. This maps directly to `ROADMAP.md` Milestone 5: A2UI Presentation Layer, specifically the output-contract and CLI-fallback items, plus `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`).
- Scope note: This is a narrow A2UI ordering and contract-coverage update. It does not expand into fallback manifest redesign or broader UI behavior changes.
- Roadmap item(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer - define `A2UI` output contract for agent-produced presentation artifacts, add deterministic schemas, and provide CLI rendering fallback for the same structured payloads.
- Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`) - the agent emits structured presentation artifacts (cards, sections, actions, metadata) that remain consumable by CLI first, then `Exegesis Console`, then future Studio UI.

### Priority outcomes
1. Keep A2UI action ordering canonical in the source path and preserve deterministic CLI fallback rendering.
2. Keep the reviewed file list limited to `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`.
3. Keep the packet language aligned with the canonical ordering change and matching assertions.
4. Keep the handoff mapping explicit so reviewers can audit the roadmap and vision alignment without inference.

### Guardrails
- No unsupported source-code or test-code claims in this kickoff packet.
- Keep the file list auditable against the actual code diff.
- Favor a small, stable A2UI metadata-versioning change over broader fallback or canonicalization work.
