from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from exegesis_textual.actions.registry import ProviderToolSpec, ToolCallRequest


def mistral_tools_from_specs(specs: tuple[ProviderToolSpec, ...] | list[ProviderToolSpec]) -> list[dict[str, Any]]:
    return [_openai_compatible_tool(spec) for spec in specs]


def openai_tools_from_specs(specs: tuple[ProviderToolSpec, ...] | list[ProviderToolSpec]) -> list[dict[str, Any]]:
    return [_openai_compatible_tool(spec) for spec in specs]


def claude_tools_from_specs(specs: tuple[ProviderToolSpec, ...] | list[ProviderToolSpec]) -> list[dict[str, Any]]:
    return [
        {
            "name": spec.name,
            "description": spec.description,
            "input_schema": deepcopy(spec.parameters),
        }
        for spec in specs
    ]


def google_tools_from_specs(specs: tuple[ProviderToolSpec, ...] | list[ProviderToolSpec]) -> list[dict[str, Any]]:
    declarations = [
        {
            "name": spec.name,
            "description": spec.description,
            "parameters": _google_schema(deepcopy(spec.parameters)),
        }
        for spec in specs
    ]
    return [{"function_declarations": declarations}] if declarations else []


def _openai_compatible_tool(spec: ProviderToolSpec) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": spec.name,
            "description": spec.description,
            "parameters": deepcopy(spec.parameters),
        },
    }


def _google_schema(schema: object) -> object:
    if isinstance(schema, dict):
        return {
            key: _google_schema(value)
            for key, value in schema.items()
            if key not in {"additionalProperties", "$schema", "unevaluatedProperties"}
        }
    if isinstance(schema, list):
        return [_google_schema(item) for item in schema]
    return schema


def parse_tool_arguments(raw: object) -> dict[str, Any]:
    if raw is None or raw == "":
        return {}
    if isinstance(raw, dict):
        return dict(raw)
    if isinstance(raw, str):
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return {"_raw": raw}
        return dict(payload) if isinstance(payload, dict) else {"value": payload}
    model_dump = getattr(raw, "model_dump", None)
    if callable(model_dump):
        try:
            payload = model_dump(exclude_none=True)
        except TypeError:
            payload = model_dump()
        return dict(payload) if isinstance(payload, dict) else {"value": payload}
    return {"value": str(raw)}


def tool_call_request_from_mistral(raw_call: object) -> ToolCallRequest | None:
    if raw_call is None:
        return None
    if isinstance(raw_call, dict):
        function = raw_call.get("function") or {}
        name = function.get("name") if isinstance(function, dict) else None
        arguments = function.get("arguments") if isinstance(function, dict) else None
        call_id = raw_call.get("id")
        if isinstance(name, str) and name:
            return ToolCallRequest(
                provider="mistral",
                tool_name=name,
                arguments=parse_tool_arguments(arguments),
                raw_call_id=str(call_id) if call_id else None,
                raw_provider_content=deepcopy(raw_call),
            )
        return None
    function = getattr(raw_call, "function", None)
    name = getattr(function, "name", None) if function is not None else None
    arguments = getattr(function, "arguments", None) if function is not None else None
    call_id = getattr(raw_call, "id", None)
    if isinstance(name, str) and name:
        return ToolCallRequest(
            provider="mistral",
            tool_name=name,
            arguments=parse_tool_arguments(arguments),
            raw_call_id=str(call_id) if call_id else None,
            raw_provider_content=_dump_raw_call(raw_call),
        )
    return None


def tool_call_request_from_openai(raw_call: object) -> ToolCallRequest | None:
    if raw_call is None:
        return None
    payload = _dump_raw_call(raw_call)
    if not isinstance(payload, dict):
        return None
    call_type = payload.get("type")
    if call_type not in {None, "function_call", "function"}:
        return None
    function = payload.get("function")
    name = payload.get("name")
    arguments = payload.get("arguments")
    if isinstance(function, dict):
        name = name or function.get("name")
        arguments = arguments if arguments is not None else function.get("arguments")
    call_id = payload.get("call_id") or payload.get("id")
    if isinstance(name, str) and name:
        return ToolCallRequest(
            provider="openai",
            tool_name=name,
            arguments=parse_tool_arguments(arguments),
            raw_call_id=str(call_id) if call_id else None,
            raw_provider_content=deepcopy(payload),
        )
    return None


def tool_call_request_from_claude(raw_call: object) -> ToolCallRequest | None:
    if raw_call is None:
        return None
    payload = _dump_raw_call(raw_call)
    if not isinstance(payload, dict):
        return None
    if payload.get("type") != "tool_use":
        return None
    name = payload.get("name")
    arguments = payload.get("input")
    call_id = payload.get("id")
    if isinstance(name, str) and name:
        return ToolCallRequest(
            provider="claude",
            tool_name=name,
            arguments=parse_tool_arguments(arguments),
            raw_call_id=str(call_id) if call_id else None,
            raw_provider_content=deepcopy(payload),
        )
    return None


def tool_call_request_from_google(raw_call: object) -> ToolCallRequest | None:
    if raw_call is None:
        return None
    payload = _dump_raw_call(raw_call)
    if not isinstance(payload, dict):
        return None
    function_call = payload.get("functionCall") or payload.get("function_call")
    if not isinstance(function_call, dict):
        return None
    name = function_call.get("name")
    arguments = function_call.get("args") or function_call.get("arguments")
    call_id = function_call.get("id") or payload.get("id")
    if isinstance(name, str) and name:
        return ToolCallRequest(
            provider="google",
            tool_name=name,
            arguments=parse_tool_arguments(arguments),
            raw_call_id=str(call_id) if call_id else None,
            raw_provider_content=deepcopy(payload),
        )
    return None


def _dump_raw_call(raw_call: object) -> object:
    if isinstance(raw_call, dict):
        return deepcopy(raw_call)
    model_dump = getattr(raw_call, "model_dump", None)
    if callable(model_dump):
        try:
            return model_dump(exclude_none=True)
        except TypeError:
            return model_dump()
    as_dict = getattr(raw_call, "dict", None)
    if callable(as_dict):
        try:
            return as_dict(exclude_none=True)
        except TypeError:
            return as_dict()
    return str(raw_call)


__all__ = [
    "claude_tools_from_specs",
    "google_tools_from_specs",
    "mistral_tools_from_specs",
    "openai_tools_from_specs",
    "parse_tool_arguments",
    "tool_call_request_from_claude",
    "tool_call_request_from_google",
    "tool_call_request_from_mistral",
    "tool_call_request_from_openai",
]
