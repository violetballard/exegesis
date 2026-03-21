# Lane Kickoff: feat-a2ui-contract

- Branch: `codex/feat-a2ui-contract`
- Lane/owned paths: `src/qual/ui/a2ui.py`, `tests/unit/test_a2ui_contract.py`
- Scope goal: Record the review-packet alignment for `feat-a2ui-contract` so the lane handoff is auditable and accurately describes fallback action availability in terminal rendering from `src/qual/ui/a2ui.py` and the matching contract assertions in `tests/unit/test_a2ui_contract.py`.

### Priority outcomes
1. Keep the reviewed file list limited to `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`.
2. Keep the scope statement aligned with the fallback action-availability rendering change.
3. Keep the packet language separated from unsupported schema-manifest, fallback-preview, and action-filtering claims.

### Guardrails
- No unsupported schema-manifest or fallback-preview claims in this kickoff packet.
- Keep the file list auditable against the actual commit diff.
- Favor a small, stable two-file handoff over feature-description drift.
