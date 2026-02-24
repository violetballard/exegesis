# Spec Update: Multi-Provider Support (OpenAI-Compatible + Anthropic) with Confidential Gating

## Goal

- Add Anthropic Claude support alongside OpenAI-compatible providers.
- Keep local-first defaults:
  - `confidential` profile allows only `local_openai` localhost endpoints.
- `standard` profile may use online providers only when `online_overrides.enabled=true`.
- Studio should make disabling confidential mode possible but frictionful; engine `PolicyGate` remains authoritative.

## A) Provider Abstraction (Engine)

Provider interface:
- `list_models() -> [model_id]`
- `chat(messages, *, model_id, tools?, tool_choice?, stream?, max_tokens?, temperature?, response_format?)`
- later: `embeddings(texts, model_id) -> vectors`
- optional: `vision_chat(messages_with_images, model_id, ...)`

Providers:
1. `OpenAICompatProvider`
- uses `base_url` + `api_key`
- supports `/v1/models` and `/v1/chat/completions` (embeddings later)
- probe for streaming and native tool calling
- if no native tools, use engine text-fallback protocol

2. `AnthropicProvider`
- uses `base_url` + `api_key`
- map OpenAI-style messages to Anthropic format
- map Anthropic tool-use blocks to internal tool-call schema
- enforce strict schema validation

## B) PolicyGate Rules (Engine)

Inputs:
- `profile.mode` (`confidential|standard`)
- provider allowlist config
- `online_overrides.enabled`, `online_overrides.scope`, `cloud_send_policy`

Rules:
1. If `profile.mode == confidential`:
- only providers in `allowed_providers.confidential` (default `[local_openai]`)
- require localhost provider endpoints
- disallowed provider => fail run with alert

2. If `profile.mode == standard`:
- providers allowed from `allowed_providers.standard`
- if provider is non-local and `online_overrides.enabled != true`, block run with guidance
- enforce `cloud_send_policy`:
  - `context_sets_only` default
  - `allow_full_doc` explicit only, never default, emits per-run warning/audit

3. Audit events:
- `online_mode_enabled(scope, cloud_send_policy)`
- `provider_used(provider_id, model_id, run_id)`
- `provider_blocked_by_policy(provider_id, reason)`

## C) Role Routing and Online Overrides

- role routing still declares provider + model
- `online_overrides.roles` may override provider/model by role
- overrides apply only when:
  - `profile.mode == standard`
  - `online_overrides.enabled == true`
  - scope merge rules are satisfied

## D) Tool Calling Normalization

- internal engine tool-call schema is canonical
- OpenAI-compatible native tool calls: validate payloads against schemas
- Anthropic tool-use blocks: map into canonical schema
- no native tools: engine text-fallback protocol (JSON-only, validate+retry)

## E) Studio UX Requirements

- Settings shows active profile mode: Confidential vs Standard.
- `Enable Online Providers...` flow requires:
  1. risk explanation
  2. acknowledgement checkbox
  3. scope selection (project default)
  4. `cloud_send_policy` selection (`context_sets_only` default)
  5. secure API key storage
  6. set `online_overrides.enabled=true`
- `Disable Online Providers` is easy and sets `online_overrides.enabled=false`
- profile may remain `standard`; with overrides disabled, runs stay local-only

## F) Engine CLI / Admin Console

- admin console can edit config YAML
- `exegesis doctor` should probe each configured provider and report:
  - reachability
  - streaming
  - tool-calling support
  - policy-blocked providers under current profile/overrides

## Acceptance Criteria

1. Confidential profile hard-blocks cloud providers.
2. Standard profile + `online_overrides.enabled=true` can route selected roles to Anthropic.
3. Non-local runs enforce `cloud_send_policy` (`context_sets_only` default).
4. Tool calls normalize and validate across providers.
5. Enabling online is frictionful; disabling is simple.
