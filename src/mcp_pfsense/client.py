"""HTTP client that only allows GET against the pfSense REST API."""

from __future__ import annotations

from typing import Any

import httpx

from mcp_pfsense.config import Settings, get_settings

_SECRET_KEYS = frozenset(
    {
        "privatekey",
        "presharedkey",
        "pre-shared-key",
        "password",
        "bcrypt-hash",
        "bcrypt_hash",
        "prv",
        "secret",
        "key",
        "apikey",
        "api_key",
        "authorizedkeys",
        "authorized_keys",
        "token",
        "client_secret",
        "shared_key",
    }
)

_SECRET_SUBSTR = (
    "password",
    "secret",
    "privatekey",
    "preshared",
    "pre-shared",
    "apikey",
    "api_key",
    "bcrypt",
    "authorizedkey",
)


class PfSenseError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ReadOnlyPfSenseClient:
    """Thin httpx wrapper that refuses every non-GET method."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client = httpx.Client(
            base_url=self.settings.api_base,
            headers={"X-API-Key": self.settings.pfsense_api_key},
            verify=self.settings.pfsense_verify_tls,
            timeout=self.settings.pfsense_timeout,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> ReadOnlyPfSenseClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        path = path if path.startswith("/") else f"/{path}"
        try:
            response = self._client.get(path, params=params)
        except httpx.HTTPError as exc:
            raise PfSenseError(f"Request failed: {exc}") from exc

        if response.status_code >= 400:
            detail = response.text[:500]
            raise PfSenseError(
                f"GET {path} -> HTTP {response.status_code}: {detail}",
                status_code=response.status_code,
            )

        payload = response.json()
        if isinstance(payload, dict) and "data" in payload:
            return redact(payload["data"])
        return redact(payload)

    def get_first(
        self,
        paths: list[str],
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Try paths in order; return first successful GET. Raise last error."""
        last: PfSenseError | None = None
        for path in paths:
            try:
                return self.get(path, params=params)
            except PfSenseError as exc:
                last = exc
                if exc.status_code not in (404, 405):
                    # Auth / forbidden / server errors: stop early
                    if exc.status_code in (401, 403):
                        raise
        if last is not None:
            raise last
        raise PfSenseError("No paths provided")


def redact(value: Any) -> Any:
    """Recursively mask known secret fields in API payloads."""
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            lower = key.lower().replace("-", "_")
            if lower in _SECRET_KEYS or any(s in lower for s in _SECRET_SUBSTR):
                out[key] = "***REDACTED***"
            else:
                out[key] = redact(item)
        return out
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value
