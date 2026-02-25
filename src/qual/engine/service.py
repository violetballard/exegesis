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
    context_health: str
    transition_summary: str
    context_repair_ratio: float
    bootstrap_signature: str
    context_delta_items: int
    bootstrap_health_summary: str
    context_retention_ratio: float
    bootstrap_context_summary: str
    context_stability: str
    context_direction: str
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
        context_transition = self._context_transition(
            has_persisted=bool(original_item_ids),
            repaired_count=repaired_count,
        )
        context_health = self._context_health(
            has_persisted=bool(original_item_ids),
            repaired_count=repaired_count,
        )
        context_repair_ratio = self._context_repair_ratio(
            original_count=len(original_item_ids),
            repaired_count=repaired_count,
        )
        context_delta_items = len(sanitized) - len(original_item_ids)
        context_direction = self._context_direction(context_delta_items)
        context_retention_ratio = self._context_retention_ratio(
            original_count=len(original_item_ids),
            active_count=len(sanitized),
        )
        context_stability = "stable" if context_delta_items == 0 and repaired_count == 0 else "changed"
        flow_state = "ready" if not vault.is_locked else "vault-locked"
        bootstrap = BootstrapState(
            flow_state=flow_state,
            vault_transition=vault_transition,
            context_source="persisted" if original_item_ids else "empty",
            context_transition=context_transition,
            context_health=context_health,
            transition_summary=f"{vault_transition}/{context_transition}",
            context_repair_ratio=context_repair_ratio,
            bootstrap_signature=f"{flow_state}|{vault_transition}|{context_health}",
            context_delta_items=context_delta_items,
            bootstrap_health_summary=self._bootstrap_health_summary(
                context_health=context_health,
                context_repair_ratio=context_repair_ratio,
            ),
            context_retention_ratio=context_retention_ratio,
            bootstrap_context_summary=self._bootstrap_context_summary(
                context_transition=context_transition,
                context_health=context_health,
                context_retention_ratio=context_retention_ratio,
            ),
            context_stability=context_stability,
            context_direction=context_direction,
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

    @staticmethod
    def _context_health(*, has_persisted: bool, repaired_count: int) -> str:
        if not has_persisted:
            return "fresh"
        if repaired_count == 0:
            return "clean"
        return "repaired"

    @staticmethod
    def _context_repair_ratio(*, original_count: int, repaired_count: int) -> float:
        if original_count == 0:
            return 0.0
        return repaired_count / original_count

    @staticmethod
    def _context_retention_ratio(*, original_count: int, active_count: int) -> float:
        if original_count == 0:
            return 1.0 if active_count == 0 else 0.0
        return active_count / original_count

    @staticmethod
    def _bootstrap_health_summary(*, context_health: str, context_repair_ratio: float) -> str:
        return f"{context_health}:{context_repair_ratio:.2%}"

    @staticmethod
    def _bootstrap_context_summary(
        *,
        context_transition: str,
        context_health: str,
        context_retention_ratio: float,
    ) -> str:
        return f"{context_transition}|{context_health}|{context_retention_ratio:.2%}"

    @staticmethod
    def _context_direction(context_delta_items: int) -> str:
        if context_delta_items > 0:
            return "growth"
        if context_delta_items < 0:
            return "shrink"
        return "flat"
