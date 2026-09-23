"""DNS Resolver tools."""

from __future__ import annotations

from mcp_pfsense.client import ReadOnlyPfSenseClient
from mcp_pfsense.tools._util import dumps, slim_list


def list_dns_host_overrides(client: ReadOnlyPfSenseClient) -> str:
    data = client.get_first(
        [
            "/services/dns_resolver/host_overrides",
            "/services/dns_resolver/host_override",
            "/services/unbound/host_overrides",
            "/dns/host_overrides",
        ]
    )
    keys = ["id", "host", "domain", "ip", "descr", "aliases"]
    return dumps(slim_list(data, keys) if isinstance(data, list) else data)
