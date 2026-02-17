from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ContextBasket:
    item_ids: list[str] = field(default_factory=list)

    @staticmethod
    def _normalize_item_id(item_id: str) -> str:
        return str(item_id).strip()

    def add(self, item_id: str) -> None:
        normalized = self._normalize_item_id(item_id)
        if not normalized:
            return
        if normalized not in self.item_ids:
            self.item_ids.append(normalized)

    def remove(self, item_id: str) -> None:
        normalized = self._normalize_item_id(item_id)
        if not normalized:
            return
        self.item_ids = [x for x in self.item_ids if x != normalized]

    def normalize(self) -> None:
        deduped: list[str] = []
        seen: set[str] = set()
        for raw in self.item_ids:
            item = self._normalize_item_id(raw)
            if not item or item in seen:
                continue
            deduped.append(item)
            seen.add(item)
        self.item_ids = deduped
