from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Protocol

from src.qual.ui.a2ui import A2UISessionStore
from src.qual.webconsole.api.actions import ActionGateway
from src.qual.webconsole.api.validators import parse_a2ui_capabilities, parse_action_ref, require_object
from src.qual.webconsole.auth.session import CSRF_HEADER_NAME, Session, SessionStore, parse_cookie_session_id


class ProviderProbeService(Protocol):
    def get_probe_report(self) -> dict[str, Any]:
        ...

    def run_probe(self) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class ApiRequest:
    method: str
    path: str
    headers: dict[str, str]
    body: bytes = b""


@dataclass(frozen=True)
class ApiResponse:
    status: int
    payload: dict[str, Any]
    headers: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ApiError(Exception):
    status: int
    message: str


@dataclass
class WebConsoleApi:
    session_store: SessionStore
    capability_sessions: A2UISessionStore
    probe_service: ProviderProbeService
    action_gateway: ActionGateway | None = None

    def dispatch(self, request: ApiRequest) -> ApiResponse:
        if request.method == "POST" and request.path == "/api/a2ui/capabilities":
            session = self._require_session(request)
            self._require_csrf(request, session)
            payload = self._parse_json(request.body)
            capabilities = parse_a2ui_capabilities(payload)
            self.capability_sessions.register(session.session_id, capabilities)
            return ApiResponse(
                status=200,
                payload={
                    "ok": True,
                    "session_id": session.session_id,
                    "client_name": capabilities.client_name,
                    "a2ui_version": capabilities.a2ui_version,
                },
            )
        if request.method == "GET" and request.path == "/api/provider/probe_report":
            self._require_session(request)
            report = self.probe_service.get_probe_report()
            return ApiResponse(status=200, payload={"ok": True, "report": report})
        if request.method == "POST" and request.path == "/api/provider/probe":
            session = self._require_session(request)
            self._require_csrf(request, session)
            # Accept optional JSON body for forward-compatible request shape.
            payload = self._parse_json(request.body) if request.body else {}
            require_object(payload)
            report = self.probe_service.run_probe()
            return ApiResponse(status=200, payload={"ok": True, "report": report})
        if request.method == "POST" and request.path == "/api/actions/execute":
            if self.action_gateway is None:
                raise ApiError(status=503, message="Action gateway is not configured")
            session = self._require_session(request)
            self._require_csrf(request, session)
            payload = self._parse_json(request.body)
            action = parse_action_ref(payload)
            result = self.action_gateway.execute(session_id=session.session_id, action=action)
            return ApiResponse(status=200, payload={"ok": True, "result": result})
        raise ApiError(status=404, message="Not found")

    def _parse_json(self, body: bytes) -> dict[str, Any]:
        if not body:
            raise ApiError(status=400, message="JSON request body is required")
        try:
            decoded = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ApiError(status=400, message="Malformed JSON payload") from exc
        try:
            return require_object(decoded)
        except ValueError as exc:
            raise ApiError(status=400, message=str(exc)) from exc

    def _require_session(self, request: ApiRequest) -> Session:
        session_id = parse_cookie_session_id(request.headers.get("cookie"))
        if session_id is None:
            raise ApiError(status=401, message="Missing session cookie")
        session = self.session_store.get(session_id)
        if session is None:
            raise ApiError(status=401, message="Invalid or expired session")
        return session

    def _require_csrf(self, request: ApiRequest, session: Session) -> None:
        sent = request.headers.get(CSRF_HEADER_NAME)
        if not sent or sent != session.csrf_token:
            raise ApiError(status=403, message="Invalid CSRF token")
