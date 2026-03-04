from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from http.cookies import SimpleCookie
import secrets

COOKIE_NAME = "exegesis_console_session"
CSRF_HEADER_NAME = "x-csrf-token"


@dataclass(frozen=True)
class Session:
    session_id: str
    csrf_token: str
    expires_at: datetime

    def is_expired(self, *, now: datetime | None = None) -> bool:
        current = now or datetime.now(UTC)
        return current >= self.expires_at


@dataclass(frozen=True)
class _OneTimeToken:
    token: str
    purpose: str
    expires_at: datetime

    def is_expired(self, *, now: datetime | None = None) -> bool:
        current = now or datetime.now(UTC)
        return current >= self.expires_at


class OneTimeTokenStore:
    """Single-use token store for localhost console bootstrapping."""

    def __init__(self) -> None:
        self._tokens: dict[str, _OneTimeToken] = {}

    def issue(self, *, purpose: str, ttl_seconds: int = 60) -> str:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        token = secrets.token_urlsafe(24)
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
        self._tokens[token] = _OneTimeToken(token=token, purpose=purpose, expires_at=expires_at)
        return token

    def consume(self, token: str, *, purpose: str) -> bool:
        entry = self._tokens.pop(token, None)
        if entry is None:
            return False
        if entry.purpose != purpose:
            return False
        return not entry.is_expired()


class SessionStore:
    """In-memory session store with short-lived, HttpOnly cookie sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create(self, *, ttl_seconds: int = 1800) -> Session:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        session = Session(
            session_id=secrets.token_urlsafe(24),
            csrf_token=secrets.token_urlsafe(18),
            expires_at=datetime.now(UTC) + timedelta(seconds=ttl_seconds),
        )
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> Session | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        if session.is_expired():
            self._sessions.pop(session_id, None)
            return None
        return session

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


def parse_cookie_session_id(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None
    cookie = SimpleCookie()
    cookie.load(cookie_header)
    morsel = cookie.get(COOKIE_NAME)
    if morsel is None:
        return None
    return morsel.value


def serialize_session_cookie(session: Session, *, secure: bool = False) -> str:
    cookie = SimpleCookie()
    cookie[COOKIE_NAME] = session.session_id
    cookie[COOKIE_NAME]["path"] = "/"
    cookie[COOKIE_NAME]["httponly"] = True
    cookie[COOKIE_NAME]["samesite"] = "Strict"
    cookie[COOKIE_NAME]["max-age"] = str(max(0, int((session.expires_at - datetime.now(UTC)).total_seconds())))
    if secure:
        cookie[COOKIE_NAME]["secure"] = True
    return cookie.output(header="", sep="").strip()
