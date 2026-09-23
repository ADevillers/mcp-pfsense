"""Unit tests with mocked pfSense API (no live firewall required)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from mcp_pfsense.client import PfSenseError, ReadOnlyPfSenseClient, redact
from mcp_pfsense.config import Settings
from mcp_pfsense.tools import firewall, system


def make_settings() -> Settings:
    return Settings(
        pfsense_url="https://pfs.test",
        pfsense_api_key="test-key",
        pfsense_verify_tls=True,
        pfsense_timeout=5.0,
    )


def test_redact_masks_wireguard_and_passwords() -> None:
    raw = {
        "descr": "peer",
        "privatekey": "AAA=",
        "presharedkey": "BBB=",
        "password": "x",
        "bcrypt-hash": "$2y$...",
        "publickey": "visible",
        "nested": {"secret": "s", "ok": 1},
    }
    cleaned = redact(raw)
    assert cleaned["privatekey"] == "***REDACTED***"
    assert cleaned["presharedkey"] == "***REDACTED***"
    assert cleaned["password"] == "***REDACTED***"
    assert cleaned["bcrypt-hash"] == "***REDACTED***"
    assert cleaned["publickey"] == "visible"
    assert cleaned["nested"]["secret"] == "***REDACTED***"
    assert cleaned["nested"]["ok"] == 1


@respx.mock
def test_get_unwraps_data_and_sends_api_key() -> None:
    route = respx.get("https://pfs.test/api/v2/system/version").mock(
        return_value=httpx.Response(
            200, json={"code": 200, "status": "ok", "data": {"version": "2.7.2"}}
        )
    )
    with ReadOnlyPfSenseClient(make_settings()) as client:
        data = client.get("/system/version")
    assert data == {"version": "2.7.2"}
    assert route.called
    assert route.calls[0].request.headers["X-API-Key"] == "test-key"


@respx.mock
def test_get_raises_on_http_error() -> None:
    respx.get("https://pfs.test/api/v2/firewall/rules").mock(
        return_value=httpx.Response(403, text="Forbidden")
    )
    with ReadOnlyPfSenseClient(make_settings()) as client:
        with pytest.raises(PfSenseError) as exc:
            client.get("/firewall/rules")
    assert exc.value.status_code == 403


@respx.mock
def test_get_first_falls_back_and_tools_work() -> None:
    respx.get("https://pfs.test/api/v2/system/version").mock(
        return_value=httpx.Response(404, text="missing")
    )
    respx.get("https://pfs.test/api/v2/system/info").mock(
        return_value=httpx.Response(
            200, json={"data": {"product": "pfSense", "version": "2.7.2-RELEASE"}}
        )
    )
    respx.get("https://pfs.test/api/v2/firewall/rules").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": 0,
                        "type": "pass",
                        "interface": "wan",
                        "protocol": "tcp",
                        "descr": "HTTPS",
                        "extra": "drop-me-if-slim",
                    }
                ]
            },
        )
    )

    with ReadOnlyPfSenseClient(make_settings()) as client:
        info = json.loads(system.get_system_info(client))
        rules = json.loads(firewall.list_firewall_rules(client, interface="wan"))

    assert info["version"] == "2.7.2-RELEASE"
    assert len(rules) == 1
    assert rules[0]["descr"] == "HTTPS"
    assert "extra" not in rules[0]
