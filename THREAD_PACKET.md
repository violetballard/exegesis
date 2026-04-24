# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: narrow command-contract hardening in `src/qual/commands/catalog.py`, plus focused regression coverage in `tests/unit/test_commands_catalog.py`.
- Canonical demo-path step advanced: `preview and apply or reject a patch`
- Concrete canonical mapping: this slice makes `preview and apply or reject a patch` more reliable by forcing the parser-backed patch-review CLI entrypoints to stay aligned with the canonical catalog, so review commands fail fast on parser/catalog drift instead of silently accepting a mutated CLI surface.
- Scope clarification: this is CLI compatibility hardening for the existing patch-review step while Textual remains disabled. It does not add new commands, new engine behavior, persistence work, or new workflow reachability.
- Roadmap tie-in: this is Milestone 3 real-workflow-loop hardening at the CLI patch-review step.
- High-risk framing note: this remains a high-risk handoff because it hardens a public command contract and uses the explicitly approved shared regression path `tests/unit/test_commands_catalog.py`.
- Review basis note: implementation approval is pinned to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md` and `handoff_packets/feat-commands.md` are metadata-only refreshes.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the existing Milestone 3 CLI compatibility surface deterministic at the patch-review step by locking the parser-backed review command surface to the canonical catalog without adding new commands or new engine behavior.
- Risk reason: this touches a public command contract in `src/qual/commands/catalog.py` and the explicitly approved shared regression path `tests/unit/test_commands_catalog.py`, so parser drift at canonical patch-review entrypoints would directly weaken the active Milestone 3 CLI compatibility surface.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Harden `command_cli_contract()` so the full grouped parser-surface projection is validated against the canonical catalog instead of trusting derived canonical-name order alone.
2. Add regression coverage proving live parser/catalog drift raises a hard failure, including alias-level drift that preserves canonical command names and direct mutation of the live parser entrypoint constant.
3. Re-run the required gates and record the results for the narrowed patch-review CLI compatibility slice.

### Early Review Triggers

- Before first edit to any shared or integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing or config behavior.

### Stop Triggers

- Unresolved test, lint, or typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (Short Updates)

- Plan complete: scope stayed pinned to the reviewed implementation slice in `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- First green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed for this handoff slice.
- Before risky/shared file edit: the only shared path in scope was the approved regression file `tests/unit/test_commands_catalog.py`.
- Ready for handoff: this packet explicitly names `preview and apply or reject a patch` as the protected canonical step and keeps the claim narrowed to CLI compatibility hardening for that existing MVP loop step.

## Commands Run and Outcomes

- `make scope-check`: `PASSED`
- `./quality-format.sh --check`: `PASSED`
- `./quality-lint.sh`: `PASSED`
- `./quality-test.sh`: `PASSED`
- `./typecheck-test.sh`: `PASSED`
- `make ci`: `PASSED`

## Roadmap and Vision Mapping

- `ROADMAP.md` Milestone 3 `Real workflow loop`: this slice keeps the patch-review entry surface deterministic for the CLI-first MVP loop while the package/layout migration lands.
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract`: the active CLI surface now rejects parser/catalog drift before it can silently change the deterministic engine-facing contract.
