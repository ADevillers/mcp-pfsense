"""Connectivity and permission check for a configured pfSense API key.

Usage:

    poetry run mcp-pfsense-check
    poetry run mcp-pfsense-check --check-write-denied
"""

from __future__ import annotations

import argparse

import httpx

from mcp_pfsense.client import PfSenseError, ReadOnlyPfSenseClient
from mcp_pfsense.config import get_settings

_PROBES: list[tuple[str, list[str]]] = [
    ("interfaces", ["/interfaces", "/interface"]),
    ("status_interfaces", ["/status/interfaces", "/status/interface", "/interfaces/status"]),
    ("gateways", ["/routing/gateways", "/routing/gateway", "/status/gateways", "/gateways"]),
    ("firewall_rules", ["/firewall/rules", "/firewall/rule"]),
    ("firewall_aliases", ["/firewall/aliases", "/firewall/alias"]),
    (
        "nat_port_forwards",
        [
            "/firewall/nat/port_forwards",
            "/firewall/nat/port_forward",
            "/firewall/nat/rules",
            "/nat/port_forwards",
        ],
    ),
    (
        "nat_outbound",
        ["/firewall/nat/outbound/mappings", "/firewall/nat/outbound", "/nat/outbound"],
    ),
    ("dhcp_servers", ["/services/dhcp_servers", "/services/dhcp_server", "/dhcp/servers"]),
    (
        "dns_host_overrides",
        [
            "/services/dns_resolver/host_overrides",
            "/services/dns_resolver/host_override",
            "/services/unbound/host_overrides",
            "/dns/host_overrides",
        ],
    ),
    (
        "wireguard_tunnels",
        ["/vpn/wireguard/tunnels", "/vpn/wireguard/tunnel", "/status/wireguard/tunnels"],
    ),
    (
        "wireguard_peers",
        ["/vpn/wireguard/peers", "/vpn/wireguard/peer", "/status/wireguard/peers"],
    ),
    ("arp_table", ["/diagnostics/arp_table", "/diagnostics/arp", "/status/arp"]),
]


def _format_ok(data: object) -> str:
    if isinstance(data, list):
        return f"OK ({len(data)} items)"
    if isinstance(data, dict):
        return f"OK (keys={sorted(data.keys())[:8]})"
    return f"OK ({type(data).__name__})"


def _probe(client: ReadOnlyPfSenseClient, label: str, paths: list[str]) -> str:
    try:
        data = client.get_first(paths)
    except PfSenseError as exc:
        code = exc.status_code or "?"
        return f"FAIL HTTP {code}"
    return _format_ok(data)


def check_write_denied(settings) -> int:
    """POST /firewall/rules with a throwaway httpx client (not ReadOnlyPfSenseClient)."""
    print("  Checking write denial (POST /firewall/rules — expect HTTP 4xx)...")
    url = settings.api_base.rstrip("/") + "/firewall/rules"
    try:
        with httpx.Client(
            headers={"X-API-Key": settings.pfsense_api_key},
            verify=settings.pfsense_verify_tls,
            timeout=settings.pfsense_timeout,
        ) as raw:
            response = raw.post(url, json={})
    except httpx.HTTPError as exc:
        print(f"  FAIL: request error: {exc}")
        return 1

    if response.status_code < 400:
        print(f"  FAIL: POST returned HTTP {response.status_code} — API is NOT read-only!")
        return 2
    print(f"  OK: POST /firewall/rules -> HTTP {response.status_code}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check pfSense API connectivity and ACLs")
    parser.add_argument(
        "--check-write-denied",
        action="store_true",
        help="POST /firewall/rules and require an HTTP 4xx (ACL probe; opt-in)",
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    print("mcp-pfsense-check")
    print(f"  URL: {settings.pfsense_url}")

    with ReadOnlyPfSenseClient(settings) as client:
        try:
            info = client.get_first(
                [
                    "/system/version",
                    "/system/info",
                    "/status/system",
                    "/system/status",
                ]
            )
        except PfSenseError as exc:
            print(f"  FAIL system info: {exc}")
            return 1

        if isinstance(info, dict):
            version = info.get("version") or info.get("product_version") or "?"
            product = info.get("product") or info.get("product_name") or "pfSense"
            print(f"  System: {product} version={version}")
            extra = {k: info[k] for k in ("release", "pkg_version", "php_version") if k in info}
            if extra:
                print(f"  Extra: {extra}")
        else:
            print(f"  System: {info}")

        print("  Read probes:")
        for label, paths in _PROBES:
            print(f"    {label}: {_probe(client, label, paths)}")

    if args.check_write_denied:
        code = check_write_denied(settings)
        if code != 0:
            return code

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
