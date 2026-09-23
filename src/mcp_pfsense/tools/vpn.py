"""WireGuard VPN tools."""

from __future__ import annotations

from mcp_pfsense.client import ReadOnlyPfSenseClient
from mcp_pfsense.tools._util import dumps, slim_list


def list_wireguard_tunnels(client: ReadOnlyPfSenseClient) -> str:
    data = client.get_first(
        [
            "/vpn/wireguard/tunnels",
            "/vpn/wireguard/tunnel",
            "/status/wireguard/tunnels",
        ]
    )
    keys = [
        "id",
        "name",
        "enabled",
        "descr",
        "listenport",
        "addresses",
        "publickey",
        "mtu",
    ]
    return dumps(slim_list(data, keys) if isinstance(data, list) else data)


def list_wireguard_peers(client: ReadOnlyPfSenseClient) -> str:
    data = client.get_first(
        [
            "/vpn/wireguard/peers",
            "/vpn/wireguard/peer",
            "/status/wireguard/peers",
        ]
    )
    keys = [
        "id",
        "enabled",
        "tun",
        "descr",
        "endpoint",
        "port",
        "persistentkeepalive",
        "publickey",
        "allowedips",
        "peerawg",
    ]
    return dumps(slim_list(data, keys) if isinstance(data, list) else data)
