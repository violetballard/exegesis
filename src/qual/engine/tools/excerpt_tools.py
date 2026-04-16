from __future__ import annotations

from src.qual.docindex.service import DocIndexService
from src.qual.retrieval.service import RetrievalService


def fetch_excerpt(
    service: RetrievalService,
    *,
    excerpt_id: str,
    confidentiality_profile: str = "confidential",
):
    return service.fetch_excerpt(
        excerpt_id,
        confidentiality_profile=confidentiality_profile,
    )


def pin_to_context_set(service: DocIndexService, *, context_set_id: str, excerpt_id: str):
    return service.pin_to_context_set(context_set_id, excerpt_id)
