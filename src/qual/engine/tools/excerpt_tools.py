from __future__ import annotations

from src.qual.docindex.service import DocIndexService


def fetch_excerpt(service: DocIndexService, *, excerpt_id: str):
    return service.fetch_excerpt(excerpt_id)


def pin_to_context_set(service: DocIndexService, *, context_set_id: str, excerpt_id: str):
    return service.pin_to_context_set(context_set_id, excerpt_id)
