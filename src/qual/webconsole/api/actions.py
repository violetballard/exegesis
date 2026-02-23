from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from src.qual.ui.a2ui import A2UISessionStore, ActionRef, execute_action_with_policy_gate


class ActionPolicyGate(Protocol):
    def allow_action(self, action_id: str, payload: dict[str, Any], *, policy_sensitive: bool) -> bool:
        ...


class ActionExecutor(Protocol):
    def execute(self, action: ActionRef) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class DenyAllPolicyGate:
    """Integration-safe default: no policy bypass without explicit wiring."""

    def allow_action(self, action_id: str, payload: dict[str, Any], *, policy_sensitive: bool) -> bool:
        return False


@dataclass(frozen=True)
class StubActionExecutor:
    """Stub executor for the initial backend slice; replace with engine integration."""

    def execute(self, action: ActionRef) -> dict[str, Any]:
        return {"status": "accepted", "action_id": action.id, "stub": True}


@dataclass
class ActionGateway:
    sessions: A2UISessionStore
    policy_gate: ActionPolicyGate
    executor: ActionExecutor

    def execute(self, *, session_id: str, action: ActionRef) -> dict[str, Any]:
        capabilities = self.sessions.get(session_id)
        result = execute_action_with_policy_gate(
            action=action,
            capabilities=capabilities,
            policy_gate=self.policy_gate,
            executor=self.executor.execute,
        )
        if not isinstance(result, dict):
            return {"status": "ok"}
        return result
