from __future__ import annotations

from typing import Literal, cast

from src.qual.retrieval.service import RetrievalConstraints, RetrievalQuery, RetrievalService

_RetrievalConfidentialityProfile = Literal["confidential", "standard"]
_SUPPORTED_CONFIDENTIALITY_PROFILES: set[str] = {"confidential", "standard"}


def retrieve_auto(
    service: RetrievalService,
    *,
    query_text: str,
    scope: str,
    intent: str,
    constraints: dict[str, object] | None = None,
    confidentiality_profile: str = "confidential",
):
    payload = _normalize_constraints(constraints)
    normalized_query_text = _normalize_text(query_text, field_name="query_text")
    normalized_scope = _normalize_text(scope, field_name="scope")
    normalized_intent = _normalize_text(intent, field_name="intent")
    normalized_confidentiality_profile = _normalize_confidentiality_profile(confidentiality_profile)
    query = RetrievalQuery(
        query_text=normalized_query_text,
        scope=normalized_scope,
        intent=normalized_intent,
        constraints=RetrievalConstraints(
            max_results=_parse_max_results(payload.get("max_results")),
            doc_types=_parse_doc_types(payload.get("doc_types")),
            date_range=_parse_date_range(payload.get("date_range")),
            require_citations=_parse_bool(
                payload.get("require_citations"),
                field_name="require_citations",
            ),
            section_hint=_parse_section_hint(payload.get("section_hint")),
            prefer_exact_matches=_parse_bool(
                payload.get("prefer_exact_matches"),
                field_name="prefer_exact_matches",
            ),
        ),
        confidentiality_profile=normalized_confidentiality_profile,
    )
    return service.retrieve_auto(query)


def _normalize_constraints(constraints: dict[str, object] | None) -> dict[str, object]:
    if constraints is None:
        return {}
    if not isinstance(constraints, dict):
        raise TypeError("constraints must be a dict when provided")
    return constraints


def _parse_max_results(raw: object) -> int:
    if raw is None:
        return 10
    if isinstance(raw, bool):
        raise TypeError("max_results must be an integer")
    if isinstance(raw, int):
        value = raw
    elif isinstance(raw, str) and raw.strip():
        try:
            value = int(raw.strip())
        except ValueError as exc:
            raise TypeError("max_results must be an integer") from exc
    else:
        raise TypeError("max_results must be an integer")
    if value < 1:
        raise ValueError("max_results must be >= 1")
    return value


def _parse_section_hint(raw: object) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise TypeError("section_hint must be a string")
    normalized = raw.strip()
    return normalized or None


def _parse_doc_types(raw: object) -> tuple[str, ...]:
    if raw is None:
        return ()
    if isinstance(raw, str):
        values: object = (raw,)
    else:
        values = raw
    if not isinstance(values, (list, tuple)):
        raise TypeError("doc_types must be a string or sequence of strings")
    seen: set[str] = set()
    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str):
            raise TypeError("doc_types must be a string or sequence of strings")
        doc_type = value.strip().casefold()
        if doc_type and doc_type not in seen:
            seen.add(doc_type)
            normalized.append(doc_type)
    return tuple(sorted(normalized))


def _parse_date_range(raw: object) -> tuple[str, str] | None:
    if raw is None:
        return None
    if not isinstance(raw, (list, tuple)) or len(raw) != 2:
        raise TypeError("date_range must be a two-item sequence of strings")
    normalized: list[str] = []
    for value in raw:
        if not isinstance(value, str):
            raise TypeError("date_range must be a two-item sequence of strings")
        date_value = value.strip()
        if not date_value:
            raise ValueError("date_range values are required")
        normalized.append(date_value)
    return (normalized[0], normalized[1])


def _parse_bool(raw: object, *, field_name: str) -> bool:
    if raw is None:
        return False
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        normalized = raw.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off", ""}:
            return False
    raise TypeError(f"{field_name} must be a boolean")


def _normalize_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def _normalize_confidentiality_profile(value: object) -> _RetrievalConfidentialityProfile:
    if not isinstance(value, str):
        raise TypeError("confidentiality_profile must be a string")
    normalized = value.strip().casefold()
    if normalized not in _SUPPORTED_CONFIDENTIALITY_PROFILES:
        raise ValueError(f"unsupported confidentiality_profile: {normalized}")
    return cast(_RetrievalConfidentialityProfile, normalized)
