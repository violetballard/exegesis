## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Keep materialized A2UI fallback actions deterministic in `src/qual/ui/a2ui.py`, with matching assertions in `tests/unit/test_a2ui_contract.py`.
- Scope completed: Resubmitted the review candidate as the narrow A2UI runtime slice plus packet metadata, with no Textual, engine, daemon/router tooling, ROADMAP/docs, quality-script, or unrelated-test changes in the branch-tip packet. The A2UI runtime slice now carries its action/card contract locally instead of importing off-scope shared contract modules.
- Canonical demo-path step advanced: deterministic A2UI actions make the "produce a plan or revision" and "preview and apply or reject a patch" CLI fallback path more reliable.
- Task summary:
  1. Restored `src/qual/ui/a2ui.py` as a self-contained A2UI runtime contract so the clean candidate does not depend on off-scope `exegesis_shared.contracts` files.
  2. Confirmed `tests/unit/test_a2ui_contract.py` asserts canonical materialized-action ordering instead of relying on input order.
  3. Cleaned the review candidate back to the narrow A2UI runtime slice plus packet metadata.
  4. Rewrote this handoff packet to match the actual review candidate and explicitly name the canonical demo-path step advanced.
- Changed-files list:
  - `src/qual/ui/a2ui.py`
  - `THREAD_PACKET.md`
  - `.codex/kickoff_packets/feat-a2ui-contract.md`
  - `.codex/packet_planner/state.json`
- Commands run with results:
  - `make scope-check` -> passed for branch `codex/feat-a2ui-contract`
  - `python -m unittest tests.unit.test_a2ui_contract tests.unit.test_terminal_chat_routing` -> passed, 16 tests
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed, 123 tests
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- Risks/blockers:
  - No known source blockers. The reviewed runtime behavior is constrained to deterministic A2UI action ordering and its contract assertion.
  - `.codex/kickoff_packets/feat-a2ui-contract.md` and `.codex/packet_planner/state.json` are packet metadata only; no Textual, engine, daemon/router tooling, ROADMAP/docs, quality-script, or unrelated-test source changes are part of this candidate.
- Roadmap/vision mapping:
  - Roadmap item(s) affected: Milestone 3 engine loop support through a stable CLI fallback contract.
  - Vision capability affected: Capabilities 3-4: plan/revise and patch review flows remain inspectable through deterministic A2UI fallback actions.
  - Canonical demo-path step advanced: deterministic A2UI actions make the "produce a plan or revision" and "preview and apply or reject a patch" CLI fallback path more reliable.
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Proposed `README.md` patch text: None.
