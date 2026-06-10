from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator, Protocol

from exegesis_textual.services.credentials import (
    CredentialStore,
    CredentialStoreError,
    KeyringCredentialStore,
    MISTRAL_ACCOUNT,
)
from exegesis_textual.services.model_settings import (
    DEFAULT_MISTRAL_MODEL,
    MistralModelSettings,
    load_mistral_model_settings,
    model_supports_reasoning,
    save_mistral_model_settings,
)
from exegesis_textual.services.projects import is_local_developer_mode, is_release_mode
from exegesis_textual.services.prompt_integrity import PromptIntegrityError, load_verified_prompt

DEFAULT_SYSTEM_PROMPT_PATH = Path(__file__).with_name("prompts") / "writer_system_prompt.md"
DEFAULT_SYSTEM_PROMPT_MANIFEST_PATH = DEFAULT_SYSTEM_PROMPT_PATH.with_name("writer_system_prompt.manifest.json")


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


@dataclass(frozen=True)
class ConnectionTestResult:
    ok: bool
    message: str


@dataclass(frozen=True)
class _ParsedContent:
    text: str = ""
    reasoning: str = ""
    replay_parts: tuple[object, ...] = ()


class TerminalChatBackend(Protocol):
    def is_configured(self) -> bool: ...

    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
    ) -> AsyncIterator[ChatEvent]: ...

    def cancel(self, chat_slug: str) -> None: ...


class MistralChatBackend:
    def __init__(self, credential_store: CredentialStore | None = None) -> None:
        self._client = None
        self._client_api_key = ""
        self._credential_store = credential_store or KeyringCredentialStore()
        self._streams: dict[str, object] = {}

    def is_configured(self) -> bool:
        return bool(self._api_key())

    def model_settings(self) -> MistralModelSettings:
        return load_mistral_model_settings()

    def save_model_settings(self, settings: MistralModelSettings) -> None:
        save_mistral_model_settings(settings)

    def has_api_key(self) -> bool:
        return bool(self._api_key())

    def set_api_key(self, api_key: str) -> None:
        clean = api_key.strip()
        if not clean:
            return
        self._credential_store.set_secret(MISTRAL_ACCOUNT, clean)
        self._client = None
        self._client_api_key = ""

    def clear_api_key(self) -> None:
        self._credential_store.delete_secret(MISTRAL_ACCOUNT)
        self._client = None
        self._client_api_key = ""

    def credential_status(self):
        return self._credential_store.status()

    async def test_connection(self, settings: MistralModelSettings, api_key: str = "") -> ConnectionTestResult:
        clean_api_key = api_key.strip() or self._api_key()
        if not clean_api_key:
            return ConnectionTestResult(False, "Mistral API key is missing. Paste a key or save one first.")
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
            return ConnectionTestResult(False, self._format_provider_error(exc))

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

    async def stream_reply(
        self,
        chat_slug: str,
        messages: list[ChatMessage],
        shell_context: ShellChatContext,
        request_mode: str = "chat",
    ) -> AsyncIterator[ChatEvent]:
        api_key = self._api_key()
        if not api_key:
            yield ChatEvent(
                kind="error",
                error="Mistral is not configured. Open Model Settings and save a Mistral API key.",
            )
            return
        try:
            system_prompt = self._load_system_prompt()
        except RuntimeError as exc:
            yield ChatEvent(kind="error", error=str(exc))
            return

        try:
            settings = self.model_settings()
            client = self._get_client(api_key)
            stream_kwargs: dict[str, object] = {
                "model": settings.model,
                "messages": self._build_messages(system_prompt, messages, shell_context, request_mode),
            }
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
            yield ChatEvent(kind="error", error=self._format_provider_error(exc))
        finally:
            self._streams.pop(chat_slug, None)

    def _format_provider_error(self, exc: Exception) -> str:
        raw = str(exc)
        if self._is_rate_limit_error(raw):
            retry_after = self._retry_after_text(raw)
            retry_line = f"\n\nTry again {retry_after}." if retry_after else "\n\nTry again after the provider rate-limit window resets."
            return (
                "Mistral rate limit reached."
                f"{retry_line}\n\n"
                "This request was not completed. Reduce basket context, use excerpts instead of whole files, "
                "or wait before trying again."
            )
        if isinstance(exc, CredentialStoreError):
            return "Secure credential storage is unavailable or locked. Open Model Settings after unlocking your keychain."
        if self._is_auth_error(raw):
            return (
                "Mistral rejected this API key.\n\n"
                "Open Model Settings, paste a current Mistral API key, save it, then run Test connection again."
            )
        return (
            "Mistral request failed. The provider returned an error that was not completed. "
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

    def _api_key(self) -> str:
        try:
            return self._credential_store.get_secret(MISTRAL_ACCOUNT).strip()
        except CredentialStoreError:
            return ""

    def _get_client(self, api_key: str):
        if self._client is None or self._client_api_key != api_key:
            from mistralai.client import Mistral

            self._client = Mistral(api_key=api_key, timeout_ms=180000)
            self._client_api_key = api_key
        return self._client

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
        if shell_context.document_type == "transcript":
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
            payload.append({"role": message.role, "content": message.payload_content()})
        return payload

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
            return _ParsedContent(text=content, replay_parts=(content,))
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
        if isinstance(chunk, (str, dict)):
            return chunk
        model_dump = getattr(chunk, "model_dump", None)
        if callable(model_dump):
            try:
                return model_dump(exclude_none=True)
            except TypeError:
                return model_dump()
        as_dict = getattr(chunk, "dict", None)
        if callable(as_dict):
            try:
                return as_dict(exclude_none=True)
            except TypeError:
                return as_dict()
        text = getattr(chunk, "text", None)
        if isinstance(text, str):
            return {"type": "text", "text": text}
        thinking = getattr(chunk, "thinking", None)
        if thinking is not None:
            return {"type": "thinking", "thinking": self._coerce_text(thinking)}
        return None


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
