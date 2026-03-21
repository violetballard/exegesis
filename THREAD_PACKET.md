## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Harden A2UI fallback previews in `src/qual/ui/a2ui.py` by excluding source `CodeBlock` entries from the read-only fallback view, with matching assertions in `tests/unit/test_a2ui_contract.py`.
- Scope completed: Updated the fallback preview sanitization so unsupported-card read-only views keep safe primitive blocks and JSON previews while omitting source code blocks, with contract tests covering that behavior.
- Task summary:
  1. Changed the engine and unknown-card fallback paths in `src/qual/ui/a2ui.py` to call `_extract_safe_primitive_blocks(..., allow_code_block=False)` so read-only fallback previews do not surface source `CodeBlock` entries.
  2. Added contract coverage in `tests/unit/test_a2ui_contract.py` to assert the fallback preview still renders safe primitive blocks and the synthetic JSON preview while excluding source code blocks.
  3. Rewrote the handoff packet to match the actual diff and removed unrelated packet-maintenance, routing, and UI-shell references.
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
  - No known blockers. The change is constrained to fallback-preview sanitization and its contract assertions.
  - The only functional risk is accidental over-sanitization of fallback previews; the added test coverage guards against dropping safe primitive blocks.
- Roadmap/vision mapping:
  - Roadmap item(s) affected: Milestone 5: A2UI Presentation Layer - harden read-only fallback previews by filtering source `CodeBlock` entries from unsupported-card fallback views.
  - Vision capability affected: Capability 5: Agent-to-UI protocol (A2UI) - fallback previews now sanitize unsupported-card read-only views by omitting source code blocks while preserving safe primitive content and JSON previews.
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
