from __future__ import annotations

import asyncio
import inspect
import json
import os
import re
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator, Protocol
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from exegesis_textual.actions.providers import (
    claude_tools_from_specs,
    google_tools_from_specs,
    mistral_tools_from_specs,
    openai_tools_from_specs,
    tool_call_request_from_claude,
    tool_call_request_from_google,
    tool_call_request_from_mistral,
    tool_call_request_from_openai,
)
from exegesis_textual.actions.registry import ProviderToolSpec, ToolCallRequest
from exegesis_textual.services.credentials import (
    CredentialStore,
    CredentialStoreError,
    KeyringCredentialStore,
    LOCAL_OPENAI_ACCOUNT,
    MISTRAL_ACCOUNT,
    PROVIDER_CREDENTIAL_ACCOUNTS,
)
from exegesis_textual.services.model_settings import (
    CLAUDE_PROVIDER,
    DEFAULT_LOCAL_OPENAI_API_KEY,
    DEFAULT_MISTRAL_MODEL,
    DEFAULT_CONTEXT_WINDOW_TOKENS,
    GOOGLE_PROVIDER,
    LOCAL_OPENAI_PROVIDER,
    MISTRAL_PROVIDER,
    OPENAI_PROVIDER,
    ModelSettings,
    MistralModelSettings,
    load_model_settings,
    model_supports_reasoning,
    normalize_local_openai_base_url,
    provider_label,
    save_model_settings,
)
from exegesis_textual.services.projects import is_local_developer_mode, is_release_mode
from exegesis_textual.services.prompt_integrity import PromptIntegrityError, load_verified_prompt

DEFAULT_SYSTEM_PROMPT_PATH = Path(__file__).with_name("prompts") / "writer_system_prompt.md"
DEFAULT_SYSTEM_PROMPT_MANIFEST_PATH = DEFAULT_SYSTEM_PROMPT_PATH.with_name("writer_system_prompt.manifest.json")
CLAUDE_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
GOOGLE_GENERATE_CONTENT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
PROVIDER_REQUEST_TIMEOUT_SECONDS = 180
PROVIDER_CONNECTION_TIMEOUT_SECONDS = 30
PROVIDER_TEST_MAX_TOKENS = 32
PROVIDER_REPLY_MAX_TOKENS = 4096
CLAUDE_API_VERSION = "2023-06-01"


@dataclass
class ChatMessage:
    role: str
    content: str
    streaming: bool = False
    provider_content: object | None = None

    def payload_content(self) -> object:
        return self.provider_content if self.provider_content is not None else self.content


@dataclass(frozen=True)
class ShellChatContext:
    project_name: str
    document_title: str
    document_type: str
    document_content: str
    confidentiality_mode: str
    basket_context: str
    selected_text: str = ""
    selection_start: int | None = None
    selection_end: int | None = None


@dataclass(frozen=True)
class ChatEvent:
    kind: str
    text: str = ""
    error: str = ""
    replay_content: object | None = None
    tool_call: ToolCallRequest | None = None


@dataclass(frozen=True)
class ConnectionTestResult:
    ok: bool
    message: str


@dataclass(frozen=True)
class _ParsedContent:
    text: str = ""
    reasoning: str = ""
    replay_parts: tuple[object, ...] = ()


@dataclass(frozen=True)
class _ProviderResponse:
    text: str = ""
    reasoning: str = ""
    replay_content: object | None = None
    tool_call: ToolCallRequest | None = None


class TerminalChatBackend(Protocol):
    def is_configured(self) -> bool: ...

    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
        tools: tuple[ProviderToolSpec, ...] | None = None,
    ) -> AsyncIterator[ChatEvent]: ...

    def cancel(self, chat_slug: str) -> None: ...


class MistralChatBackend:
    def __init__(self, credential_store: CredentialStore | None = None) -> None:
        self._client = None
        self._client_api_key = ""
        self._credential_store = credential_store or KeyringCredentialStore()
        self._streams: dict[str, object] = {}

    def is_configured(self) -> bool:
        settings = self.model_settings()
        if settings.provider == LOCAL_OPENAI_PROVIDER:
            return settings.local_endpoint_configured() and bool(self._api_key(LOCAL_OPENAI_PROVIDER))
        return bool(self._api_key(settings.provider))

    def model_settings(self) -> ModelSettings:
        return load_model_settings()

    def save_model_settings(self, settings: ModelSettings) -> None:
        save_model_settings(settings)

    def has_api_key(self, provider: str | None = None) -> bool:
        resolved_provider = provider or self.model_settings().provider
        if resolved_provider == LOCAL_OPENAI_PROVIDER:
            try:
                return bool(self._credential_store.get_secret(LOCAL_OPENAI_ACCOUNT).strip())
            except CredentialStoreError:
                return False
        return bool(self._api_key(resolved_provider))

    def set_api_key(self, api_key: str, provider: str | None = None) -> None:
        clean = api_key.strip()
        if not clean:
            return
        self._credential_store.set_secret(self._credential_account(provider or self.model_settings().provider), clean)
        self._client = None
        self._client_api_key = ""

    def clear_api_key(self, provider: str | None = None) -> None:
        self._credential_store.delete_secret(self._credential_account(provider or self.model_settings().provider))
        self._client = None
        self._client_api_key = ""

    def credential_status(self):
        return self._credential_store.status()

    def context_window_tokens(self) -> int:
        try:
            return self.model_settings().context_window_tokens
        except Exception:
            return DEFAULT_CONTEXT_WINDOW_TOKENS

    async def test_connection(self, settings: MistralModelSettings, api_key: str = "") -> ConnectionTestResult:
        clean_api_key = api_key.strip() or self._api_key(settings.provider)
        if settings.provider == LOCAL_OPENAI_PROVIDER:
            if not settings.model.strip():
                return ConnectionTestResult(False, "Local model ID is missing. Enter the model loaded by your local OpenAI-compatible server.")
            try:
                await self._complete_local_openai_once(
                    settings=settings,
                    api_key=clean_api_key or DEFAULT_LOCAL_OPENAI_API_KEY,
                    system_prompt="Reply exactly: OK",
                    messages=[{"role": "user", "content": "Connection test. Reply exactly: OK"}],
                    tools=None,
                    max_tokens=PROVIDER_TEST_MAX_TOKENS,
                )
            except Exception as exc:
                return ConnectionTestResult(False, self._format_provider_error(exc, provider=settings.provider, for_connection=True))
            return ConnectionTestResult(True, f"Live local OpenAI-compatible connection succeeded. {settings.model_label()} is ready.")
        if not clean_api_key:
            return ConnectionTestResult(False, f"{provider_label(settings.provider)} API key is missing. Paste a key or save one first.")
        if settings.provider != MISTRAL_PROVIDER:
            try:
                await asyncio.wait_for(
                    self._complete_provider_once(
                        settings=settings,
                        api_key=clean_api_key,
                        system_prompt="Reply exactly: OK",
                        messages=[{"role": "user", "content": "Connection test. Reply exactly: OK"}],
                        tools=None,
                        max_tokens=PROVIDER_TEST_MAX_TOKENS,
                    ),
                    timeout=PROVIDER_CONNECTION_TIMEOUT_SECONDS,
                )
            except asyncio.TimeoutError:
                return ConnectionTestResult(False, f"{settings.provider_label()} connection test timed out after {PROVIDER_CONNECTION_TIMEOUT_SECONDS} seconds. Check the selected model, provider status, and network connection.")
            except Exception as exc:
                if settings.provider == GOOGLE_PROVIDER and self._is_rate_limit_error(str(exc)):
                    if await self._google_model_is_reachable(settings, clean_api_key):
                        retry_after = self._retry_after_text(str(exc))
                        retry_line = (
                            f" Try again {retry_after}."
                            if retry_after
                            else " Wait for the Google generation quota window to reset."
                        )
                        return ConnectionTestResult(
                            False,
                            (
                                "Google API key and model are configured, but Gemini generation quota is currently "
                                f"exhausted.{retry_line}"
                            ),
                        )
                return ConnectionTestResult(False, self._format_provider_error(exc, provider=settings.provider, for_connection=True))
            return ConnectionTestResult(True, f"Live {settings.provider_label()} connection succeeded. {settings.model_label()} is ready.")
        try:
            client = self._get_client(clean_api_key)
            request: dict[str, object] = {
                "model": settings.model,
                "messages": [
                    {
                        "role": "user",
                        "content": "Connection test. Reply with exactly: OK",
                    }
                ],
                "max_tokens": 32,
                "temperature": 0,
                "top_p": 1,
                "timeout_ms": 30000,
            }
            reasoning_effort = settings.provider_payload_reasoning_effort()
            if reasoning_effort and model_supports_reasoning(settings.model):
                request["reasoning_effort"] = reasoning_effort
            await client.chat.complete_async(**request)
        except Exception as exc:
            return ConnectionTestResult(False, self._format_provider_error(exc, provider=settings.provider, for_connection=True))

        reasoning = settings.provider_payload_reasoning_effort()
        reasoning_text = f" with {reasoning} reasoning" if reasoning else " without selectable reasoning"
        return ConnectionTestResult(True, f"Live Mistral connection succeeded. {settings.model}{reasoning_text} is ready.")

    def cancel(self, chat_slug: str) -> None:
        stream = self._streams.get(chat_slug)
        if stream is None:
            return
        response = getattr(stream, "response", None)
        if response is not None:
            asyncio.create_task(response.aclose())
            return
        aclose = getattr(stream, "aclose", None)
        if callable(aclose):
            asyncio.create_task(aclose())

    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
        tools: tuple[ProviderToolSpec, ...] | None = None,
    ) -> AsyncIterator[ChatEvent]:
        settings = self.model_settings()
        api_key = self._api_key(settings.provider)
        if not api_key:
            yield ChatEvent(
                kind="error",
                error=f"{provider_label(settings.provider)} is not configured. Open Model Settings and save an API key.",
            )
            return
        try:
            system_prompt = self._load_system_prompt()
        except RuntimeError as exc:
            yield ChatEvent(kind="error", error=str(exc))
            return

        if settings.provider == LOCAL_OPENAI_PROVIDER:
            if not settings.model.strip():
                yield ChatEvent(kind="error", error="Local model ID is missing. Open Model Settings and enter the model loaded by your local endpoint.")
                return
            async for event in self._stream_local_openai(
                chat_slug=chat_slug,
                settings=settings,
                api_key=api_key or DEFAULT_LOCAL_OPENAI_API_KEY,
                system_prompt=system_prompt,
                messages=self._build_messages(system_prompt, messages, shell_context, request_mode),
                tools=tools if request_mode == "chat" else None,
            ):
                yield event
            return

        if settings.provider == OPENAI_PROVIDER:
            async for event in self._stream_openai_responses(
                chat_slug=chat_slug,
                settings=settings,
                api_key=api_key,
                system_prompt=system_prompt,
                messages=self._build_messages(system_prompt, messages, shell_context, request_mode),
                tools=tools if request_mode == "chat" else None,
            ):
                yield event
            return

        if settings.provider == CLAUDE_PROVIDER:
            async for event in self._stream_claude_messages(
                chat_slug=chat_slug,
                settings=settings,
                api_key=api_key,
                system_prompt=system_prompt,
                messages=self._build_messages(system_prompt, messages, shell_context, request_mode),
                tools=tools if request_mode == "chat" else None,
            ):
                yield event
            return

        if settings.provider == GOOGLE_PROVIDER:
            async for event in self._stream_google_generate_content(
                chat_slug=chat_slug,
                settings=settings,
                api_key=api_key,
                system_prompt=system_prompt,
                messages=self._build_messages(system_prompt, messages, shell_context, request_mode),
                tools=tools if request_mode == "chat" else None,
            ):
                yield event
            return

        if settings.provider != MISTRAL_PROVIDER:
            try:
                response = await self._complete_provider_once(
                    settings=settings,
                    api_key=api_key,
                    system_prompt=system_prompt,
                    messages=self._build_messages(system_prompt, messages, shell_context, request_mode),
                    tools=tools if request_mode == "chat" else None,
                    max_tokens=PROVIDER_REPLY_MAX_TOKENS,
                )
                if response.tool_call is not None:
                    yield ChatEvent(kind="tool_call", tool_call=response.tool_call)
                    return
                if response.reasoning:
                    yield ChatEvent(kind="reasoning_delta", text=response.reasoning)
                if response.text:
                    yield ChatEvent(kind="assistant_delta", text=response.text)
                yield ChatEvent(kind="assistant_done", replay_content=response.replay_content)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                yield ChatEvent(kind="error", error=self._format_provider_error(exc, provider=settings.provider))
            return

        try:
            client = self._get_client(api_key)
            stream_kwargs: dict[str, object] = {
                "model": settings.model,
                "messages": self._build_messages(system_prompt, messages, shell_context, request_mode),
            }
            if request_mode == "chat" and tools:
                stream_kwargs["tools"] = mistral_tools_from_specs(tools)
                stream_kwargs["tool_choice"] = "auto"
                stream_kwargs["parallel_tool_calls"] = False
            reasoning_effort = settings.provider_payload_reasoning_effort()
            if reasoning_effort and model_supports_reasoning(settings.model):
                stream_kwargs["reasoning_effort"] = reasoning_effort
            stream = await client.chat.stream_async(**stream_kwargs)
            self._streams[chat_slug] = stream
            replay_parts: list[object] = []
            async with stream:
                async for event in stream:
                    data = getattr(event, "data", None)
                    choices = getattr(data, "choices", None) or []
                    for choice in choices:
                        delta = getattr(choice, "delta", None)
                        tool_calls = self._tool_calls_from_choice(choice, delta)
                        if tool_calls:
                            yield ChatEvent(kind="tool_call", tool_call=tool_calls[0])
                            return
                        parsed = self._parse_content(getattr(delta, "content", None))
                        replay_parts.extend(parsed.replay_parts)
                        if parsed.reasoning:
                            yield ChatEvent(kind="reasoning_delta", text=parsed.reasoning)
                        if parsed.text:
                            yield ChatEvent(kind="assistant_delta", text=parsed.text)
                        finish_reason = getattr(choice, "finish_reason", None)
                        if finish_reason:
                            yield ChatEvent(kind="assistant_done", replay_content=replay_parts or None)
                            return
            yield ChatEvent(kind="assistant_done", replay_content=replay_parts or None)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            yield ChatEvent(kind="error", error=self._format_provider_error(exc, provider=settings.provider))
        finally:
            self._streams.pop(chat_slug, None)

    def _format_provider_error(self, exc: Exception, *, provider: str = MISTRAL_PROVIDER, for_connection: bool = False) -> str:
        label = provider_label(provider)
        raw = str(exc)
        if self._is_rate_limit_error(raw):
            retry_after = self._retry_after_text(raw)
            retry_line = f"\n\nTry again {retry_after}." if retry_after else "\n\nTry again after the provider rate-limit window resets."
            if for_connection:
                return (
                    f"{label} rate limit reached."
                    f"{retry_line}\n\n"
                    "The connection test reached the provider rate limit. Your key may still be valid; wait for quota "
                    "to reset or choose another provider."
                )
            return (
                f"{label} rate limit reached."
                f"{retry_line}\n\n"
                "This request was not completed. Reduce basket context, use excerpts instead of whole files, "
                "or wait before trying again."
            )
        if isinstance(exc, CredentialStoreError):
            return "Secure credential storage is unavailable or locked. Open Model Settings after unlocking your keychain."
        if self._is_auth_error(raw):
            return (
                f"{label} rejected this API key.\n\n"
                "Open Model Settings, paste a current API key, save it, then run Test connection again."
            )
        if for_connection and self._is_configuration_error(raw):
            return (
                f"{label} rejected the selected model or request settings.\n\n"
                "Choose another model or context/reasoning option in Model Settings, then run Test connection again."
            )
        return (
            f"{label} request failed. The provider returned an error that was not completed. "
            "Check provider configuration, project context size, and network availability before trying again."
        )

    @staticmethod
    def _is_rate_limit_error(raw: str) -> bool:
        lowered = raw.casefold()
        return "429" in lowered or "rate limit" in lowered or "rate_limit" in lowered

    @staticmethod
    def _is_auth_error(raw: str) -> bool:
        lowered = raw.casefold()
        return "401" in lowered or "unauthorized" in lowered or "invalid api key" in lowered or "invalid_api_key" in lowered

    @staticmethod
    def _is_configuration_error(raw: str) -> bool:
        lowered = raw.casefold()
        return (
            "400" in lowered
            or "404" in lowered
            or "invalid_request" in lowered
            or "not_found" in lowered
            or "model_not_found" in lowered
            or ("model" in lowered and ("invalid" in lowered or "not found" in lowered or "does not exist" in lowered))
        )

    @staticmethod
    def _retry_after_text(raw: str) -> str:
        json_match = re.search(r"(\{.*\})", raw, flags=re.DOTALL)
        if json_match:
            try:
                payload = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                payload = {}
            retry_after = payload.get("retry_after") or payload.get("retryAfter")
            if retry_after is not None:
                try:
                    seconds = int(float(retry_after))
                except (TypeError, ValueError):
                    seconds = 0
                if seconds > 0:
                    if seconds >= 60:
                        minutes = max(1, round(seconds / 60))
                        return f"in about {minutes} minute{'s' if minutes != 1 else ''}"
                    return f"in about {seconds} second{'s' if seconds != 1 else ''}"
        retry_match = re.search(r"retry[_ -]?after[\"':= ]+([0-9]+)", raw, flags=re.IGNORECASE)
        if retry_match:
            seconds = int(retry_match.group(1))
            if seconds >= 60:
                minutes = max(1, round(seconds / 60))
                return f"in about {minutes} minute{'s' if minutes != 1 else ''}"
            return f"in about {seconds} second{'s' if seconds != 1 else ''}"
        return ""

    def _api_key(self, provider: str = MISTRAL_PROVIDER) -> str:
        try:
            secret = self._credential_store.get_secret(self._credential_account(provider)).strip()
        except CredentialStoreError:
            return ""
        if provider == LOCAL_OPENAI_PROVIDER:
            return secret or DEFAULT_LOCAL_OPENAI_API_KEY
        return secret

    @staticmethod
    def _credential_account(provider: str) -> str:
        if provider == LOCAL_OPENAI_PROVIDER:
            return LOCAL_OPENAI_ACCOUNT
        return PROVIDER_CREDENTIAL_ACCOUNTS.get(provider, MISTRAL_ACCOUNT)

    def _get_client(self, api_key: str):
        if self._client is None or self._client_api_key != api_key:
            from mistralai.client import Mistral

            self._client = Mistral(api_key=api_key, timeout_ms=180000)
            self._client_api_key = api_key
        return self._client

    async def _google_model_is_reachable(self, settings: MistralModelSettings, api_key: str) -> bool:
        try:
            from google import genai

            await asyncio.wait_for(
                genai.Client(api_key=api_key).aio.models.get(model=settings.model),
                timeout=PROVIDER_CONNECTION_TIMEOUT_SECONDS,
            )
        except Exception:
            return False
        return True

    async def _complete_local_openai_once(
        self,
        *,
        settings: ModelSettings,
        api_key: str,
        system_prompt: str,
        messages: list[dict[str, object]],
        tools: tuple[ProviderToolSpec, ...] | None,
        max_tokens: int,
    ) -> _ProviderResponse:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key or DEFAULT_LOCAL_OPENAI_API_KEY, base_url=normalize_local_openai_base_url(settings.endpoint_url))
        kwargs = self._local_openai_chat_kwargs(settings, messages, tools, max_tokens=max_tokens, stream=False)
        response = await client.chat.completions.create(**kwargs)
        message = response.choices[0].message if getattr(response, "choices", None) else None
        raw_message = self._dump_provider_model(message)
        tool_calls = self._raw_tool_calls(message)
        if tool_calls:
            call = tool_call_request_from_openai(tool_calls[0])
            if call is not None:
                return _ProviderResponse(tool_call=call, replay_content=raw_message)
        content = getattr(message, "content", "") if message is not None else ""
        parsed_text, parsed_reasoning = self._parse_local_reasoning_text(str(content or ""), settings)
        return _ProviderResponse(parsed_text, parsed_reasoning, replay_content=raw_message)

    async def _stream_local_openai(
        self,
        *,
        chat_slug: str,
        settings: ModelSettings,
        api_key: str,
        system_prompt: str,
        messages: list[dict[str, object]],
        tools: tuple[ProviderToolSpec, ...] | None,
    ) -> AsyncIterator[ChatEvent]:
        from openai import AsyncOpenAI

        parser_state = {
            "buffer": "",
            "in_reasoning": False,
            "start": settings.reasoning_start_tag or "<think>",
            "end": settings.reasoning_end_tag or "</think>",
        }
        replay_chunks: list[object] = []
        try:
            client = AsyncOpenAI(api_key=api_key or DEFAULT_LOCAL_OPENAI_API_KEY, base_url=normalize_local_openai_base_url(settings.endpoint_url))
            stream = await client.chat.completions.create(
                **self._local_openai_chat_kwargs(settings, messages, tools, max_tokens=PROVIDER_REPLY_MAX_TOKENS, stream=True)
            )
            self._streams[chat_slug] = stream
            async for chunk in stream:
                replay_chunks.append(self._dump_provider_model(chunk))
                choices = getattr(chunk, "choices", None) or []
                for choice in choices:
                    delta = getattr(choice, "delta", None)
                    tool_calls = self._raw_tool_calls(delta)
                    if tool_calls:
                        call = tool_call_request_from_openai(tool_calls[0])
                        if call is not None:
                            yield ChatEvent(kind="tool_call", tool_call=call)
                            return
                    text = getattr(delta, "content", "") if delta is not None else ""
                    for kind, value in self._consume_local_reasoning_delta(str(text or ""), parser_state):
                        if kind == "reasoning" and value:
                            yield ChatEvent(kind="reasoning_delta", text=value)
                        elif kind == "text" and value:
                            yield ChatEvent(kind="assistant_delta", text=value)
            for kind, value in self._flush_local_reasoning(parser_state):
                if kind == "reasoning" and value:
                    yield ChatEvent(kind="reasoning_delta", text=value)
                elif kind == "text" and value:
                    yield ChatEvent(kind="assistant_delta", text=value)
            yield ChatEvent(kind="assistant_done", replay_content=replay_chunks or None)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            yield ChatEvent(kind="error", error=self._format_provider_error(exc, provider=settings.provider))
        finally:
            self._streams.pop(chat_slug, None)

    async def _stream_claude_messages(
        self,
        *,
        chat_slug: str,
        settings: ModelSettings,
        api_key: str,
        system_prompt: str,
        messages: list[dict[str, object]],
        tools: tuple[ProviderToolSpec, ...] | None,
    ) -> AsyncIterator[ChatEvent]:
        from anthropic import AsyncAnthropic

        replay_events: list[object] = []
        current_tool: dict[str, object] | None = None
        try:
            system_text, conversation = self._provider_system_and_messages(system_prompt, messages)
            kwargs: dict[str, object] = {
                "model": settings.model,
                "system": system_text,
                "messages": self._claude_messages(conversation),
                "max_tokens": PROVIDER_REPLY_MAX_TOKENS,
            }
            kwargs.update(self._claude_reasoning_kwargs(settings))
            if tools:
                kwargs["tools"] = claude_tools_from_specs(tools)
                kwargs["tool_choice"] = {"type": "auto"}
            client = AsyncAnthropic(api_key=api_key)
            stream_manager = client.messages.stream(**kwargs)
            async with stream_manager as stream:
                self._streams[chat_slug] = stream
                async for event in stream:
                    payload = self._dump_provider_model(event)
                    replay_events.append(payload)
                    if not isinstance(payload, dict):
                        continue
                    event_type = str(payload.get("type") or "")
                    content_block = payload.get("content_block")
                    if event_type == "content_block_start" and isinstance(content_block, dict):
                        call = tool_call_request_from_claude(content_block)
                        if call is not None:
                            current_tool = {
                                "type": "tool_use",
                                "id": call.raw_call_id,
                                "name": call.tool_name,
                                "input_json": "",
                            }
                        continue
                    delta = payload.get("delta")
                    if event_type == "content_block_delta" and isinstance(delta, dict):
                        delta_type = str(delta.get("type") or "")
                        text = delta.get("text")
                        thinking = delta.get("thinking")
                        if delta_type == "text_delta" and isinstance(text, str) and text:
                            yield ChatEvent(kind="assistant_delta", text=text)
                        elif delta_type == "thinking_delta" and isinstance(thinking, str) and thinking:
                            yield ChatEvent(kind="reasoning_delta", text=thinking)
                        elif delta_type == "input_json_delta" and current_tool is not None:
                            current_tool["input_json"] = str(current_tool.get("input_json") or "") + str(delta.get("partial_json") or "")
                        continue
                    if event_type == "content_block_stop" and current_tool is not None:
                        raw_call = {
                            "type": "tool_use",
                            "id": current_tool.get("id"),
                            "name": current_tool.get("name"),
                            "input": self._json_arguments(current_tool.get("input_json")),
                        }
                        call = tool_call_request_from_claude(raw_call)
                        if call is not None:
                            yield ChatEvent(kind="tool_call", tool_call=call)
                            return
                        current_tool = None
            yield ChatEvent(kind="assistant_done", replay_content=replay_events or None)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            yield ChatEvent(kind="error", error=self._format_provider_error(exc, provider=settings.provider))
        finally:
            self._streams.pop(chat_slug, None)

    async def _stream_google_generate_content(
        self,
        *,
        chat_slug: str,
        settings: ModelSettings,
        api_key: str,
        system_prompt: str,
        messages: list[dict[str, object]],
        tools: tuple[ProviderToolSpec, ...] | None,
    ) -> AsyncIterator[ChatEvent]:
        from google import genai

        replay_chunks: list[object] = []
        try:
            system_text, conversation = self._provider_system_and_messages(system_prompt, messages)
            config: dict[str, object] = {
                "system_instruction": system_text,
                "max_output_tokens": PROVIDER_REPLY_MAX_TOKENS,
                "temperature": 0.2,
                "top_p": 1,
                "thinking_config": {"thinking_level": settings.reasoning_effort},
            }
            if tools:
                config["tools"] = google_tools_from_specs(tools)
            client = genai.Client(api_key=api_key)
            stream = client.aio.models.generate_content_stream(
                model=settings.model,
                contents=self._google_contents(conversation),
                config=config,
            )
            if inspect.isawaitable(stream):
                stream = await stream
            self._streams[chat_slug] = stream
            async for chunk in stream:
                payload = self._dump_provider_model(chunk)
                replay_chunks.append(payload)
                for kind, value in self._google_stream_parts(payload):
                    if kind == "tool_call":
                        call = tool_call_request_from_google(value)
                        if call is not None:
                            yield ChatEvent(kind="tool_call", tool_call=call)
                            return
                    elif kind == "reasoning" and value:
                        yield ChatEvent(kind="reasoning_delta", text=str(value))
                    elif kind == "text" and value:
                        yield ChatEvent(kind="assistant_delta", text=str(value))
            yield ChatEvent(kind="assistant_done", replay_content=replay_chunks or None)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            yield ChatEvent(kind="error", error=self._format_provider_error(exc, provider=settings.provider))
        finally:
            self._streams.pop(chat_slug, None)

    async def _stream_openai_responses(
        self,
        *,
        chat_slug: str,
        settings: ModelSettings,
        api_key: str,
        system_prompt: str,
        messages: list[dict[str, object]],
        tools: tuple[ProviderToolSpec, ...] | None,
    ) -> AsyncIterator[ChatEvent]:
        from openai import AsyncOpenAI

        replay_events: list[object] = []
        try:
            system_text, conversation = self._provider_system_and_messages(system_prompt, messages)
            client = AsyncOpenAI(api_key=api_key)
            kwargs: dict[str, object] = {
                "model": settings.model,
                "instructions": system_text,
                "input": self._openai_responses_input(conversation),
                "max_output_tokens": PROVIDER_REPLY_MAX_TOKENS,
                "reasoning": {"effort": settings.reasoning_effort},
                "stream": True,
            }
            if tools:
                kwargs["tools"] = self._openai_responses_tools(tools)
                kwargs["tool_choice"] = "auto"
                kwargs["parallel_tool_calls"] = False
            stream = await client.responses.create(**kwargs)
            self._streams[chat_slug] = stream
            async for event in stream:
                payload = self._dump_provider_model(event)
                replay_events.append(payload)
                event_type = str(payload.get("type") if isinstance(payload, dict) else getattr(event, "type", ""))
                if event_type.endswith("output_text.delta"):
                    delta = payload.get("delta") if isinstance(payload, dict) else getattr(event, "delta", "")
                    if isinstance(delta, str) and delta:
                        yield ChatEvent(kind="assistant_delta", text=delta)
                    continue
                if "reasoning" in event_type and event_type.endswith(".delta"):
                    delta = payload.get("delta") if isinstance(payload, dict) else getattr(event, "delta", "")
                    if isinstance(delta, str) and delta:
                        yield ChatEvent(kind="reasoning_delta", text=delta)
                    continue
                item = payload.get("item") if isinstance(payload, dict) else None
                if event_type == "response.output_item.done" and isinstance(item, dict):
                    call = tool_call_request_from_openai(item)
                    if call is not None:
                        yield ChatEvent(kind="tool_call", tool_call=call)
                        return
            yield ChatEvent(kind="assistant_done", replay_content=replay_events or None)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            yield ChatEvent(kind="error", error=self._format_provider_error(exc, provider=settings.provider))
        finally:
            self._streams.pop(chat_slug, None)

    def _local_openai_chat_kwargs(
        self,
        settings: ModelSettings,
        messages: list[dict[str, object]],
        tools: tuple[ProviderToolSpec, ...] | None,
        *,
        max_tokens: int,
        stream: bool,
    ) -> dict[str, object]:
        kwargs: dict[str, object] = {
            "model": settings.model,
            "messages": self._local_openai_messages(messages),
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "stream": stream,
        }
        effort = settings.provider_payload_reasoning_effort()
        if effort:
            kwargs["extra_body"] = {"reasoning_effort": effort}
        if tools:
            kwargs["tools"] = openai_tools_from_specs(tools)
            kwargs["tool_choice"] = "auto"
        return kwargs

    @staticmethod
    def _claude_reasoning_kwargs(settings: ModelSettings) -> dict[str, object]:
        effort = settings.provider_payload_reasoning_effort()
        if not effort:
            return {}
        kwargs: dict[str, object] = {"output_config": {"effort": effort}}
        if settings.model.startswith("claude-opus-4-") or settings.model == "claude-sonnet-4-6":
            kwargs["thinking"] = {"type": "adaptive"}
        return kwargs

    def _local_openai_messages(self, messages: list[dict[str, object]]) -> list[dict[str, object]]:
        payload: list[dict[str, object]] = []
        for message in messages:
            role = str(message.get("role") or "user")
            provider_content = self._message_provider_content(message)
            if role == "tool":
                payload.append(
                    {
                        "role": "tool",
                        "tool_call_id": self._provider_content_tool_call_id(provider_content) or "tool_result",
                        "content": self._content_to_text(message.get("content")),
                    }
                )
                continue
            tool_calls = self._openai_chat_tool_calls(provider_content)
            if role == "assistant" and tool_calls:
                payload.append(
                    {
                        "role": "assistant",
                        "content": self._content_to_text(message.get("content")) or None,
                        "tool_calls": tool_calls,
                    }
                )
                continue
            content = self._content_to_text(message.get("content"))
            if not content:
                continue
            payload.append({"role": "assistant" if role == "assistant" else role, "content": content})
        return payload or [{"role": "user", "content": "Hello."}]

    @staticmethod
    def _dump_provider_model(value: object) -> object:
        if value is None:
            return None
        model_dump = getattr(value, "model_dump", None)
        if callable(model_dump):
            try:
                return model_dump(exclude_none=True, warnings=False)
            except TypeError:
                return model_dump()
        if isinstance(value, (dict, list, str, int, float, bool)):
            return deepcopy(value)
        return str(value)

    def _parse_local_reasoning_text(self, text: str, settings: ModelSettings) -> tuple[str, str]:
        state = {
            "buffer": "",
            "in_reasoning": False,
            "start": settings.reasoning_start_tag or "<think>",
            "end": settings.reasoning_end_tag or "</think>",
        }
        text_parts: list[str] = []
        reasoning_parts: list[str] = []
        for kind, value in self._consume_local_reasoning_delta(text, state):
            if kind == "reasoning":
                reasoning_parts.append(value)
            else:
                text_parts.append(value)
        for kind, value in self._flush_local_reasoning(state):
            if kind == "reasoning":
                reasoning_parts.append(value)
            else:
                text_parts.append(value)
        return "".join(text_parts), "".join(reasoning_parts)

    @staticmethod
    def _safe_reasoning_holdback(buffer: str, marker: str) -> int:
        max_len = min(len(buffer), max(0, len(marker) - 1))
        for size in range(max_len, 0, -1):
            if marker.startswith(buffer[-size:]):
                return size
        return 0

    def _consume_local_reasoning_delta(self, text: str, state: dict[str, object]) -> list[tuple[str, str]]:
        state["buffer"] = str(state.get("buffer") or "") + text
        start = str(state.get("start") or "<think>")
        end = str(state.get("end") or "</think>")
        output: list[tuple[str, str]] = []
        while True:
            buffer = str(state.get("buffer") or "")
            if not buffer:
                break
            if bool(state.get("in_reasoning")):
                index = buffer.find(end)
                if index >= 0:
                    output.append(("reasoning", buffer[:index]))
                    state["buffer"] = buffer[index + len(end) :]
                    state["in_reasoning"] = False
                    continue
                holdback = self._safe_reasoning_holdback(buffer, end)
                flush = buffer[:-holdback] if holdback else buffer
                state["buffer"] = buffer[-holdback:] if holdback else ""
                if flush:
                    output.append(("reasoning", flush))
                break
            index = buffer.find(start)
            if index >= 0:
                output.append(("text", buffer[:index]))
                state["buffer"] = buffer[index + len(start) :]
                state["in_reasoning"] = True
                continue
            holdback = self._safe_reasoning_holdback(buffer, start)
            flush = buffer[:-holdback] if holdback else buffer
            state["buffer"] = buffer[-holdback:] if holdback else ""
            if flush:
                output.append(("text", flush))
            break
        return output

    def _flush_local_reasoning(self, state: dict[str, object]) -> list[tuple[str, str]]:
        buffer = str(state.get("buffer") or "")
        state["buffer"] = ""
        if not buffer:
            return []
        return [("reasoning" if bool(state.get("in_reasoning")) else "text", buffer)]

    async def _complete_provider_once(
        self,
        *,
        settings: ModelSettings,
        api_key: str,
        system_prompt: str,
        messages: list[dict[str, object]],
        tools: tuple[ProviderToolSpec, ...] | None,
        max_tokens: int,
    ) -> _ProviderResponse:
        if settings.provider == CLAUDE_PROVIDER:
            return await self._complete_claude(settings, api_key, system_prompt, messages, tools, max_tokens)
        if settings.provider == GOOGLE_PROVIDER:
            return await self._complete_google(settings, api_key, system_prompt, messages, tools, max_tokens)
        if settings.provider == OPENAI_PROVIDER:
            return await self._complete_openai(settings, api_key, system_prompt, messages, tools, max_tokens)
        raise RuntimeError(f"Unsupported provider: {settings.provider}")

    async def _complete_claude(
        self,
        settings: ModelSettings,
        api_key: str,
        system_prompt: str,
        messages: list[dict[str, object]],
        tools: tuple[ProviderToolSpec, ...] | None,
        max_tokens: int,
    ) -> _ProviderResponse:
        from anthropic import AsyncAnthropic

        system_text, conversation = self._provider_system_and_messages(system_prompt, messages)
        kwargs: dict[str, object] = {
            "model": settings.model,
            "system": system_text,
            "messages": self._claude_messages(conversation),
            "max_tokens": max_tokens,
            "timeout": PROVIDER_CONNECTION_TIMEOUT_SECONDS if max_tokens <= PROVIDER_TEST_MAX_TOKENS else None,
        }
        kwargs.update(self._claude_reasoning_kwargs(settings))
        if tools:
            kwargs["tools"] = claude_tools_from_specs(tools)
            kwargs["tool_choice"] = {"type": "auto"}
        payload = self._dump_provider_model(await AsyncAnthropic(api_key=api_key).messages.create(**kwargs))
        if not isinstance(payload, dict):
            raise RuntimeError("Claude returned an unexpected response shape.")
        return self._parse_claude_response(payload)

    async def _complete_google(
        self,
        settings: ModelSettings,
        api_key: str,
        system_prompt: str,
        messages: list[dict[str, object]],
        tools: tuple[ProviderToolSpec, ...] | None,
        max_tokens: int,
    ) -> _ProviderResponse:
        from google import genai

        system_text, conversation = self._provider_system_and_messages(system_prompt, messages)
        config: dict[str, object] = {
            "system_instruction": system_text,
            "max_output_tokens": max_tokens,
            "temperature": 0,
            "top_p": 1,
        }
        if tools:
            config["tools"] = google_tools_from_specs(tools)
        response = await asyncio.wait_for(
            genai.Client(api_key=api_key).aio.models.generate_content(
                model=settings.model,
                contents=self._google_contents(conversation),
                config=config,
            ),
            timeout=PROVIDER_CONNECTION_TIMEOUT_SECONDS if max_tokens <= PROVIDER_TEST_MAX_TOKENS else PROVIDER_REQUEST_TIMEOUT_SECONDS,
        )
        payload = self._dump_provider_model(response)
        if not isinstance(payload, dict):
            raise RuntimeError("Google returned an unexpected response shape.")
        return self._parse_google_response(payload)

    async def _complete_openai(
        self,
        settings: ModelSettings,
        api_key: str,
        system_prompt: str,
        messages: list[dict[str, object]],
        tools: tuple[ProviderToolSpec, ...] | None,
        max_tokens: int,
    ) -> _ProviderResponse:
        from openai import AsyncOpenAI

        system_text, conversation = self._provider_system_and_messages(system_prompt, messages)
        kwargs: dict[str, object] = {
            "model": settings.model,
            "instructions": system_text,
            "input": self._openai_responses_input(conversation),
            "max_output_tokens": max_tokens,
            "timeout": PROVIDER_CONNECTION_TIMEOUT_SECONDS if max_tokens <= PROVIDER_TEST_MAX_TOKENS else None,
        }
        effort = settings.provider_payload_reasoning_effort()
        if effort:
            kwargs["reasoning"] = {"effort": effort}
        if tools:
            kwargs["tools"] = self._openai_responses_tools(tools)
            kwargs["tool_choice"] = "auto"
            kwargs["parallel_tool_calls"] = False
        payload = self._dump_provider_model(await AsyncOpenAI(api_key=api_key).responses.create(**kwargs))
        if not isinstance(payload, dict):
            raise RuntimeError("OpenAI returned an unexpected response shape.")
        return self._parse_openai_response(payload)

    async def _post_json_async(self, url: str, headers: dict[str, str], payload: dict[str, object]) -> dict[str, object]:
        return await asyncio.to_thread(self._post_json, url, headers, payload)

    def _post_json(self, url: str, headers: dict[str, str], payload: dict[str, object]) -> dict[str, object]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib_request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib_request.urlopen(request, timeout=PROVIDER_REQUEST_TIMEOUT_SECONDS) as response:
                response_body = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"{exc.code} {exc.reason}: {self._redact_provider_error(error_body)}") from exc
        except urllib_error.URLError as exc:
            raise RuntimeError(str(exc.reason)) from exc
        try:
            payload_obj = json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Provider returned a non-JSON response.") from exc
        if not isinstance(payload_obj, dict):
            raise RuntimeError("Provider returned an unexpected response shape.")
        return payload_obj

    @staticmethod
    def _redact_provider_error(raw: str) -> str:
        redacted = re.sub(r"(api[_ -]?key|token|authorization)[\"':= ]+[^,}\s]+", r"\1=<redacted>", raw, flags=re.IGNORECASE)
        if len(redacted) > 1000:
            redacted = redacted[:1000] + "..."
        return redacted

    def _provider_system_and_messages(
        self,
        system_prompt: str,
        messages: list[dict[str, object]],
    ) -> tuple[str, list[dict[str, object]]]:
        system_parts: list[str] = []
        conversation: list[dict[str, object]] = []
        for message in messages:
            role = str(message.get("role") or "")
            if role == "system":
                text = self._content_to_text(message.get("content"))
                if text:
                    system_parts.append(text)
                continue
            conversation.append(dict(message))
        if not system_parts and system_prompt.strip():
            system_parts.append(system_prompt.strip())
        return "\n\n".join(system_parts), conversation

    def _claude_messages(self, conversation: list[dict[str, object]]) -> list[dict[str, object]]:
        payload: list[dict[str, object]] = []
        for message in conversation:
            role = str(message.get("role") or "user")
            provider_content = self._message_provider_content(message)
            if role == "tool":
                call_id = self._provider_content_tool_call_id(provider_content) or "tool_result"
                payload.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": call_id,
                                "content": self._content_to_text(message.get("content")),
                            }
                        ],
                    }
                )
                continue
            tool_blocks = self._claude_tool_use_blocks(provider_content)
            if role == "assistant" and tool_blocks:
                payload.append({"role": "assistant", "content": tool_blocks})
                continue
            content = self._content_to_text(message.get("content"))
            if not content:
                continue
            payload.append({"role": "assistant" if role == "assistant" else "user", "content": content})
        return payload or [{"role": "user", "content": "Hello."}]

    def _google_contents(self, conversation: list[dict[str, object]]) -> list[dict[str, object]]:
        payload: list[dict[str, object]] = []
        for message in conversation:
            role = str(message.get("role") or "user")
            provider_content = self._message_provider_content(message)
            if role == "tool":
                payload.append(
                    {
                        "role": "user",
                        "parts": [
                            {
                                "functionResponse": {
                                    "name": self._provider_content_tool_name(provider_content) or "tool_result",
                                    "response": {"result": self._content_to_text(message.get("content"))},
                                }
                            }
                        ],
                    }
                )
                continue
            function_parts = self._google_function_call_parts(provider_content)
            if role == "assistant" and function_parts:
                payload.append({"role": "model", "parts": function_parts})
                continue
            content = self._content_to_text(message.get("content"))
            if not content:
                continue
            payload.append({"role": "model" if role == "assistant" else "user", "parts": [{"text": content}]})
        return payload or [{"role": "user", "parts": [{"text": "Hello."}]}]

    def _openai_responses_input(self, conversation: list[dict[str, object]]) -> list[dict[str, object]]:
        payload: list[dict[str, object]] = []
        for message in conversation:
            role = str(message.get("role") or "user")
            provider_content = self._message_provider_content(message)
            if role == "tool":
                call_id = self._provider_content_tool_call_id(provider_content) or f"exegesis-tool-{len(payload) + 1}"
                payload.append(
                    {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": self._content_to_text(message.get("content")),
                    }
                )
                continue
            function_calls = self._openai_function_call_items(provider_content)
            if role == "assistant" and function_calls:
                payload.extend(function_calls)
                continue
            content = self._content_to_text(message.get("content"))
            if not content:
                continue
            payload.append({"role": "assistant" if role == "assistant" else "user", "content": content})
        return payload or [{"role": "user", "content": "Hello."}]

    @staticmethod
    def _openai_responses_tools(specs: tuple[ProviderToolSpec, ...] | list[ProviderToolSpec]) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "name": spec.name,
                "description": spec.description,
                "parameters": deepcopy(spec.parameters),
            }
            for spec in specs
        ]

    @staticmethod
    def _content_to_text(content: object) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    text = item.get("text") or item.get("content")
                    if isinstance(text, str):
                        parts.append(text)
            return "\n".join(part for part in parts if part)
        if isinstance(content, dict):
            text = content.get("text") or content.get("content")
            if isinstance(text, str):
                return text
        return str(content)

    @staticmethod
    def _message_provider_content(message: dict[str, object]) -> object:
        return message.get("provider_content") if message.get("provider_content") is not None else message

    @staticmethod
    def _provider_content_tool_call_id(provider_content: object) -> str | None:
        if not isinstance(provider_content, dict):
            return None
        call_id = provider_content.get("tool_call_id") or provider_content.get("call_id")
        if call_id:
            return str(call_id)
        tool_calls = provider_content.get("tool_calls")
        if isinstance(tool_calls, list) and tool_calls:
            first = tool_calls[0]
            if isinstance(first, dict):
                raw_id = first.get("id") or first.get("call_id")
                return str(raw_id) if raw_id else None
        return None

    @staticmethod
    def _provider_content_tool_name(provider_content: object) -> str | None:
        if not isinstance(provider_content, dict):
            return None
        name = provider_content.get("name")
        if name:
            return str(name)
        tool_calls = provider_content.get("tool_calls")
        if isinstance(tool_calls, list) and tool_calls:
            first = tool_calls[0]
            if isinstance(first, dict):
                function = first.get("function")
                if isinstance(function, dict) and function.get("name"):
                    return str(function["name"])
        return None

    def _openai_chat_tool_calls(self, provider_content: object) -> list[dict[str, object]]:
        calls: list[dict[str, object]] = []
        for call in self._provider_content_tool_calls(provider_content):
            function = call.get("function") if isinstance(call, dict) else None
            if not isinstance(function, dict):
                continue
            name = function.get("name")
            if not isinstance(name, str):
                continue
            raw_arguments = function.get("arguments")
            arguments = raw_arguments if isinstance(raw_arguments, str) else json.dumps(self._json_arguments(raw_arguments))
            calls.append(
                {
                    "id": str(call.get("id") or call.get("call_id") or f"call_{len(calls) + 1}"),
                    "type": "function",
                    "function": {"name": name, "arguments": arguments},
                }
            )
        return calls

    def _claude_tool_use_blocks(self, provider_content: object) -> list[dict[str, object]]:
        if not isinstance(provider_content, dict):
            return []
        blocks: list[dict[str, object]] = []
        for call in self._provider_content_tool_calls(provider_content):
            function = call.get("function") if isinstance(call, dict) else None
            if not isinstance(function, dict):
                continue
            name = function.get("name")
            if not isinstance(name, str):
                continue
            blocks.append(
                {
                    "type": "tool_use",
                    "id": str(call.get("id") or call.get("call_id") or f"toolu_{len(blocks) + 1}"),
                    "name": name,
                    "input": self._json_arguments(function.get("arguments")),
                }
            )
        return blocks

    def _google_function_call_parts(self, provider_content: object) -> list[dict[str, object]]:
        parts: list[dict[str, object]] = []
        for call in self._provider_content_tool_calls(provider_content):
            function = call.get("function") if isinstance(call, dict) else None
            if not isinstance(function, dict):
                continue
            name = function.get("name")
            if not isinstance(name, str):
                continue
            parts.append({"functionCall": {"name": name, "args": self._json_arguments(function.get("arguments"))}})
        return parts

    def _openai_function_call_items(self, provider_content: object) -> list[dict[str, object]]:
        items: list[dict[str, object]] = []
        for call in self._provider_content_tool_calls(provider_content):
            function = call.get("function") if isinstance(call, dict) else None
            if not isinstance(function, dict):
                continue
            name = function.get("name")
            if not isinstance(name, str):
                continue
            items.append(
                {
                    "type": "function_call",
                    "call_id": str(call.get("id") or call.get("call_id") or f"call_{len(items) + 1}"),
                    "name": name,
                    "arguments": function.get("arguments") if isinstance(function.get("arguments"), str) else json.dumps(self._json_arguments(function.get("arguments"))),
                }
            )
        return items

    @staticmethod
    def _provider_content_tool_calls(provider_content: object) -> list[dict[str, object]]:
        if not isinstance(provider_content, dict):
            return []
        raw_calls = provider_content.get("tool_calls")
        if isinstance(raw_calls, list):
            return [dict(call) for call in raw_calls if isinstance(call, dict)]
        return []

    @staticmethod
    def _json_arguments(raw: object) -> dict[str, object]:
        if raw is None:
            return {}
        if isinstance(raw, dict):
            return dict(raw)
        if isinstance(raw, str):
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                return {"_raw": raw}
            return dict(payload) if isinstance(payload, dict) else {"value": payload}
        return {"value": str(raw)}

    def _google_stream_parts(self, payload: object) -> list[tuple[str, object]]:
        if not isinstance(payload, dict):
            return []
        candidates = payload.get("candidates")
        first = candidates[0] if isinstance(candidates, list) and candidates else {}
        content = first.get("content") if isinstance(first, dict) else {}
        parts = content.get("parts") if isinstance(content, dict) else []
        output: list[tuple[str, object]] = []
        for part in parts if isinstance(parts, list) else []:
            if not isinstance(part, dict):
                continue
            function_call = part.get("functionCall") or part.get("function_call")
            if isinstance(function_call, dict):
                output.append(("tool_call", part))
                continue
            text = part.get("text")
            if isinstance(text, str) and text:
                output.append(("reasoning" if part.get("thought") else "text", text))
        return output

    def _parse_claude_response(self, payload: dict[str, object]) -> _ProviderResponse:
        content = payload.get("content")
        blocks = content if isinstance(content, list) else []
        text_parts: list[str] = []
        reasoning_parts: list[str] = []
        for block in blocks:
            if not isinstance(block, dict):
                continue
            tool_call = tool_call_request_from_claude(block)
            if tool_call is not None:
                return _ProviderResponse(tool_call=tool_call, replay_content=blocks)
            block_type = str(block.get("type") or "")
            if block_type == "thinking":
                thinking = block.get("thinking") or block.get("text")
                if isinstance(thinking, str):
                    reasoning_parts.append(thinking)
            elif block_type == "text":
                text = block.get("text")
                if isinstance(text, str):
                    text_parts.append(text)
        return _ProviderResponse("\n".join(text_parts), "\n".join(reasoning_parts), replay_content=blocks or None)

    def _parse_google_response(self, payload: dict[str, object]) -> _ProviderResponse:
        candidates = payload.get("candidates")
        first = candidates[0] if isinstance(candidates, list) and candidates else {}
        content = first.get("content") if isinstance(first, dict) else {}
        parts = content.get("parts") if isinstance(content, dict) else []
        text_parts: list[str] = []
        reasoning_parts: list[str] = []
        for part in parts if isinstance(parts, list) else []:
            if not isinstance(part, dict):
                continue
            tool_call = tool_call_request_from_google(part)
            if tool_call is not None:
                return _ProviderResponse(tool_call=tool_call, replay_content=parts)
            text = part.get("text")
            if isinstance(text, str):
                if part.get("thought"):
                    reasoning_parts.append(text)
                else:
                    text_parts.append(text)
        return _ProviderResponse("\n".join(text_parts), "\n".join(reasoning_parts), replay_content=parts or None)

    def _parse_openai_response(self, payload: dict[str, object]) -> _ProviderResponse:
        output = payload.get("output")
        items = output if isinstance(output, list) else []
        text_parts: list[str] = []
        reasoning_parts: list[str] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            tool_call = tool_call_request_from_openai(item)
            if tool_call is not None:
                return _ProviderResponse(tool_call=tool_call, replay_content=items)
            item_type = str(item.get("type") or "")
            if item_type == "reasoning":
                summary = item.get("summary")
                if isinstance(summary, list):
                    reasoning_parts.extend(self._content_to_text(part) for part in summary)
                elif isinstance(summary, str):
                    reasoning_parts.append(summary)
                continue
            if item_type == "message":
                content = item.get("content")
                if isinstance(content, list):
                    for part in content:
                        if not isinstance(part, dict):
                            continue
                        text = part.get("text")
                        if isinstance(text, str):
                            text_parts.append(text)
                continue
            text = item.get("text")
            if isinstance(text, str):
                text_parts.append(text)
        fallback_text = payload.get("output_text")
        if not text_parts and isinstance(fallback_text, str):
            text_parts.append(fallback_text)
        return _ProviderResponse("\n".join(text_parts), "\n".join(reasoning_parts), replay_content=items or None)

    def _system_prompt_path(self) -> Path:
        override = os.environ.get("EXEGESIS_SYSTEM_PROMPT_PATH")
        if override and is_local_developer_mode():
            return Path(override).expanduser()
        return DEFAULT_SYSTEM_PROMPT_PATH

    def _load_system_prompt(self) -> str:
        path = self._system_prompt_path()
        if path == DEFAULT_SYSTEM_PROMPT_PATH:
            try:
                prompt, _identity = load_verified_prompt(
                    DEFAULT_SYSTEM_PROMPT_PATH,
                    DEFAULT_SYSTEM_PROMPT_MANIFEST_PATH,
                    require_manifest=is_release_mode(),
                )
            except PromptIntegrityError as exc:
                raise RuntimeError(str(exc)) from exc
            return prompt
        try:
            prompt = path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise RuntimeError(f"System prompt is unavailable: {path} ({exc})") from exc
        if not prompt:
            raise RuntimeError(f"System prompt is empty: {path}")
        return prompt

    def _build_messages(
        self,
        system_prompt: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str,
    ) -> list[dict[str, object]]:
        mode = request_mode if request_mode in {"chat", "draft", "rewrite", "summary"} else "chat"
        transcript_policy = ""
        if shell_context.document_type == "transcript" and shell_context.confidentiality_mode != "local-confidential":
            document_content = (
                "[Transcript metadata only. The full transcript text is intentionally withheld because this is a "
                "non-confidential project. Do not claim to know, summarize, quote, analyze, or answer questions about "
                "the transcript content unless the user provides excerpts, selected text, snippets, or search results "
                "in this chat.]"
            )
            transcript_policy = (
                "- Transcript context policy: full transcript text is not available in this non-confidential model "
                "context. If the user asks about the active transcript, start the response by saying the full "
                "transcript is withheld in non-confidential mode. Do not ask how you can assist with the transcript. "
                "Ask how you can assist with the project, or invite the user to provide excerpts, selected passages, "
                "snippets, or search results for transcript-specific help.\n"
            )
        else:
            document_content = shell_context.document_content.strip() or "(empty document)"
        section_context = self._document_sections_context(document_content)
        context_message = {
            "role": "system",
            "content": (
                "Current shell context:\n"
                f"- Project: {shell_context.project_name}\n"
                f"- Active document: {shell_context.document_title}\n"
                f"- Active document type: {shell_context.document_type}\n"
                f"- Confidentiality mode: {shell_context.confidentiality_mode}\n"
                f"{transcript_policy}"
                "- Use only the project, document, basket, selected-text, and notebook context provided here. "
                "Do not claim unavailable capabilities or hidden context.\n\n"
                "Notebook action inference:\n"
                "- If the user asks to write, draft, compose, generate, or add prose without naming a target, infer the active document as the target and use draft_into_document.\n"
                "- If the user names an existing section such as abstract, introduction, findings, or conclusion, infer that section as the draft insertion target and set insert_after_heading when using draft_into_document.\n"
                "- If selected text is active and the user asks to make it shorter/clearer/stronger, revise it, rewrite it, tighten it, or otherwise edit it without naming a target, infer the active selection as the target and use rewrite_selection.\n\n"
                "Available document sections:\n"
                f"{section_context}\n\n"
                "Current open document content:\n"
                "<current_document>\n"
                f"{document_content}\n"
                "</current_document>\n\n"
                f"{self._selection_context(shell_context)}"
                f"{self._mode_instruction(mode, shell_context.basket_context)}"
            ),
        }
        payload: list[dict[str, object]] = [
            {"role": "system", "content": system_prompt},
            context_message,
        ]
        for message in messages:
            if not message.content and message.streaming:
                continue
            message_payload = message.payload_content()
            if isinstance(message_payload, dict) and isinstance(message_payload.get("role"), str):
                payload.append(message_payload)
            else:
                payload.append({"role": message.role, "content": message_payload})
        return payload

    @classmethod
    def _document_sections_context(cls, document_content: str) -> str:
        headings = cls._document_headings(document_content)
        if not headings:
            return "(none detected)"
        return "\n".join(f"- {heading}" for heading in headings)

    @staticmethod
    def _document_headings(document_content: str) -> tuple[str, ...]:
        headings: list[str] = []
        for line in document_content.splitlines():
            match = re.match(r"^#{1,6}\s+(.+?)\s*$", line.strip())
            if match is None:
                continue
            title = match.group(1).strip().strip("*_`").rstrip(":").strip()
            if title:
                headings.append(title)
        return tuple(headings)

    def _tool_calls_from_choice(self, choice: object, delta: object) -> list[ToolCallRequest]:
        raw_calls = self._raw_tool_calls(delta)
        if not raw_calls:
            message = getattr(choice, "message", None)
            raw_calls = self._raw_tool_calls(message)
        calls: list[ToolCallRequest] = []
        for raw_call in raw_calls:
            call = tool_call_request_from_mistral(raw_call)
            if call is not None:
                calls.append(call)
        return calls

    @staticmethod
    def _raw_tool_calls(container: object) -> list[object]:
        if container is None:
            return []
        if isinstance(container, dict):
            raw_calls = container.get("tool_calls")
        else:
            raw_calls = getattr(container, "tool_calls", None)
        if raw_calls is None:
            return []
        if isinstance(raw_calls, dict):
            return [raw_calls]
        if isinstance(raw_calls, (list, tuple)):
            return list(raw_calls)
        return []

    def _selection_context(self, shell_context: ShellChatContext) -> str:
        if not shell_context.selected_text:
            return ""
        start = shell_context.selection_start
        end = shell_context.selection_end
        range_text = f"{start}-{end}" if start is not None and end is not None else "unknown"
        return (
            "Active rewrite selection:\n"
            f"- Character range: {range_text}\n"
            "<selected_text>\n"
            f"{shell_context.selected_text.strip()}\n"
            "</selected_text>\n\n"
        )

    def _mode_instruction(self, request_mode: str, basket_context: str) -> str:
        if request_mode == "draft":
            basket_block = (
                "Current basket context:\n"
                "<basket>\n"
                f"{basket_context.strip()}\n"
                "</basket>\n\n"
                if basket_context.strip()
                else "Current basket context:\n<basket>\n(empty basket)\n</basket>\n\n"
            )
            return (
                "Mode: draft\n"
                "- Use the terminal instruction plus the open document and basket context to generate new text for direct insertion into the open document.\n"
                "- If the user asks for a body section, paragraph, or passage, return only that body text. Do not repeat the document title, current section heading, or surrounding outline headings unless the user explicitly asks for headings.\n"
                "- Document types are opinionated workflow signals: drafts are the main manuscript, memos are writer guidance, summaries are compressed synthesis, transcripts are raw source material, and literature docs are evidence/reference material.\n"
                "- Return only the text to insert into the document. Do not add preambles, explanations, markdown fences, or chatty framing.\n\n"
                f"{basket_block}"
            )
        if request_mode == "rewrite":
            basket_block = (
                "Current basket context:\n"
                "<basket>\n"
                f"{basket_context.strip()}\n"
                "</basket>\n\n"
                if basket_context.strip()
                else "Current basket context:\n<basket>\n(empty basket)\n</basket>\n\n"
            )
            return (
                "Mode: rewrite\n"
                "- Use the terminal instruction, the current open document, basket context, and the explicit <selected_text> block to rewrite only the selected passage.\n"
                "- Return only replacement text for the <selected_text> block. Do not rewrite or summarize the whole document.\n"
                "- Do not add commentary, explanations, markdown fences, or diff markers.\n"
                "- Preserve the surrounding document voice unless the instruction clearly asks for a stronger shift.\n\n"
                f"{basket_block}"
            )
        if request_mode == "summary":
            return (
                "Mode: summary\n"
                "- Summarize the current open document according to the user's requested target length.\n"
                "- Use the current open document as the source of truth.\n"
                "- Return only the summary text. Do not add preambles, explanations, markdown fences, or provenance notes.\n"
            )
        return (
            "Mode: chat\n"
            "- Answer questions about the current open document.\n"
            "- Use the current open document as the primary source of truth for your answer.\n"
            "- Keep answers grounded in the context explicitly provided by Exegesis.\n"
        )

    def _parse_content(self, content: object) -> _ParsedContent:
        if content is None:
            return _ParsedContent()
        if isinstance(content, str):
            replay = ({"type": "text", "text": content},) if content else ()
            return _ParsedContent(text=content, replay_parts=replay)
        items = content if isinstance(content, list) else [content]
        text_parts: list[str] = []
        reasoning_parts: list[str] = []
        replay_parts: list[object] = []
        for item in items:
            item_text, item_reasoning = self._extract_chunk_text(item)
            if item_text:
                text_parts.append(item_text)
            if item_reasoning:
                reasoning_parts.append(item_reasoning)
            replay = self._chunk_replay_payload(item)
            if replay is not None:
                replay_parts.append(replay)
        return _ParsedContent(
            text="".join(text_parts),
            reasoning="".join(reasoning_parts),
            replay_parts=tuple(replay_parts),
        )

    def _extract_chunk_text(self, chunk: object) -> tuple[str, str]:
        if chunk is None:
            return "", ""
        if isinstance(chunk, str):
            return chunk, ""
        if isinstance(chunk, dict):
            chunk_type = str(chunk.get("type") or chunk.get("kind") or "").casefold()
            if "think" in chunk_type or "reason" in chunk_type:
                return "", self._extract_reasoning_text(chunk)
            return self._extract_visible_text(chunk), ""
        chunk_type = chunk.__class__.__name__.casefold()
        if "think" in chunk_type or "reason" in chunk_type:
            return "", self._extract_reasoning_text(chunk)
        if hasattr(chunk, "thinking"):
            return "", self._extract_reasoning_text(chunk)
        return self._extract_visible_text(chunk), ""

    def _extract_reasoning_text(self, chunk: object) -> str:
        if isinstance(chunk, dict):
            thinking = chunk.get("thinking") or chunk.get("content") or chunk.get("text") or ""
            return self._coerce_text(thinking)
        thinking = getattr(chunk, "thinking", None)
        if thinking is None:
            thinking = getattr(chunk, "content", None)
        if thinking is None:
            thinking = getattr(chunk, "text", None)
        return self._coerce_text(thinking)

    def _extract_visible_text(self, chunk: object) -> str:
        if isinstance(chunk, dict):
            text = chunk.get("text")
            if isinstance(text, str):
                return text
            content = chunk.get("content")
            return self._coerce_text(content)
        text = getattr(chunk, "text", None)
        if isinstance(text, str):
            return text
        content = getattr(chunk, "content", None)
        return self._coerce_text(content)

    def _coerce_text(self, content: object) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(self._coerce_text(item) for item in content)
        if isinstance(content, dict):
            text = content.get("text")
            if isinstance(text, str):
                return text
            nested = content.get("content") or content.get("thinking")
            return self._coerce_text(nested)
        text = getattr(content, "text", None)
        if isinstance(text, str):
            return text
        nested = getattr(content, "content", None)
        if nested is not None:
            return self._coerce_text(nested)
        return ""

    def _chunk_replay_payload(self, chunk: object) -> object | None:
        if chunk is None:
            return None
        if isinstance(chunk, str):
            return {"type": "text", "text": chunk} if chunk else None
        if isinstance(chunk, dict):
            return self._canonical_replay_chunk(chunk)
        model_dump = getattr(chunk, "model_dump", None)
        if callable(model_dump):
            try:
                payload = model_dump(exclude_none=True, warnings=False)
            except TypeError:
                payload = model_dump()
            return self._canonical_replay_chunk(payload) if isinstance(payload, dict) else payload
        as_dict = getattr(chunk, "dict", None)
        if callable(as_dict):
            try:
                payload = as_dict(exclude_none=True)
            except TypeError:
                payload = as_dict()
            return self._canonical_replay_chunk(payload) if isinstance(payload, dict) else payload
        text = getattr(chunk, "text", None)
        if isinstance(text, str):
            return {"type": "text", "text": text}
        thinking = getattr(chunk, "thinking", None)
        if thinking is not None:
            return {"type": "thinking", "thinking": self._canonical_thinking_chunks(thinking)}
        return None

    def _canonical_replay_chunk(self, chunk: dict[str, object]) -> dict[str, object]:
        chunk_type = str(chunk.get("type") or chunk.get("kind") or "").casefold()
        if "think" in chunk_type or "reason" in chunk_type or "thinking" in chunk:
            thinking = chunk.get("thinking") or chunk.get("content") or chunk.get("text") or ""
            return {"type": "thinking", "thinking": self._canonical_thinking_chunks(thinking)}
        return chunk

    def _canonical_thinking_chunks(self, thinking: object) -> list[dict[str, str]]:
        if isinstance(thinking, list):
            chunks = [
                {"type": "text", "text": text}
                for text in (self._coerce_text(item) for item in thinking)
                if text
            ]
            return chunks
        text = self._coerce_text(thinking)
        return [{"type": "text", "text": text}] if text else []


__all__ = [
    "ChatEvent",
    "ChatMessage",
    "DEFAULT_MISTRAL_MODEL",
    "DEFAULT_SYSTEM_PROMPT_MANIFEST_PATH",
    "DEFAULT_SYSTEM_PROMPT_PATH",
    "MistralChatBackend",
    "ShellChatContext",
    "TerminalChatBackend",
]
