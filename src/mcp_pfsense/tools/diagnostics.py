"""Diagnostics tools."""

from __future__ import annotations

from mcp_pfsense.client import ReadOnlyPfSenseClient
from mcp_pfsense.tools._util import dumps


def get_arp_table(client: ReadOnlyPfSenseClient) -> str:
    data = client.get_first(
        [
            "/diagnostics/arp_table",
            "/diagnostics/arp",
            "/status/arp",
        ]
    )
    return dumps(data)
