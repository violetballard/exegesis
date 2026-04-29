# Migrate `qual` Infra from Codex to OpenCode + Claude Code

## Summary
We’ll do this in two stages: move the human/operator workflow to Claude Code first, then run a shadowed backend migration and cut the daemon over. The control plane stays Python, the packet/worktree model stays intact, and we replace only the agent runtime layer.

Target runtime split:
- online workers: Claude Code sidecar
- offline workers: OpenCode server backed by LM Studio
- standard local model: `qwen3.6-35b-a3b`
- heavy local model: `qwen3.5-122b-a10b`
- standard cloud model family: Claude Sonnet 4
- heavy cloud model family: Claude Opus 4

Important default we’re choosing:
- keep `.codex/` state directories and `codex/<lane>` branch names through the migration
- remove Codex/OpenAI from the daemon runtime path first
- do any namespace cleanup later as a separate, lower-risk pass

## Key Changes
### 1. Move operator workflow to Claude Code first
- Add project-local Claude Code commands in `.claude/commands/` for the existing operator actions:
  - `daemon-status`
  - `daemon-start`
  - `daemon-stop`
  - `pipeline-tick`
  - `planner-run`
  - `router-run`
  - `milestone-report`
- Keep the current Python and shell scripts as the single source of truth; the Claude commands should wrap them, not reimplement them.
- Add a project `CLAUDE.md` that points Claude Code at the existing repo workflow, while keeping `AGENTS.md` as the authoritative shared instruction file.
- Do not duplicate `.agents/skills` for OpenCode at first: OpenCode already discovers `.agents/skills/*/SKILL.md`, so those stay where they are.
- Add `.opencode/commands/` only for commands we explicitly want inside OpenCode; otherwise let OpenCode consume `AGENTS.md` and `.agents/skills` directly.

### 2. Introduce a vendor-neutral runtime layer under the daemon
Replace Codex-specific launch/client logic with a backend interface instead of editing packet logic, planner logic, or status logic directly.

New runtime interface:
- `AgentRuntime`
- `start_run(role, lane, prompt, workdir, profile) -> RunHandle`
- `resume_run(run_handle, prompt) -> RunHandle`
- `abort_run(run_handle) -> None`
- `probe(profile) -> ProbeResult`

New runtime data types:
- `RuntimeProfile`
  - `backend`: `claude_cli` | `opencode_server`
  - `provider`
  - `model`
  - `transport`
  - `args`
  - `env`
- `RunHandle`
  - `backend`
  - `run_id`
  - optional `session_id`
  - optional `pid`
  - `log_path`
  - `workdir`
- `ProbeResult`
  - `healthy`
  - `reason`
  - `latency_ms`

Implementation split:
- `ClaudeCodeRuntime`: used for cloud worker, reviewer, fixer, and integrator runs
- `OpenCodeRuntime`: used for local fallback and local heavy runs through `opencode serve`

### 3. Replace Codex-specific execution paths
Update the daemon/runtime code so all current Codex assumptions get routed through the new runtime layer.

Codex-specific surfaces to remove from the active daemon path:
- `codex_mcp_client.py`
- direct `codex exec` launches in router/feature launchers
- `CODEX_HOME`-specific local runtime assumptions
- status/process regexes that only recognize Codex processes

Concrete changes:
- `codex_packet_handoff/tools/router.py`: swap reviewer/fixer/integrator launch and resume calls to `AgentRuntime`
- `codex_packet_handoff/tools/launch_feature_lanes.py`: swap feature lane launch/resume to `AgentRuntime`
- `codex_packet_handoff/tools/daemon_monitor.py`, `codex_packet_handoff/tools/daemon_ctl.py`, `codex_packet_handoff/tools/local_exec_sweeper.py`: update process detection, stale-run cleanup, and status reporting for:
  - `claude -p` or equivalent Claude Code non-interactive runs
  - `opencode serve` and OpenCode-backed local runs
- `codex_packet_handoff/tools/setup.py` and router config generation: replace `codex_cmd` / `fallback_codex_cmd` style config with backend-neutral profiles

New profile defaults:
- cloud standard: Claude Sonnet 4 via `claude_cli`
- cloud heavy: Claude Opus 4 via `claude_cli`
- local standard: `qwen3.6-35b-a3b` via OpenCode + LM Studio
- local heavy: `qwen3.5-122b-a10b` via OpenCode + LM Studio

### 4. Use OpenCode server for local/offline runs
Use OpenCode’s HTTP server as the local programmatic backend instead of shelling its TUI/CLI directly.

Design choice:
- run `opencode serve` as a daemon-managed local service
- use its session/message APIs for local worker execution
- keep CLI fallback as break-glass only, not the primary automation path

Config shape:
- project config in `.opencode/opencode.json`
- provider config for LM Studio there
- model mapping there for the two Qwen local profiles
- permission policy there for the local agent runtime

Local assumptions we’re locking:
- LM Studio remains the local provider
- exact model IDs should be resolved against OpenCode’s LM Studio provider listing during implementation
- if LM Studio exposes slightly different model strings, we map to them once in config and keep the logical profile names stable

### 5. Use Claude Code as the online worker sidecar
Design the cloud path around Claude Code, since we want to move away from OpenAI and prefer Claude for online workers.

Decision:
- daemon launches Claude Code for online worker roles through a dedicated sidecar runtime
- the control plane stores backend-neutral run metadata, not Codex thread IDs
- if Claude Code exposes resumable session IDs cleanly, record them
- if not, the daemon still works in stateless run mode using packet + worktree state as the source of truth

Important default:
- correctness must not depend on a vendor-specific persistent thread/session ID
- status should report `run_id` first, backend-native `session_id` second if available

Auth/default behavior:
- primary implementation target: use the local Claude Code installation and its authenticated environment
- fallback path: if non-interactive automation cannot reliably use subscription auth, keep the same `ClaudeCodeRuntime` interface and back it with Anthropic API credentials without changing daemon architecture

### 6. Preserve pipeline semantics during migration
Do not redesign the packet workflow while migrating runtimes.

Keep unchanged in the first migration:
- `.codex/packets/lanes/*`
- planner packet emission
- lane worktree management
- branch-per-lane workflow
- queue truth / status script semantics
- `runtime_mode` cloud/local switching behavior

What changes:
- the executor behind each lane role
- config/profile schema
- status presentation of “thread/session” fields
- operator frontend commands

### 7. Shadow mode, then cutover
The migration phases should be:

1. Claude Code operator commands
- land `.claude/commands/` and `CLAUDE.md`
- prove status/start/stop/tick/report workflows without changing daemon runtime

2. Runtime abstraction
- add `AgentRuntime` and wire both Codex and new backends behind it
- no behavioral change yet

3. OpenCode local backend
- switch local fallback and local heavy profiles to OpenCode + LM Studio in shadow mode
- keep cloud on Codex temporarily while validating local parity

4. Claude Code cloud sidecar
- switch cloud worker profiles in shadow mode
- compare queue movement, logs, and handoff quality against current daemon behavior

5. Full cutover
- remove Codex from active router/setup/runtime paths
- keep compatibility shims only where needed for older state files

6. Cleanup pass
- remove dead Codex-only modules and config keys
- decide later whether `.codex/` and `codex/` names should be renamed

## Test Plan
- Operator parity:
  - Claude Code commands produce the same outputs as current status/start/stop/tick/report scripts
  - OpenCode can discover current `AGENTS.md` and `.agents/skills`
- Runtime parity:
  - feature lane launch works on OpenCode local standard model
  - feature lane launch works on OpenCode local heavy model
  - cloud reviewer/fixer/integrator runs work through Claude Code sidecar
  - `cloud_primary` and `local_fallback` switching still behaves correctly
- State and monitoring:
  - `status.py` queue truth remains unchanged
  - `daemon_monitor.py` correctly identifies Claude/OpenCode processes
  - orphan sweeper kills stale OpenCode/Claude worker runs without killing active ones
- Failure handling:
  - if OpenCode local server is down, daemon reports explicit local backend failure
  - if Claude Code sidecar auth is unavailable, daemon reports explicit cloud backend failure and only then falls back according to runtime policy
  - no fallback path silently reintroduces Codex/OpenAI
- Acceptance criteria:
  - normal daemon operation requires neither `codex exec` nor `codex mcp-server`
  - online workers run as Claude
  - offline workers run through OpenCode + LM Studio
  - operator maintenance can be done from Claude Code without losing current status visibility

## Assumptions
- We are intentionally keeping the Python daemon/coordinator and packet model; this is a backend-runtime migration, not a workflow redesign.
- We are intentionally not renaming `.codex/` or `codex/<lane>` during the first migration because that would add unnecessary breakage while we are still validating parity.
- OpenCode is assumed to stay on the current LM Studio backend for local models.
- We are designing around Claude Code for online work, but if subscription-backed non-interactive automation is not reliable enough, we keep the same cloud runtime interface and swap only its auth/provider layer.
- Sonnet 4 is the default standard online worker; Opus 4 is reserved for heavier work such as integrator-class or explicitly heavy profiles.
