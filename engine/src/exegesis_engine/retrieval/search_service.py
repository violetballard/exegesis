"""Canonical retrieval compat shim.

The retrieval implementation currently lives in ``src.qual.retrieval.service``.
Expose that implementation through the engine package so canonical imports and
compat imports resolve to the same objects during the staged migration.
"""

from src.qual.retrieval.service import (
    RetrievalConstraints,
    RetrievalDocHit,
    RetrievalHit,
    RetrievalQuery,
    RetrievalResult,
    RetrievalService,
)

__all__ = [
    "RetrievalConstraints",
    "RetrievalDocHit",
    "RetrievalHit",
    "RetrievalQuery",
    "RetrievalResult",
    "RetrievalService",
]
