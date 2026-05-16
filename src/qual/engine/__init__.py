"""Engine package with lazy public exports.

Importing the package eagerly used to pull in the run pipeline, which in turn
imported retrieval/docindex code and created a circular import for callers that
only needed lower-level engine modules. Keep the package import lightweight and
resolve public symbols on demand.
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

_EXPORTS: dict[str, tuple[str, str]] = {
    "EngineRuntime": ("src.qual.engine.service", "EngineRuntime"),
    "EngineService": ("src.qual.engine.service", "EngineService"),
    "EngineRunFlowResult": ("src.qual.engine.run_pipeline", "EngineRunFlowResult"),
    "EngineRunFlowSnapshot": ("src.qual.engine.run_pipeline", "EngineRunFlowSnapshot"),
    "EngineRunRecord": ("src.qual.engine.run_pipeline", "EngineRunRecord"),
    "EngineRunService": ("src.qual.engine.run_pipeline", "EngineRunService"),
    "RunArtifact": ("src.qual.engine.run_pipeline", "RunArtifact"),
    "RunEvent": ("src.qual.engine.run_pipeline", "RunEvent"),
    "RunSummary": ("src.qual.engine.run_pipeline", "RunSummary"),
}

if TYPE_CHECKING:
    from src.qual.engine.run_pipeline import (
        EngineRunFlowResult,
        EngineRunFlowSnapshot,
        EngineRunRecord,
        EngineRunService,
        RunArtifact,
        RunEvent,
        RunSummary,
    )
    from src.qual.engine.service import EngineRuntime, EngineService

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    try:
        module_name, attr_name = _EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted({*globals(), *_EXPORTS})
