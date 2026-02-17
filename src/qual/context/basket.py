from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ContextBasket:
    item_ids: list[str] = field(default_factory=list)

    def add(self, item_id: str) -> None:
        if item_id not in self.item_ids:
            self.item_ids.append(item_id)

    def remove(self, item_id: str) -> None:
        self.item_ids = [x for x in self.item_ids if x != item_id]
