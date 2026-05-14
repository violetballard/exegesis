# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Merge candidate: branch tip after the latest fixer commit.
- Corrected review surface: `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/catalog.py`, and the approved shared test file `tests/unit/test_commands_catalog.py`.
- Exact canonical demo-path step advanced: `retrieve relevant material and gather context into the basket`.
- Command-catalog mapping: this slice keeps the active operator command surface deterministic for the engine-first MVP loop while Textual remains disabled, specifically strengthening the retrieval/context step by preventing silent drift between `command_names()` and the approved parser entrypoint order.
