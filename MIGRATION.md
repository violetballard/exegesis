# Migrate `qual` Infra Toward OpenCode + Claude Workers

## Summary
We are no longer treating this as a full replacement of the operator/control-plane chat. The durable control plane remains this Codex-backed monitoring and infra thread for now, because it carries the long-running project context and works well as the human operations seat. The daemon stays Python, the packet/worktree model stays intact, and runtime migration happens behind the worker execution layer.

Current state already completed:
- local/offline worker backend has moved to OpenCode + LM Studio
- current local model: `qwen3.6-27b`
- local Qwen/OpenCode workers are the baseline worker pool
- hybrid scheduling is active: local workers keep moving while cloud adds capacity when available

Future target:
- keep Codex for control-plane monitoring and infra work while it remains useful and paid/available
- replace OpenAI cloud worker dependency over time with Claude-family cloud workers
- keep OpenCode + Qwen local as the always-on fallback/baseline
- keep `.codex/` state directories and `codex/<lane>` branch names through the migration
- defer namespace cleanup until after the runtime transition is boring and stable

## Target Runtime Split
- control-plane/operator chat: keep Codex for monitoring, daemon work, commits, and long-context project continuity
- local workers: OpenCode + LM Studio using `qwen3.6-27b`
- cloud integrator: Claude Opus 4.7, high effort by default
- cloud reviewer: Claude Sonnet 4.6, high effort by default, with Opus escalation for high-risk/shared/core reviews
- cloud fixer: Claude Sonnet 4.6, medium effort by default, with Opus escalation after repeated failure
- cloud feature worker: Claude Sonnet 4.6, medium effort by default
- cloud light/triage worker: Claude Haiku 4.5, low or medium effort
- manual deep architecture/spec work: Claude Opus 4.7, high/xhigh effort, with max effort only for one-off manual escalations

## Design Principles
- This is a backend-runtime migration, not a workflow redesign.
- Local workers are baseline capacity, not merely emergency fallback.
- Cloud workers are additive capacity and should be spent where they improve quality most.
- Quota failure should disable only the cloud pool; local workers should continue.
- No active local job should be killed or migrated just because cloud quota returns.
- Correctness must not depend on vendor-native persistent thread IDs.
- The packet/worktree filesystem remains the source of truth.
- We do not need to replace this Codex chat with Claude Code as part of the migration.

## Key Changes
### 1. Preserve the Current Operator Workflow
Do not make Claude Code the required operator frontend.

Keep unchanged:
- this Codex-backed control-plane chat for status, daemon repair, commits, and monitoring
- existing `.agents/skills/*/SKILL.md`
- existing Python and shell scripts as the operational source of truth
- `AGENTS.md` as the authoritative shared instruction file

Optional later additions:
- add `CLAUDE.md` only if it helps Claude Code workers understand the repo
- add `.claude/commands/` only as convenience wrappers, not as the primary control plane
- add `.opencode/commands/` only for commands we explicitly want inside OpenCode

Non-goal:
- do not spend migration work replacing this long-running Codex monitor chat with Claude Code

### 2. Introduce or Continue Hardening a Vendor-Neutral Runtime Layer
Replace direct provider assumptions with backend-neutral worker profiles wherever practical.

Runtime interface shape:
- `AgentRuntime`
- `start_run(role, lane, prompt, workdir, profile) -> RunHandle`
- `resume_run(run_handle, prompt) -> RunHandle`
- `abort_run(run_handle) -> None`
- `probe(profile) -> ProbeResult`

Runtime profile fields:
- `backend`: `codex_cli` | `claude_cli` | `anthropic_api` | `opencode_cli` | `opencode_server`
- `provider`
- `model`
- `effort`
- `transport`
- `args`
- `env`
- `context_window`

Run metadata fields:
- `backend`
- `run_id`
- optional `session_id`
- optional `pid`
- `log_path`
- `workdir`
- `provider_used`
- `model_used`
- `effort_used`

Implementation split:
- `OpenCodeRuntime`: used for local Qwen worker runs
- `ClaudeRuntime`: used for future cloud worker, reviewer, fixer, and integrator runs
- `CodexRuntime`: kept for current control-plane/cloud compatibility until Claude cloud cutover is proven

### 3. Keep OpenCode as the Local/Offline Backend
This part is already effectively complete for the daemon’s local pool.

Current local defaults:
- backend: OpenCode
- provider: LM Studio
- model: `qwen3.6-27b`
- local total cap: `4`
- local jobs continue even when cloud quota is exhausted

Implementation notes:
- keep logical profile names stable even if LM Studio/OpenCode expose model strings slightly differently
- keep process detection and orphan sweeping aware of `opencode run`
- consider `opencode serve` later if it gives better process/session control, but do not block on it while `opencode run` is working

### 4. Add Claude as a Tiered Cloud Worker Pool
Design Claude as a cloud worker pool, not as a replacement for local execution or this operator chat.

Recommended cloud role mapping:
- `cloud_integrator`: Claude Opus 4.7, high effort
- `cloud_reviewer`: Claude Sonnet 4.6, high effort
- `cloud_reviewer_high_risk`: Claude Opus 4.7, high effort
- `cloud_fixer`: Claude Sonnet 4.6, medium effort
- `cloud_fixer_escalated`: Claude Opus 4.7, high effort
- `cloud_feature`: Claude Sonnet 4.6, medium effort
- `cloud_light_feature`: Claude Haiku 4.5, medium effort
- `cloud_triage`: Claude Haiku 4.5, low effort
- `manual_architecture`: Claude Opus 4.7, high/xhigh effort

Cost/performance policy:
- Haiku is for cheap triage, packet cleanup, status summaries, simple classification, and low-risk formatting work.
- Sonnet is the default serious worker: feature work, ordinary fixers, and most reviews.
- Opus is the closer: integrator, high-risk review, stuck fixers, provider/routing/core changes, and deep architecture/spec reconciliation.
- Max effort is manual-only, not daemon-default.

### 5. Preserve Hybrid Scheduling
The hybrid pool is the correct target shape.

Default scheduling policy:
1. Poll and reconcile active jobs.
2. Run integrator work first.
3. Run reviewer work next.
4. Run fixer work next.
5. Refill feature lanes last.

Provider preference:
- Integrator: cloud first when available, otherwise local.
- Reviewer: cloud first when available, otherwise local.
- Fixer: local first, cloud only if local is full or if escalation is warranted.
- Feature workers: local baseline, cloud spillover when cloud has spare capacity.

Capacity defaults:
- local total cap: `4`
- cloud total cap: `4`
- cloud roles compete under precedence rather than each having unlimited independent caps
- cloud quota failures disable only cloud scheduling
- cloud quota recovery applies only to new work

### 6. Replace Codex-Specific Cloud Execution Paths Gradually
Do not rip out Codex cloud worker support until Claude cloud workers have proven parity.

Codex-specific surfaces to migrate behind the runtime layer:
- direct `codex exec` launches in router/feature launchers
- `CODEX_HOME`-specific worker assumptions
- status/process regexes that only recognize Codex processes
- config keys that assume every worker profile is `codex_cmd` + `model_args`

Concrete files likely involved:
- `packet_garden/tools/router.py`
- `packet_garden/tools/launch_feature_lanes.py`
- `packet_garden/tools/agents_coordinator.py`
- `packet_garden/tools/daemon_monitor.py`
- `packet_garden/tools/daemon_ctl.py`
- `packet_garden/tools/local_exec_sweeper.py`
- `packet_garden/tools/setup.py`
- `.codex/packet_router/config.json`
- `.codex/packet_router/example.json`

### 7. Claude Cloud Auth Strategy
Primary target:
- use Claude Code or Claude CLI if non-interactive automation is stable and can use the user’s authenticated environment

Fallback target:
- keep the same `ClaudeRuntime` interface and back it with Anthropic API credentials if subscription-backed non-interactive automation is not reliable enough

Required behavior:
- status must show provider/model/effort used per run
- cloud auth failure must be explicit
- cloud auth failure must not stop local OpenCode/Qwen workers
- no fallback path should silently reintroduce OpenAI cloud workers once Claude cutover is complete

### 8. Migration Phases
Current completed phase:
1. OpenCode local backend
- local fallback and local heavy worker pool use OpenCode + LM Studio
- current model is `qwen3.6-27b`
- hybrid mode keeps local pool active while cloud is available or exhausted

Next phases:
2. Runtime profile cleanup
- normalize provider/model/effort/context metadata across Codex, Claude, and OpenCode profiles
- keep current behavior while making provider switching less special-case heavy

3. Claude cloud shadow path
- add Claude cloud profiles without disabling current Codex cloud profiles
- prove reviewer/fixer/integrator runs on Claude against real packets
- compare queue movement, logs, cost, and handoff quality

4. Claude cloud cutover
- route cloud reviewer/integrator/fixer/feature roles to Claude according to the tiering policy
- keep local OpenCode/Qwen pool unchanged
- keep this Codex chat as the operator control plane unless we explicitly decide otherwise later

5. Cleanup pass
- remove dead Codex-only worker modules and config keys after Claude cloud is stable
- keep `.codex/` and `codex/<lane>` names until renaming is a separate low-risk project

## Test Plan
- Runtime metadata:
  - status output shows backend, provider, model, effort, context window, and pid/session id where available
  - historical Codex, current OpenCode, and future Claude jobs can all be represented in one status view
- Local OpenCode:
  - feature lane launch works on `qwen3.6-27b`
  - local workers continue when cloud quota/auth fails
  - orphan sweeper kills stale OpenCode runs without killing active ones
- Claude cloud:
  - cloud reviewer works through Claude profile
  - cloud fixer works through Claude profile
  - cloud integrator works through Claude profile
  - high-risk review can escalate from Sonnet to Opus
  - Haiku low/medium can complete cheap triage/status/packet work without burning Sonnet/Opus budget
- Hybrid scheduling:
  - integrator gets precedence over reviewer, fixer, and feature work
  - reviewer gets precedence over fixer and feature work
  - local feature refill does not starve cloud reviewer/integrator work
  - no duplicate local/cloud job launches for the same lane/packet
- Failure handling:
  - Claude auth failure disables only Claude cloud scheduling
  - cloud quota failure disables only cloud scheduling
  - local OpenCode/Qwen work continues
  - status clearly distinguishes local capacity, cloud capacity, and cloud quota/auth state
- Acceptance criteria:
  - offline workers run through OpenCode + LM Studio
  - online workers can run as Claude by role tier
  - this Codex chat remains usable as the control-plane monitor
  - daemon operation does not require replacing the operator workflow with Claude Code

## Assumptions
- We are intentionally keeping the Python daemon/coordinator and packet model.
- We are intentionally keeping `.codex/` and `codex/<lane>` names during the runtime transition.
- OpenCode remains on LM Studio for local workers.
- `qwen3.6-27b` remains the local default unless memory/performance testing says otherwise.
- Claude model names and effort labels may need exact provider-string updates at implementation time.
- Claude Code/CLI subscription automation may not be reliable enough; Anthropic API can back the same runtime interface if needed.
- Codex remains acceptable for this control-plane chat and monitoring role even while we reduce OpenAI dependency in daemon worker execution.
