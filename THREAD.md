# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: current branch tip `codex/feat-commands`.
- Review basis: full branch-tip diff from merge base `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27..HEAD`.
- Files in target: `THREAD.md`, `THREAD_PACKET.md`, `scripts/scope-check.sh`, `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`, `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`.
- Parser-surface fix: `command_cli_contract()` validates against the actual argparse subparser choices from `src/qual/cli.py`, with focused tests for parser token rename, parser-only token addition, and parser-only token removal.
- Demo-path mapping: task-by-task details in `THREAD_PACKET.md` identify the AGENTS canonical command surfaces for `open project/document`, `retrieve relevant material`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `persist session state`.
- Canonical demo-path impact: deterministic CLI contract validation makes the CLI fallback a reliable way to drive the engine-first MVP loop; live CLI command parsing and catalog metadata can no longer silently drift, so the retrieval command surface is discoverable and parseable from the same contract.
- Lane-owned files: `src/qual/commands/**`.
- Shared-by-approval files: `tests/unit/test_commands_catalog.py`; `src/qual/cli.py`.
- Integrator-locked files touched: `src/qual/cli.py` only.
- Latest fixer traceability: `c2ff1842f5b1cd4c667814689fee116ef36d8cec` changed `THREAD.md`, `THREAD_PACKET.md`, and `tests/unit/test_commands_catalog.py`; it is not a metadata-only commit.
- Fixer prompts satisfied: `20260429T152044Z`, `20260429T152842Z`, `20260429T154016Z`, `20260429T154607Z`, `20260429T155155Z`, `20260429T155636Z`, `20260429T160222Z`, `20260429T161403Z`, `20260429T161853Z`; canonical packet details live in `THREAD_PACKET.md`.
