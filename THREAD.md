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
- Shared-file approval note: the `src/qual/cli.py` edit is intentional, limited to exposing the live argparse command-token lookup surface for catalog validation, and is submitted in this handoff for explicit integrator approval before merge.
- Integrator-locked files touched: `src/qual/cli.py` only; this file is part of the actual branch-tip merge target and is called out for explicit review/approval.
- Post-`f8d860e` target delta: `THREAD.md`, `THREAD_PACKET.md`, `src/qual/cli.py`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`.
- Implementation/test traceability: `c0b5392d4`, `8b56b5a13`, `c2ff1842f`, and `9d0c82ccdfa74d8daf33d98ce410fd599bf45609` are recent post-`f8d860e` non-metadata commits in the branch-tip review target; `9d0c82ccdfa74d8daf33d98ce410fd599bf45609` changed `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py` as well as handoff metadata.
- Previous metadata-only traceability: `c65bfe07cc2b48aa35b3552774da12178d0e51bc4` changed `THREAD.md` and `THREAD_PACKET.md` only.
- Reviewed-tip metadata-only traceability: `e233e4733c186a4843c4c1b4cd90a20c860f7118` changed `THREAD.md` and `THREAD_PACKET.md` only.
- Fixer prompts satisfied: `20260429T152044Z`, `20260429T152842Z`, `20260429T154016Z`, `20260429T154607Z`, `20260429T155155Z`, `20260429T155636Z`, `20260429T160222Z`, `20260429T161403Z`, `20260429T161853Z`, `20260429T162401Z`, `20260429T162824Z`, `20260429T163215Z`, `20260429T163501Z`, `20260429T164041Z`, `20260429T164708Z`, `20260429T164803Z`; canonical packet details live in `THREAD_PACKET.md`.
