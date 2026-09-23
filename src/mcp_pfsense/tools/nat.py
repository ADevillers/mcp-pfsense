"""NAT tools."""

from __future__ import annotations

from mcp_pfsense.client import ReadOnlyPfSenseClient
from mcp_pfsense.tools._util import dumps, slim_list

_PF_KEYS = [
    "id",
    "interface",
    "protocol",
    "source",
    "sourceport",
    "destination",
    "destinationport",
    "target",
    "local-port",
    "descr",
    "disabled",
    "natreflection",
]


def list_nat_port_forwards(client: ReadOnlyPfSenseClient) -> str:
    data = client.get_first(
        [
            "/firewall/nat/port_forwards",
            "/firewall/nat/port_forward",
            "/firewall/nat/rules",
            "/nat/port_forwards",
        ]
    )
    return dumps(slim_list(data, _PF_KEYS) if isinstance(data, list) else data)


def list_outbound_nat(client: ReadOnlyPfSenseClient) -> str:
    data = client.get_first(
        [
            "/firewall/nat/outbound/mappings",
            "/firewall/nat/outbound",
            "/nat/outbound",
        ]
    )
    return dumps(data)
