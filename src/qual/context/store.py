from __future__ import annotations

import json
from pathlib import Path

from src.qual.context.basket import ContextBasket


class ContextBasketStore:
    """Persist context basket state for scaffold CLI workflows."""

    def __init__(self, root_dir: Path) -> None:
        self._path = root_dir / "context_basket.json"

    def load(self) -> ContextBasket:
        if not self._path.exists():
            return ContextBasket()
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return ContextBasket()
        if not isinstance(payload, dict):
            return ContextBasket()
        items = payload.get("item_ids", [])
        if not isinstance(items, list):
            return ContextBasket()
        basket = ContextBasket(item_ids=[str(x) for x in items])
        basket.normalize()
        return basket

    def save(self, basket: ContextBasket) -> None:
        basket.normalize()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"schema_version": 1, "item_ids": list(basket.item_ids)}
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self._path)

    def clear(self) -> None:
        if self._path.exists():
            self._path.unlink()
