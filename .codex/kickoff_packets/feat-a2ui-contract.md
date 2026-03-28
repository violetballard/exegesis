# Lane Kickoff: feat-a2ui-contract

- Branch: `codex/feat-a2ui-contract`
- Lane/owned paths: `src/qual/ui/a2ui.py`, `tests/unit/test_a2ui_contract.py`
- Scope goal: Version fallback card debug metadata in `src/qual/ui/a2ui.py` and keep the contract assertions aligned with the versioned fallback debug payload.
- Scope note: This is a narrow fallback-metadata and contract-coverage update. It does not expand into fallback manifest redesign or broader UI behavior changes.
- Roadmap item(s) affected: `ROADMAP.md` Milestone 5: A2UI Presentation Layer
- Vision capability affected: `PRODUCT_VISION.md` Capability 5: Agent-to-UI protocol (`A2UI`)

### Priority outcomes
1. Keep fallback debug metadata versioned in the A2UI source path.
2. Keep the reviewed file list limited to `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`.
3. Keep the packet language aligned with the versioned fallback debug payload and matching assertions.
4. Keep the handoff mapping explicit so reviewers can audit the roadmap and vision alignment without inference.

### Guardrails
- No unsupported source-code or test-code claims in this kickoff packet.
- Keep the file list auditable against the actual code diff.
- Favor a small, stable A2UI metadata-versioning change over broader fallback or canonicalization work.
