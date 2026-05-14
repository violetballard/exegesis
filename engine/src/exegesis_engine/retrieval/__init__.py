from src.qual.engine import retrieval as _engine_retrieval
from exegesis_engine.retrieval.search_service import (
    RetrievalConstraints,
    RetrievalDocHit,
    RetrievalHit,
    RetrievalQuery,
    RetrievalResult,
    RetrievalService,
)

for _export_name in _engine_retrieval.__all__:
    globals()[_export_name] = getattr(_engine_retrieval, _export_name)

_SERVICE_EXPORTS = [
    "RetrievalConstraints",
    "RetrievalDocHit",
    "RetrievalHit",
    "RetrievalQuery",
    "RetrievalResult",
    "RetrievalService",
]


def _canonical_export_names() -> list[str]:
    export_names = list(_engine_retrieval.__all__)
    insert_after = "DEFERRED_STRATEGY_IDS"
    insertion_index = export_names.index(insert_after) + 1 if insert_after in export_names else 0
    for export_name in reversed(_SERVICE_EXPORTS):
        if export_name not in export_names:
            export_names.insert(insertion_index, export_name)
    return export_names


__all__ = _canonical_export_names()
