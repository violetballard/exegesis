# Project Profiles Spec: Confidential vs Standard + Online Overrides (UX + PolicyGate + Audit)

## Goal

- Support two profile modes:
  - `confidential` (local only, default, encrypted, offline-first, blocks external providers)
  - `standard` (online-capable profile)
- Online providers are enabled only through explicit overrides (`online_overrides.enabled=true`).
- Make online enablement deliberate (not hard, not easy).
- Enforce rules in engine `PolicyGate`, not UI-only checks.

## Non-Goals

- Collaboration features.
- Telemetry-based enforcement.
- Background network activity in `confidential` mode.

## A) Data Model

1. `ProjectProfile`
- `profile_mode: "confidential" | "standard"`
- `irb_sensitive: bool`
  - if `true`, `profile_mode` MUST be `confidential`
- `cloud_send_policy: "context_sets_only" | "allow_full_doc"`
  - valid only when `profile_mode == "standard"`
  - default `context_sets_only`
- `online_overrides_enabled: bool` (default false)
- `online_enabled_at: timestamp?`
- `online_enabled_scope: "project" | "global"`

2. `ProviderConfig`
- `providers` map
- `roles` map (`role -> {provider, model}`)

3. `RunContext`
- `run_id`
- `project_id`
- `role`
- `attached_context_set_ids`
- `attached_excerpt_ids?`
- `active_section_id?`
- `cloud_full_doc_ok` (default `false`)
- `requested_provider_id` (resolved after routing/overrides)

## B) UI State Machine (Studio)

Project creation:
1. create project (name + location)
2. sensitive/IRB checkbox
  - if checked: force `confidential`, disable `online`
3. choose mode
  - `confidential` default
  - `standard` disabled when IRB-sensitive
4. if `standard` and user enables online overrides:
  - choose `cloud_send_policy` (default `context_sets_only`)
  - require acknowledgement checkbox
  - provider setup page (secure key storage)
5. create project

Project settings:
- enable online providers flow (when `irb_sensitive=false`) with friction:
  - explanation
  - acknowledgement
  - policy selection
  - confirm action/token
- disable online providers should be easy and reset project online overrides

Mode banner:
- `Confidential (Local Only)`
- `Standard Profile (Online Overrides Enabled)` + current `cloud_send_policy`

## C) PolicyGate Rules (engine authoritative)

Inputs:
- `project.profile_mode`
- `project.irb_sensitive`
- `project.cloud_send_policy`
- `project.online_overrides_enabled`
- provider allowlist config
- project-level mode overrides

1. Hard constraints:
- if `irb_sensitive == true`:
  - force `profile_mode=confidential`
  - reject standard/online override enable attempts with `IRB_SENSITIVE_PROJECT`

2. Provider allowlist:
- `confidential`:
  - allowed providers: confidential allowlist (default `local_openai`)
  - provider host must be localhost/127.0.0.1
  - non-allowed provider => block run + alert
- `standard`:
  - allowed providers: standard allowlist (default `local_openai`, `openai_cloud`, `anthropic`)
  - if non-local provider requested and `online_overrides_enabled != true`, block run + alert
  - non-allowed provider => block run + alert

3. Cloud content policy (for non-local providers in standard mode with online overrides enabled):
- `context_sets_only`:
  - allow prompt + explicitly attached context excerpts + minimal metadata
  - forbid full documents/corpus index/unattached excerpts
  - if no context set attached: allow with warning
- `allow_full_doc`:
  - requires per-run `cloud_full_doc_ok=true`
  - if missing: downgrade to `context_sets_only` + warning
  - if present: allow bounded broader context and log `cloud_full_doc_used`

4. Tool restrictions:
- `confidential`:
  - block tools with `network_required=true`
- `standard`:
  - tools may be allowed under normal confirmation/policy gates

## D) Engine API / Commands (minimum)

Project APIs:
- `project.create({name, path, irb_sensitive, profile_mode, cloud_send_policy, online_overrides_enabled})`
- `project.set_profile(project_id, profile_mode, cloud_send_policy?, online_overrides_enabled?, confirm_token?)`
  - `confirm_token` required for confidential -> standard with online overrides

Run API:
- `run.execute({project_id, role, prompt, attached_context_set_ids, cloud_full_doc_ok=false, ...})`

Routing metadata:
- return `provider_used`, `model_used` at run level for UI and audit

## E) Audit Events (encrypted, content-free)

Required events:
- `project_created(profile_mode, irb_sensitive)`
- `project_profile_change_requested(from,to)`
- `project_profile_changed(from,to,cloud_send_policy)`
- `online_mode_enabled(scope,cloud_send_policy)`
- `cloud_send_policy_changed(old,new)`
- `cloud_run_executed(provider_id,model_id,run_id)`
- `cloud_run_blocked(provider_id,reason)`
- `cloud_full_doc_used(run_id)`
- `network_tool_blocked(tool_id,reason)`

Never log:
- prompts/excerpts/document paths/content payloads

## F) Default Product Behaviors

- default `profile_mode=confidential`
- default `irb_sensitive=false`
- default `cloud_send_policy=context_sets_only`
- default `online_overrides_enabled=false`
- enabling online overrides requires friction; disabling is easy
- confidential/local-first minimum supported Studio memory remains 32GB
- online mode may run on lower-memory machines because local inference is not required

## G) Acceptance Criteria

1. New projects default to confidential and block online providers at engine level.
2. IRB-sensitive projects cannot enable standard-mode online overrides.
3. Standard-mode projects can route roles to OpenAI/Claude when online overrides are enabled.
4. Cloud sending defaults to `context_sets_only`; full-doc requires per-run flag + audit.
5. UI clearly indicates profile mode, override state, and provider used per run.
6. Engine blocks network-required tools in confidential mode.
7. Audit logs capture mode/provider decisions without content leakage.
