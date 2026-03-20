from __future__ import annotations

from typing import Protocol

from src.qual.docindex.service import DocIndexService


class ExcerptFetchService(Protocol):
    def fetch_excerpt(self, excerpt_id: str) -> dict[str, object]: ...


def fetch_excerpt(service: ExcerptFetchService, *, excerpt_id: str):
    return service.fetch_excerpt(excerpt_id)


def pin_to_context_set(service: DocIndexService, *, context_set_id: str, excerpt_id: str):
    return service.pin_to_context_set(context_set_id, excerpt_id)
