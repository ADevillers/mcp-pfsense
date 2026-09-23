"""Interface tools."""

from __future__ import annotations

from mcp_pfsense.client import ReadOnlyPfSenseClient
from mcp_pfsense.tools._util import dumps, slim_list

_IFACE_KEYS = [
    "id",
    "if",
    "descr",
    "enable",
    "ipaddr",
    "subnet",
    "gateway",
    "ipaddrv6",
    "subnetv6",
    "media",
    "type",
    "alias-address",
    "alias-subnet",
]


def list_interfaces(client: ReadOnlyPfSenseClient) -> str:
    data = client.get_first(["/interfaces", "/interface"])
    return dumps(slim_list(data, _IFACE_KEYS) if isinstance(data, list) else data)


def get_interface_status(client: ReadOnlyPfSenseClient) -> str:
    data = client.get_first(
        [
            "/status/interfaces",
            "/status/interface",
            "/interfaces/status",
        ]
    )
    return dumps(data)


def list_gateways(client: ReadOnlyPfSenseClient) -> str:
    data = client.get_first(
        [
            "/routing/gateways",
            "/routing/gateway",
            "/status/gateways",
            "/gateways",
        ]
    )
    return dumps(data)
