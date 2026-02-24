from __future__ import annotations

from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from typing import Any
from urllib.parse import urlsplit

from src.qual.ui.a2ui import A2UISessionStore
from src.qual.webconsole.api.actions import ActionGateway, DenyAllPolicyGate, StubActionExecutor
from src.qual.webconsole.api.handlers import ApiError, ApiRequest, ProviderProbeService, WebConsoleApi
from src.qual.webconsole.auth.session import (
    OneTimeTokenStore,
    Session,
    SessionStore,
    serialize_session_cookie,
)


_LOCALHOST_HOSTS = frozenset({"127.0.0.1", "localhost"})


@dataclass(frozen=True)
class LocalhostOnlyConfig:
    host: str = "127.0.0.1"
    port: int = 0
    secure_cookie: bool = False
    max_body_bytes: int = 256_000

    def validate(self) -> None:
        if self.host not in _LOCALHOST_HOSTS:
            raise ValueError("Web console server must bind to localhost only")
        if self.port < 0 or self.port > 65535:
            raise ValueError("port must be between 0 and 65535")
        if self.max_body_bytes <= 0:
            raise ValueError("max_body_bytes must be positive")


WebConsoleServerConfig = LocalhostOnlyConfig


@dataclass
class StaticProbeService:
    """Safe default provider probe service; replace with engine probe integration."""

    report: dict[str, Any] = field(
        default_factory=lambda: {
            "provider": {"base_url": "http://127.0.0.1"},
            "streaming": False,
            "tool_calling": "unsupported",
            "vision": False,
            "roles_available": {},
            "recommended_actions": ["Wire engine probe service"],
            "timestamp": "",
        }
    )

    def get_probe_report(self) -> dict[str, Any]:
        return dict(self.report)

    def run_probe(self) -> dict[str, Any]:
        return dict(self.report)


class _WebConsoleHandler(BaseHTTPRequestHandler):
    server: "_ApiServer"

    def do_GET(self) -> None:  # noqa: N802
        self._handle()

    def do_POST(self) -> None:  # noqa: N802
        self._handle()

    def log_message(self, format: str, *args: Any) -> None:
        # Keep default server silent; caller can attach structured logging later.
        return

    def _handle(self) -> None:
        path = urlsplit(self.path).path
        body = self._read_body()
        headers = {key.lower(): value for key, value in self.headers.items()}
        request = ApiRequest(method=self.command, path=path, headers=headers, body=body)
        try:
            response = self.server.api.dispatch(request)
            self._write_json(response.status, response.payload, response.headers)
        except ApiError as exc:
            self._write_json(exc.status, {"ok": False, "error": exc.message}, exc.headers)
        except Exception:
            self._write_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": "internal_error"})

    def _read_body(self) -> bytes:
        if self.command != "POST":
            return b""
        raw_length = self.headers.get("Content-Length", "0")
        try:
            size = int(raw_length)
        except ValueError:
            raise ApiError(status=400, message="Invalid Content-Length")
        if size < 0 or size > self.server.max_body_bytes:
            raise ApiError(status=413, message="Request body too large")
        return self.rfile.read(size)

    def _write_json(self, status: int, payload: dict[str, Any], headers: dict[str, str] | None = None) -> None:
        raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'")
        if headers:
            for key, value in headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(raw)


class _ApiServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        RequestHandlerClass: type[BaseHTTPRequestHandler],
        *,
        api: WebConsoleApi,
        max_body_bytes: int,
    ) -> None:
        super().__init__(server_address, RequestHandlerClass)
        self.api = api
        self.max_body_bytes = max_body_bytes


@dataclass
class WebConsoleServer:
    config: WebConsoleServerConfig = field(default_factory=WebConsoleServerConfig)
    session_store: SessionStore = field(default_factory=SessionStore)
    token_store: OneTimeTokenStore = field(default_factory=OneTimeTokenStore)
    capability_sessions: A2UISessionStore = field(default_factory=A2UISessionStore)
    probe_service: ProviderProbeService = field(default_factory=StaticProbeService)
    action_gateway: ActionGateway = field(
        default_factory=lambda: ActionGateway(
            sessions=A2UISessionStore(),
            policy_gate=DenyAllPolicyGate(),
            executor=StubActionExecutor(),
        )
    )
    _server: _ApiServer | None = field(default=None, init=False, repr=False)
    _thread: threading.Thread | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.config.validate()
        self.action_gateway.sessions = self.capability_sessions

    def start(self) -> tuple[str, int]:
        if self._server is not None:
            raise RuntimeError("server already started")
        api = WebConsoleApi(
            session_store=self.session_store,
            capability_sessions=self.capability_sessions,
            probe_service=self.probe_service,
            action_gateway=self.action_gateway,
            secure_cookie=self.config.secure_cookie,
        )
        self._server = _ApiServer(
            (self.config.host, self.config.port),
            _WebConsoleHandler,
            api=api,
            max_body_bytes=self.config.max_body_bytes,
        )
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True, name="webconsole-http")
        self._thread.start()
        host, port = self._server.server_address
        return str(host), int(port)

    def stop(self) -> None:
        server = self._server
        if server is None:
            return
        server.shutdown()
        server.server_close()
        self._server = None
        thread = self._thread
        if thread is not None:
            thread.join(timeout=1.0)
        self._thread = None

    def issue_one_time_token(self, *, purpose: str = "open_console", ttl_seconds: int = 60) -> str:
        return self.token_store.issue(purpose=purpose, ttl_seconds=ttl_seconds)

    def consume_one_time_token(self, token: str, *, purpose: str = "open_console") -> Session:
        if not self.token_store.consume(token, purpose=purpose):
            raise PermissionError("invalid or expired token")
        return self.session_store.create()

    def session_cookie_header(self, session: Session) -> str:
        return serialize_session_cookie(session, secure=self.config.secure_cookie)

    @property
    def server_address(self) -> tuple[str, int] | None:
        if self._server is None:
            return None
        host, port = self._server.server_address
        return str(host), int(port)

    def __enter__(self) -> "WebConsoleServer":
        self.start()
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: Any) -> None:
        self.stop()


def create_server(config: WebConsoleServerConfig | None = None) -> WebConsoleServer:
    if config is None:
        return WebConsoleServer()
    return WebConsoleServer(config=config)
