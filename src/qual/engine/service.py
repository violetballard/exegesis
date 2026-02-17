from __future__ import annotations

from dataclasses import dataclass

from src.qual.context.store import ContextBasketStore
from src.qual.context.basket import ContextBasket
from src.qual.drafting.service import DraftingService
from src.qual.storage.vault import VaultService, VaultState


@dataclass
class EngineRuntime:
    vault: VaultState
    basket: ContextBasket
    drafting: DraftingService


class EngineService:
    """Application service layer with clear sub-service boundaries."""

    def __init__(self) -> None:
        self._vault_service = VaultService()
        self._drafting_service = DraftingService()

    def bootstrap(self, *, app_data_dir, project_name: str) -> EngineRuntime:
        vault = self._vault_service.create_or_open(app_data_dir, project_name)
        basket_store = ContextBasketStore(app_data_dir)
        basket = basket_store.load()
        original_item_ids = list(basket.item_ids)
        sanitized = self._sanitize_item_ids(original_item_ids)
        basket.item_ids = sanitized
        if sanitized != original_item_ids:
            basket_store.save(basket)
        return EngineRuntime(vault=vault, basket=basket, drafting=self._drafting_service)

    @staticmethod
    def _sanitize_item_ids(values: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for raw in values:
            normalized = raw.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            cleaned.append(normalized)
        return cleaned
