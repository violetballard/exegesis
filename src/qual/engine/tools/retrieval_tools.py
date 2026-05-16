from __future__ import annotations

from src.qual.retrieval.service import RetrievalConstraints, RetrievalQuery, RetrievalService


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
    normalized_intent = _normalize_text(intent, field_name="intent")
    query = RetrievalQuery(
        query_text=query_text,
        scope=scope,
        intent=normalized_intent,
        constraints=RetrievalConstraints(
            max_results=_parse_max_results(payload.get("max_results")),
            section_hint=_parse_section_hint(payload.get("section_hint")),
            prefer_exact_matches=_parse_bool(payload.get("prefer_exact_matches"), field_name="prefer_exact_matches"),
        ),
        confidentiality_profile=confidentiality_profile,  # type: ignore[arg-type]
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
