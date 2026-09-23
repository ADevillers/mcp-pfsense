"""Firewall rules and aliases."""

from __future__ import annotations

from typing import Any

from mcp_pfsense.client import ReadOnlyPfSenseClient
from mcp_pfsense.tools._util import dumps, slim_list

_RULE_KEYS = [
    "id",
    "tracker",
    "type",
    "interface",
    "ipprotocol",
    "protocol",
    "source",
    "destination",
    "src",
    "dst",
    "srcport",
    "dstport",
    "descr",
    "disabled",
    "log",
    "gateway",
    "sched",
    "floating",
    "direction",
    "quick",
]


def list_firewall_rules(
    client: ReadOnlyPfSenseClient,
    interface: str | None = None,
) -> str:
    params: dict[str, Any] | None = None
    if interface:
        # pfrest filter query style varies; try common forms
        params = {"interface": interface}
    data = client.get_first(["/firewall/rules", "/firewall/rule"], params=params)
    if interface and isinstance(data, list):
        filtered = [
            r
            for r in data
            if isinstance(r, dict) and str(r.get("interface", "")).lower() == interface.lower()
        ]
        # If server ignored the filter param, filter client-side
        if filtered or params:
            data = filtered if filtered else data
    return dumps(slim_list(data, _RULE_KEYS) if isinstance(data, list) else data)


def list_aliases(client: ReadOnlyPfSenseClient) -> str:
    data = client.get_first(["/firewall/aliases", "/firewall/alias"])
    keys = ["id", "name", "type", "address", "descr", "detail", "url", "updatefreq"]
    return dumps(slim_list(data, keys) if isinstance(data, list) else data)
