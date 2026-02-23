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
    payload = constraints if constraints is not None else {}
    query = RetrievalQuery(
        query_text=query_text,
        scope=scope,
        intent=intent,  # type: ignore[arg-type]
        constraints=RetrievalConstraints(
            max_results=int(payload.get("max_results", 10)),
            section_hint=payload.get("section_hint"),  # type: ignore[arg-type]
            prefer_exact_matches=bool(payload.get("prefer_exact_matches", False)),
        ),
        confidentiality_profile=confidentiality_profile,  # type: ignore[arg-type]
    )
    return service.retrieve_auto(query)
