from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Protocol

from src.qual.engine.policy_gate import PolicyGate
from src.qual.ui.a2ui import A2UISessionStore
from src.qual.webconsole.api.actions import ActionGateway
from src.qual.webconsole.api.validators import (
    parse_a2ui_capabilities,
    parse_action_ref,
    parse_provider_probe_request,
    require_object,
    sanitize_probe_report,
)
from src.qual.webconsole.auth.session import (
    CSRF_HEADER_NAME,
    Session,
    SessionStore,
    parse_cookie_session_id,
    serialize_cleared_session_cookie,
)


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
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class WebConsoleApi:
    session_store: SessionStore
    capability_sessions: A2UISessionStore
    probe_service: ProviderProbeService
    action_gateway: ActionGateway | None = None
    secure_cookie: bool = False

    _ALLOWED_METHODS_BY_PATH: dict[str, tuple[str, ...]] = field(
        default_factory=lambda: {
            "/api/a2ui/capabilities": ("POST",),
            "/api/provider/probe_report": ("GET",),
            "/api/provider/probe": ("POST",),
            "/api/actions/execute": ("POST",),
            "/api/auth/logout": ("POST",),
        },
        init=False,
        repr=False,
    )

    def dispatch(self, request: ApiRequest) -> ApiResponse:
        self._enforce_method_if_known(request)
        if request.method == "POST" and request.path == "/api/a2ui/capabilities":
            session = self._require_session(request)
            self._require_csrf(request, session)
            self._require_json_content_type(request)
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
            report = sanitize_probe_report(self.probe_service.get_probe_report())
            return ApiResponse(status=200, payload={"ok": True, "report": report})
        if request.method == "POST" and request.path == "/api/provider/probe":
            session = self._require_session(request)
            self._require_csrf(request, session)
            self._require_json_content_type(request)
            # Accept optional JSON body for forward-compatible request shape.
            payload = self._parse_json(request.body) if request.body else {}
            probe_request = parse_provider_probe_request(payload)
            if probe_request.base_url is not None:
                try:
                    PolicyGate(
                        confidentiality_profile=probe_request.confidentiality_profile,
                        llm_base_url=probe_request.base_url,
                    ).enforce_localhost_llm()
                except PermissionError as exc:
                    raise ApiError(status=403, message=str(exc)) from exc
            report = sanitize_probe_report(self.probe_service.run_probe())
            return ApiResponse(status=200, payload={"ok": True, "report": report})
        if request.method == "POST" and request.path == "/api/actions/execute":
            if self.action_gateway is None:
                raise ApiError(status=503, message="Action gateway is not configured")
            session = self._require_session(request)
            self._require_csrf(request, session)
            self._require_json_content_type(request)
            payload = self._parse_json(request.body)
            action = parse_action_ref(payload)
            result = self.action_gateway.execute(session_id=session.session_id, action=action)
            return ApiResponse(status=200, payload={"ok": True, "result": result})
        if request.method == "POST" and request.path == "/api/auth/logout":
            session = self._require_session(request)
            self._require_csrf(request, session)
            self.session_store.clear(session.session_id)
            return ApiResponse(
                status=200,
                payload={"ok": True},
                headers={"Set-Cookie": serialize_cleared_session_cookie(secure=self.secure_cookie)},
            )
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

    def _require_json_content_type(self, request: ApiRequest) -> None:
        content_type = request.headers.get("content-type", "")
        if "application/json" not in content_type:
            raise ApiError(status=415, message="Content-Type must be application/json")

    def _enforce_method_if_known(self, request: ApiRequest) -> None:
        allowed = self._ALLOWED_METHODS_BY_PATH.get(request.path)
        if allowed is None:
            return
        if request.method in allowed:
            return
        raise ApiError(
            status=405,
            message="Method not allowed",
            headers={"Allow": ", ".join(allowed)},
        )
