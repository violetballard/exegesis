from __future__ import annotations

from exegesis_engine.state.models import BasketItem, WorkflowCard


class PlanService:
    def plan_from_basket(self, basket_items: list[BasketItem]) -> WorkflowCard:
        if not basket_items:
            body = "Basket is empty. Add context items before planning."
        else:
            lines = [f"- Use {item.label} ({item.item_type})" for item in basket_items]
            body = "\n".join(lines)
        return WorkflowCard(
            id="plan-from-basket",
            card_type="plan",
            title="Plan From Basket",
            body=body,
            metadata={"item_count": len(basket_items)},
            actions=[{"id": "save_to_project", "label": "Save plan"}],
        )
