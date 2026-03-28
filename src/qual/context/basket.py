import math
from dataclasses import dataclass, field


@dataclass
class ContextBasket:
    item_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.normalize()

    @staticmethod
    def _normalize_item_id(item_id: object) -> str:
        if not isinstance(item_id, str):
            if isinstance(item_id, bool):
                return ""
            if isinstance(item_id, int):
                return str(item_id).strip()
            if isinstance(item_id, float):
                if not math.isfinite(item_id):
                    return ""
                return str(item_id).strip()
            return ""
        return item_id.strip()

    def add(self, item_id: object) -> None:
        self.normalize()
        normalized = self._normalize_item_id(item_id)
        if not normalized:
            return
        if normalized not in self.item_ids:
            self.item_ids.append(normalized)

    def remove(self, item_id: object) -> None:
        self.normalize()
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
