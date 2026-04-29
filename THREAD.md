# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review target: current branch tip `codex/feat-commands`.
- Review basis: full branch-tip diff from merge base `06cdebc2d5d53533b73f264a4bbf5a4b4daacb27..HEAD`.
- Files in target: `THREAD.md`, `THREAD_PACKET.md`, `scripts/scope-check.sh`, `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`, `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`.
- Parser-surface fix: `command_cli_contract()` validates against the actual argparse subparser choices exposed by `src/qual/cli.py`, with focused tests for parser command-token rename, parser alias-token rename, parser-only token addition, and parser-only token removal.
- Demo-path mapping: task-by-task details in `THREAD_PACKET.md` identify the canonical command surfaces for `open project/document`, `retrieve relevant material`, `gather context into basket`, `plan/revise`, `apply/reject patch`, `persist state`, and `continue working`.
- Canonical demo-path impact: deterministic CLI contract validation makes the CLI fallback a reliable way to drive the engine-first MVP loop; live CLI command parsing and catalog metadata can no longer silently drift, so the retrieval command surface is discoverable and parseable from the same contract.
- Lane-owned files: `src/qual/commands/**`.
- Approved shared-test exception: `tests/unit/test_commands_catalog.py`.
- Shared-by-approval files: `src/qual/cli.py`.
- Integrator-locked files touched: `src/qual/cli.py` only; this file is part of the actual branch-tip merge target and needs explicit review/approval.
- Implementation/test traceability: `9d0c82ccdfa74d8daf33d98ce410fd599bf45609` changed `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py` as well as handoff metadata; it is not a metadata-only commit.
- Latest metadata-only traceability: `1269da599851c60b7428109f5ac2adf13dee430b` changed `THREAD.md` and `THREAD_PACKET.md` only.
- Fixer prompts satisfied: `20260429T152044Z`, `20260429T152842Z`, `20260429T154016Z`, `20260429T154607Z`, `20260429T155155Z`, `20260429T155636Z`, `20260429T160222Z`, `20260429T161403Z`, `20260429T161853Z`, `20260429T162401Z`, `20260429T162824Z`, `20260429T163215Z`; canonical packet details live in `THREAD_PACKET.md`.
