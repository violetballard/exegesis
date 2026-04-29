from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol


@dataclass(frozen=True)
class StrategyRun:
    strategy_id: str
    hits: list[Any]
    elapsed_ms: int
    cache_used: bool


class RetrievalStrategy(Protocol):
    id: str

    def supports(self, query: Any) -> bool:
        ...

    def retrieve(self, query: Any, *, candidate_doc_ids: tuple[str, ...]) -> StrategyRun:
        ...
