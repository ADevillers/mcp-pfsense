"""DHCP tools."""

from __future__ import annotations

from mcp_pfsense.client import ReadOnlyPfSenseClient
from mcp_pfsense.tools._util import dumps


def list_dhcp_servers(client: ReadOnlyPfSenseClient) -> str:
    data = client.get_first(
        [
            "/services/dhcp_servers",
            "/services/dhcp_server",
            "/dhcp/servers",
        ]
    )
    return dumps(data)


def list_dhcp_static_mappings(client: ReadOnlyPfSenseClient) -> str:
    data = client.get_first(
        [
            "/services/dhcp_server/static_mappings",
            "/services/dhcp_servers/static_mappings",
            "/services/dhcp_static_mappings",
            "/dhcp/static_mappings",
        ]
    )
    return dumps(data)
