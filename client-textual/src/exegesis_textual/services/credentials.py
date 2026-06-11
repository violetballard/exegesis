from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

KEYRING_SERVICE = "exegesis.developer.providers"
MISTRAL_ACCOUNT = "mistral"
CLAUDE_ACCOUNT = "claude"
GOOGLE_ACCOUNT = "google"
OPENAI_ACCOUNT = "openai"
LOCAL_OPENAI_ACCOUNT = "local_openai"
PROVIDER_CREDENTIAL_ACCOUNTS = {
    MISTRAL_ACCOUNT: MISTRAL_ACCOUNT,
    CLAUDE_ACCOUNT: CLAUDE_ACCOUNT,
    GOOGLE_ACCOUNT: GOOGLE_ACCOUNT,
    OPENAI_ACCOUNT: OPENAI_ACCOUNT,
    LOCAL_OPENAI_ACCOUNT: LOCAL_OPENAI_ACCOUNT,
}


class CredentialStoreError(RuntimeError):
    """Raised when secure credential storage cannot be used safely."""


@dataclass(frozen=True)
class CredentialStoreStatus:
    available: bool
    backend_name: str = ""
    error_message: str = ""


class CredentialStore(Protocol):
    def get_secret(self, account: str) -> str: ...

    def set_secret(self, account: str, secret: str) -> None: ...

    def delete_secret(self, account: str) -> None: ...

    def status(self) -> CredentialStoreStatus: ...


class KeyringCredentialStore:
    def __init__(self, service: str = KEYRING_SERVICE) -> None:
        self._service = service

    def get_secret(self, account: str) -> str:
        try:
            secret = self._keyring().get_password(self._service, account)
        except Exception as exc:
            raise CredentialStoreError("Secure credential storage is unavailable or locked.") from exc
        return secret or ""

    def set_secret(self, account: str, secret: str) -> None:
        try:
            self._keyring().set_password(self._service, account, secret)
        except Exception as exc:
            raise CredentialStoreError("Could not save the API key in secure credential storage.") from exc

    def delete_secret(self, account: str) -> None:
        try:
            self._keyring().delete_password(self._service, account)
        except Exception:
            return

    def status(self) -> CredentialStoreStatus:
        try:
            backend = self._keyring().get_keyring()
        except Exception as exc:
            return CredentialStoreStatus(
                available=False,
                error_message="Secure credential storage is unavailable or locked.",
            )
        backend_module = backend.__class__.__module__
        backend_name = f"{backend_module}.{backend.__class__.__name__}"
        if backend_module.endswith(".fail"):
            return CredentialStoreStatus(
                available=False,
                backend_name=backend_name,
                error_message="Python keyring has no secure backend available.",
            )
        return CredentialStoreStatus(available=True, backend_name=backend_name)

    @staticmethod
    def _keyring():
        try:
            import keyring
        except Exception as exc:
            raise CredentialStoreError("Python keyring is not available.") from exc
        return keyring


class InMemoryCredentialStore:
    def __init__(self, initial: dict[str, str] | None = None) -> None:
        self._secrets = dict(initial or {})

    def get_secret(self, account: str) -> str:
        return self._secrets.get(account, "")

    def set_secret(self, account: str, secret: str) -> None:
        self._secrets[account] = secret

    def delete_secret(self, account: str) -> None:
        self._secrets.pop(account, None)

    def status(self) -> CredentialStoreStatus:
        return CredentialStoreStatus(available=True, backend_name="InMemoryCredentialStore")


class UnavailableCredentialStore:
    def __init__(self, message: str = "Secure credential storage is unavailable or locked.") -> None:
        self._message = message

    def get_secret(self, account: str) -> str:
        raise CredentialStoreError(self._message)

    def set_secret(self, account: str, secret: str) -> None:
        raise CredentialStoreError(self._message)

    def delete_secret(self, account: str) -> None:
        raise CredentialStoreError(self._message)

    def status(self) -> CredentialStoreStatus:
        return CredentialStoreStatus(available=False, error_message=self._message)


__all__ = [
    "CredentialStore",
    "CredentialStoreError",
    "CredentialStoreStatus",
    "CLAUDE_ACCOUNT",
    "GOOGLE_ACCOUNT",
    "InMemoryCredentialStore",
    "KEYRING_SERVICE",
    "KeyringCredentialStore",
    "LOCAL_OPENAI_ACCOUNT",
    "MISTRAL_ACCOUNT",
    "OPENAI_ACCOUNT",
    "PROVIDER_CREDENTIAL_ACCOUNTS",
    "UnavailableCredentialStore",
]
