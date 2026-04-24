# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `2f6929c1185a3d77c984ce1de01d1fb445ebb84a`
- Packet refresh role: `reviewer-fix handoff refresh`
- Packet refresh basis: `regenerated against the live branch tip after reviewer traceability rejection on 2026-04-23`
- Packet refresh parent commit: `5301c0633dac89d072b80de8c603356e982f06ab`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the CLI-first MVP command surface deterministic across the demo loop by canonicalizing terminal-driven demo tokens and preserving the correct flow-step alignment for resolved argv.
- Risk reason: the reviewed branch tip includes additional command-surface behavior beyond the earlier packeted `command_cli_contract()` hardening and still carries one approved shared-test file outside lane-owned paths.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (Completed)

1. Regenerate the handoff packet against the actual implementation being proposed for merge at the live branch tip.
2. Rewrite the traceability note so it matches the post-packet command-surface commits instead of calling them metadata-only.
3. Add an explicit canonical demo-path step statement tied to the CLI-first MVP loop in roadmap language.
4. Re-run the required local gates for the current branch tip and record the outcomes.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Earlier packets incorrectly pinned review scope to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and described later refresh work as metadata-only.
- The actual branch tip proposed for merge is `2f6929c1185a3d77c984ce1de01d1fb445ebb84a`.
- The post-packet implementation commits now in scope are:
  - `6c8d54c79eb9c0da811069e97603664468067d22` `Harden demo terminal command canonicalization`
  - `2f6929c1185a3d77c984ce1de01d1fb445ebb84a` `Fix demo argv flow-step alignment`
- True reviewed implementation range represented by this packet: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..2f6929c1185a3d77c984ce1de01d1fb445ebb84a`
- This packet no longer claims any post-`f8d860e` implementation commit is metadata-only.
- Reviewed implementation files touched in the true branch delta:
  - `scripts/scope-check.sh`
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/canonical.py`
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- Handoff metadata files in the true branch delta:
  - `THREAD.md`
  - `THREAD_PACKET.md`
- Recomputed branch delta stats for the true reviewed basis:
  - `9` files changed
  - `+9745/-483` lines in `f8d860ed..2f6929c1`
- Budget note: this remains larger than an `AGENTS.md` high-risk `4`-task packet allows, so the packet is truthful about the size even though the branch is not a small-scope high-risk handoff.

## Scope Completed

- Hardened `command_cli_contract()` and related command-catalog validation so parser/catalog drift fails fast instead of silently changing the CLI surface.
- Added canonical demo-token handling for terminal operations so `terminal --operation-kind ... --message ...` routes deterministically to `apply-patch`, `reject-patch`, `persist`, and `export-handoff`.
- Fixed demo argv flow-step alignment so resolved argv keeps the correct canonical workflow token when shimmed terminal/demo routes are involved.
- Expanded regression coverage for command-catalog contract hardening and terminal-message canonicalization.
- Regenerated the handoff packet so the commit, scope, files, risk, and demo-path mapping all match the actual live branch tip.

## Canonical Demo-Path Mapping

- Canonical demo-path step advanced: `patch-review -> apply-patch/reject-patch -> persist -> export-handoff` in the current CLI-first MVP loop.
- Explicit roadmap-language statement: this handoff makes the canonical `preview and apply or reject a patch` step more real by keeping the terminal-driven CLI surface mapped to the same canonical tokens the roadmap MVP flow depends on before `persist` and `export-handoff`.
- Concrete operator impact: terminal orchestration and synthesis-request messages now canonicalize to stable demo tokens, so operators do not lose the parser-facing routes for `apply-patch`, `reject-patch`, `persist`, or `export-handoff` when message casing or phrasing varies.
- Flow-step integrity note: the `2f6929c1` alignment fix keeps resolved argv on the correct workflow token instead of falling back to a raw shim token, which is necessary for consistent downstream CLI behavior in the engine-first loop.
- Scope guard: this is command-surface hardening for the active CLI/operator path, not broader UI, Textual, or A2UI feature work.

## Approved Exception Note

- Approved shared-test exception: `tests/unit/test_commands_catalog.py`
- Approved by: the lane `reviewer` role, as recorded in archived approval packet `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/packets/lanes/feat-commands/archive/R__APPROVED__codex-feat-commands__96f57e262da909d58a61cbdf4aa162aac8f16196__20260424T005429Z.md`
- Approval source: archived reviewer approval packet `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/packets/lanes/feat-commands/archive/R__APPROVED__codex-feat-commands__96f57e262da909d58a61cbdf4aa162aac8f16196__20260424T005429Z.md`, plus canonical lane metadata `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/.codex/lane_meta/feat-commands.json`
- Approval scope note: this packet still includes that shared test file in the true reviewed basis and does not describe it as lane-owned.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Rebased the handoff description on the actual branch tip `2f6929c1` instead of the older narrowed packet basis.
2. Included the two post-packet command-surface commits `6c8d54c7` and `2f6929c1` in the reviewed scope and risk statement.
3. Added the explicit canonical demo-path statement tying this work to the CLI-first `preview and apply or reject a patch` loop step and its downstream `persist` / `export-handoff` transitions.
4. Re-ran the required local gates for the current branch tip and recorded the results below.

### Files Changed

- `THREAD.md`
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

### Commands Run and Outcomes

- `make scope-check`: `PASSED` (`[devex] scope-check: passed for branch 'codex/feat-commands'`)
- `./quality-format.sh --check`: `PASSED` (`[format] check passed`)
- `./quality-lint.sh`: `PASSED` (`[lint] passed`)
- `./quality-test.sh`: `PASSED` (`smoke passed`; `Ran 205 tests ... OK`)
- `./typecheck-test.sh`: `PASSED` (`[typecheck] compiling Python sources in src/`)
- `make ci`: `PASSED` (`[devex] CI entrypoint completed`)

### Risks / Blockers

- Risks:
  - the branch scope is broader than the earlier narrow `command_cli_contract()` handoff and now includes terminal canonicalization plus flow-step alignment behavior in `src/qual/commands/catalog.py`
  - the true reviewed basis still exceeds the normal high-risk packet size limits in `AGENTS.md`
- Blockers:
  - none for re-review packet generation; integration can decide whether to require a split based on the truthful scope above

## Required Handoff Fields

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 1 `Bootstrap Flow Stabilization`: `Command and diff-preview behavior hardening`
- `ROADMAP.md` Milestone 2 `Test Hardening`: `Add focused unit coverage for core behaviors` and `Keep command-level probes for integration confidence`
- `ROADMAP.md` MVP flow requirement: `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate`; this branch hardens the `patch` segment and the downstream `export` handoff transitions inside that exact loop

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: the CLI must remain a deterministic first-class operator surface while engine contracts harden
- `PRODUCT_VISION.md` capability 5 `Agent-to-UI protocol (A2UI)`: stable canonical command routing preserves the CLI fallback path that the same underlying artifacts depend on

### Routing / Provider Impact Note

- None. This branch does not touch provider routing or configuration behavior.

### Scope-Check / Ownership Note

- Shared/integrator-locked edits: `NO`
- Shared-by-approval implementation path included in the reviewed range: `tests/unit/test_commands_catalog.py`
- Lane-owned implementation path remains `src/qual/commands/**`
