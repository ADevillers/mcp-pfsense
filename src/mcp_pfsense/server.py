"""Read-only MCP server for pfSense REST API (pfrest)."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import TypeVar

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from mcp_pfsense.client import ReadOnlyPfSenseClient
from mcp_pfsense.tools import dhcp, diagnostics, dns, firewall, interfaces, nat, system, vpn

_READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False)

mcp = MCPServer(
    "pfsense",
    version="0.1.0",
    instructions=(
        "Read-only pfSense REST API (pfrest). Never attempt write/mutate operations. "
        "Reach the API over a private network path; do not expose the webGUI on the WAN."
    ),
)

T = TypeVar("T")


def _client() -> ReadOnlyPfSenseClient:
    return ReadOnlyPfSenseClient()


async def _run(fn: Callable[[], T]) -> T:
    return await asyncio.to_thread(fn)


@mcp.tool(annotations=_READ_ONLY)
async def get_system_info() -> str:
    """Get pfSense system / version information."""

    def _call() -> str:
        with _client() as client:
            return system.get_system_info(client)

    return await _run(_call)


@mcp.tool(annotations=_READ_ONLY)
async def list_interfaces() -> str:
    """List configured interfaces (WAN, LAN, OPTx…)."""

    def _call() -> str:
        with _client() as client:
            return interfaces.list_interfaces(client)

    return await _run(_call)


@mcp.tool(annotations=_READ_ONLY)
async def get_interface_status() -> str:
    """Get runtime interface status (link, IPs, traffic counters when available)."""

    def _call() -> str:
        with _client() as client:
            return interfaces.get_interface_status(client)

    return await _run(_call)


@mcp.tool(annotations=_READ_ONLY)
async def list_gateways() -> str:
    """List routing gateways (and status when available)."""

    def _call() -> str:
        with _client() as client:
            return interfaces.list_gateways(client)

    return await _run(_call)


@mcp.tool(annotations=_READ_ONLY)
async def list_firewall_rules(interface: str | None = None) -> str:
    """List firewall rules. Optionally filter by interface name (wan, lan, opt…)."""

    def _call() -> str:
        with _client() as client:
            return firewall.list_firewall_rules(client, interface=interface)

    return await _run(_call)


@mcp.tool(annotations=_READ_ONLY)
async def list_aliases() -> str:
    """List firewall aliases (hosts, networks, ports, URLs…)."""

    def _call() -> str:
        with _client() as client:
            return firewall.list_aliases(client)

    return await _run(_call)


@mcp.tool(annotations=_READ_ONLY)
async def list_nat_port_forwards() -> str:
    """List NAT port forwards."""

    def _call() -> str:
        with _client() as client:
            return nat.list_nat_port_forwards(client)

    return await _run(_call)


@mcp.tool(annotations=_READ_ONLY)
async def list_outbound_nat() -> str:
    """List outbound NAT mode / mappings."""

    def _call() -> str:
        with _client() as client:
            return nat.list_outbound_nat(client)

    return await _run(_call)


@mcp.tool(annotations=_READ_ONLY)
async def list_dhcp_servers() -> str:
    """List DHCP server configs (ranges, DNS, gateways per interface)."""

    def _call() -> str:
        with _client() as client:
            return dhcp.list_dhcp_servers(client)

    return await _run(_call)


@mcp.tool(annotations=_READ_ONLY)
async def list_dhcp_static_mappings() -> str:
    """List DHCP static mappings (MAC → IP reservations)."""

    def _call() -> str:
        with _client() as client:
            return dhcp.list_dhcp_static_mappings(client)

    return await _run(_call)


@mcp.tool(annotations=_READ_ONLY)
async def list_dns_host_overrides() -> str:
    """List DNS Resolver host overrides."""

    def _call() -> str:
        with _client() as client:
            return dns.list_dns_host_overrides(client)

    return await _run(_call)


@mcp.tool(annotations=_READ_ONLY)
async def list_wireguard_tunnels() -> str:
    """List WireGuard tunnels (private keys redacted)."""

    def _call() -> str:
        with _client() as client:
            return vpn.list_wireguard_tunnels(client)

    return await _run(_call)


@mcp.tool(annotations=_READ_ONLY)
async def list_wireguard_peers() -> str:
    """List WireGuard peers (preshared keys redacted)."""

    def _call() -> str:
        with _client() as client:
            return vpn.list_wireguard_peers(client)

    return await _run(_call)


@mcp.tool(annotations=_READ_ONLY)
async def get_arp_table() -> str:
    """Get the ARP table."""

    def _call() -> str:
        with _client() as client:
            return diagnostics.get_arp_table(client)

    return await _run(_call)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
