from __future__ import annotations

from dataclasses import dataclass

from src.qual.config import validate_project_name
from src.qual.context.store import ContextBasketStore
from src.qual.context.basket import ContextBasket
from src.qual.drafting.service import DraftingService
from src.qual.storage.vault import VaultService, VaultState


@dataclass(frozen=True)
class BootstrapState:
    flow_state: str
    vault_transition: str
    context_source: str
    context_transition: str
    original_context_items: int
    active_context_items: int
    repaired_context_items: int


@dataclass
class EngineRuntime:
    vault: VaultState
    basket: ContextBasket
    drafting: DraftingService
    bootstrap: BootstrapState


class EngineService:
    """Application service layer with clear sub-service boundaries."""

    def __init__(self) -> None:
        self._vault_service = VaultService()
        self._drafting_service = DraftingService()

    def bootstrap(self, *, app_data_dir, project_name: str) -> EngineRuntime:
        safe_project_name = validate_project_name(project_name)
        project_root = app_data_dir / safe_project_name
        vault_transition = "opened" if project_root.exists() else "created"
        vault = self._vault_service.create_or_open(app_data_dir, safe_project_name)
        basket_store = ContextBasketStore(app_data_dir)
        basket = basket_store.load()
        original_item_ids = list(basket.item_ids)
        sanitized, repaired_count = self._sanitize_item_ids(original_item_ids)
        basket.item_ids = sanitized
        if sanitized != original_item_ids:
            basket_store.save(basket)
        bootstrap = BootstrapState(
            flow_state="ready" if not vault.is_locked else "vault-locked",
            vault_transition=vault_transition,
            context_source="persisted" if original_item_ids else "empty",
            context_transition=self._context_transition(
                has_persisted=bool(original_item_ids),
                repaired_count=repaired_count,
            ),
            original_context_items=len(original_item_ids),
            active_context_items=len(sanitized),
            repaired_context_items=repaired_count,
        )
        return EngineRuntime(
            vault=vault,
            basket=basket,
            drafting=self._drafting_service,
            bootstrap=bootstrap,
        )

    @staticmethod
    def _sanitize_item_ids(values: list[str]) -> tuple[list[str], int]:
        cleaned: list[str] = []
        seen: set[str] = set()
        repaired_count = 0
        for raw in values:
            normalized = raw.strip()
            if not normalized:
                repaired_count += 1
                continue
            if normalized in seen:
                repaired_count += 1
                continue
            if normalized != raw:
                repaired_count += 1
            seen.add(normalized)
            cleaned.append(normalized)
        return cleaned, repaired_count

    @staticmethod
    def _context_transition(*, has_persisted: bool, repaired_count: int) -> str:
        if not has_persisted:
            return "fresh"
        if repaired_count > 0:
            return "loaded-repaired"
        return "loaded-clean"
