"""System / status tools."""

from __future__ import annotations

from mcp_pfsense.client import ReadOnlyPfSenseClient
from mcp_pfsense.tools._util import dumps


def get_system_info(client: ReadOnlyPfSenseClient) -> str:
    data = client.get_first(
        [
            "/system/version",
            "/system/info",
            "/status/system",
            "/system/status",
        ]
    )
    return dumps(data)
