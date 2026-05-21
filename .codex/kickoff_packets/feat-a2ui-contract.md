# Lane Kickoff: feat-a2ui-contract

- Branch: `codex/feat-a2ui-contract`
- Lane/owned paths: `shared/src/exegesis_shared/contracts/**`, `shared/src/exegesis_shared/models/**`, `shared/src/exegesis_shared/types/**`, `src/qual/ui/a2ui.py`, `src/qual/ui/test_a2ui_fallback_safety.py`, `tests/unit/test_a2ui_contract.py`, `tests/unit/test_a2ui*.py`
- Scope goal: Stabilize shared A2UI card/action/selection contracts needed by the engine-first MVP while keeping rendering and UI ambition out of shared code.

### Priority outcomes
1. Keep A2UI contracts typed, policy-aware, and engine-authoritative.
2. Support patch review, retrieval, basket, and context cards needed by the canonical demo path.
3. Preserve CLI fallback behavior without turning shared contracts into UI rendering code.

### Definition of done
- Shared A2UI contracts validate payloads and capabilities.
- Patch review actions resolve through typed, policy-gated engine actions.
- Unknown or unsupported cards degrade safely.
- CLI fallback surfaces can preview and apply/reject patch proposals through stable contracts.

### Milestone 3 closure focus
- Canonical demo-path step advanced:
  - preview and apply or reject a patch through shared card/action contracts
  - keep the future Textual client unblocked by engine contract gaps
- Prefer hardening the current patch/retrieval/basket contract path over expanding UI ambition.

### Do not spend time on
- Textual implementation work.
- Generated UI promotion systems.
- Native/workstation A2UI futures.
- Visual polish.

### Guardrails
- Shared package must stay UI-agnostic.
- `src/qual/ui/a2ui.py` remains a compatibility shim.
- Do not edit control-plane metadata, packet files, or ownership policy.
