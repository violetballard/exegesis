"""Canonical FTS-first retrieval package."""

from exegesis_engine.retrieval.facade import *  # noqa: F401,F403
from exegesis_engine.retrieval.facade import __all__ as _FACADE_EXPORTS
from exegesis_engine.retrieval.helpers import *  # noqa: F401,F403
from exegesis_engine.retrieval.service import (
    RetrievalConstraints,
    RetrievalDocHit,
    RetrievalHit,
    RetrievalQuery,
    RetrievalResult,
    RetrievalService,
)

_SERVICE_EXPORTS = [
    "RetrievalConstraints",
    "RetrievalDocHit",
    "RetrievalHit",
    "RetrievalQuery",
    "RetrievalResult",
    "RetrievalService",
]

__all__ = [*_FACADE_EXPORTS]
_insert_at = __all__.index("DEFERRED_STRATEGY_IDS") + 1
for _offset, _export_name in enumerate(_SERVICE_EXPORTS):
    if _export_name not in __all__:
        __all__.insert(_insert_at + _offset, _export_name)
