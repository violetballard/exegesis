# Lane Kickoff: feat-a2ui-contract

- Branch: `codex/feat-a2ui-contract`
- Lane/owned paths: `src/qual/ui/a2ui.py`, `tests/unit/test_a2ui_contract.py`
- Scope goal: Make terminal A2UI rendering show payloads for duplicate action labels and keep the contract assertions aligned with that exact output.
- Scope note: This is a narrow terminal-rendering and contract-coverage update. It does not expand into fallback manifest redesign or broader UI behavior changes.

### Priority outcomes
1. Keep duplicate action labels payload-aware in the terminal renderer.
2. Keep the reviewed file list limited to `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`.
3. Keep the packet language aligned with the actual rendered strings and matching assertions.

### Guardrails
- No unsupported source-code or test-code claims in this kickoff packet.
- Keep the file list auditable against the actual code diff.
- Favor a small, stable A2UI rendering change over broader fallback or canonicalization work.
