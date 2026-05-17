# Lane Kickoff: feat-a2ui-contract

- Branch: `codex/feat-a2ui-contract`
- Lane/owned paths: `src/qual/ui/a2ui.py`, `tests/unit/test_a2ui_contract.py`
- Scope goal: Canonicalize materialized A2UI action order in `src/qual/ui/a2ui.py` so CLI fallback rendering stays deterministic for the engine-side Milestone 3 workflow loop, with matching assertions in `tests/unit/test_a2ui_contract.py`.

### Current Canon Mapping

- Roadmap item affected: `ROADMAP.md` Milestone 3: Real workflow loop.
- Roadmap lane mapping: `feat-a2ui-contract` supports shared card/action contracts and selection models for the engine loop.
- Vision capability affected: `PRODUCT_VISION.md` Capability 4: Shared UI contract (`A2UI`).
- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Audit mapping: deterministic A2UI action ordering keeps CLI fallback patch preview, apply, and reject affordances stable while the engine loop remains the source of authority.

### Priority outcomes

1. Keep card/action schemas deterministic and versionable.
2. Make CLI fallback rendering reliable for the demo loop.
3. Keep contract work in service of the engine loop instead of leading product scope.

### Definition of done

- Shared action, card, and selection structures are stable enough for engine outputs.
- CLI can consume the same structures that future UI work will consume.
- Contract shape does not force UI-specific assumptions into the engine.

### Do not spend time on

- The full final A2UI protocol.
- Presentation richness before the engine loop is standing.
- Letting contract polish outrun actual workflow behavior.

### Guardrails

- No dedicated web client work.
- Keep renderer logic separate from engine decisions.
- Favor a small, stable contract over broad UI ambition.

## Handoff Requirements

- CLI rendering fallback must remain preserved for all A2UI changes.
- Action handling must remain typed, allowlisted, and engine-authoritative.
- Required gate results must be reported before integration.

## Notes

- This lane is intentionally narrow and does not change routing or provider configuration.
- The required Milestone 3 roadmap task and Capability 4 vision mapping are explicit above so the handoff can be audited without inference.
