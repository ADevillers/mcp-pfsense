# mcp-pfsense

Read-only [MCP](https://modelcontextprotocol.io/) server for the
[pfSense REST API](https://pfrest.org/) (community package `pfSense-pkg-RESTAPI`).

**No write tools** in v0. Designed for local MCP clients against a pfSense box reached over a private network (VPN / reverse proxy recommended).

## Features

- API key auth (`X-API-Key`)
- HTTP client that only issues `GET`
- Aggressive secret redaction (WireGuard keys, passwords, bcrypt hashes…)
- Tools: system, interfaces, gateways, firewall, aliases, NAT, DHCP, DNS, WireGuard, ARP

## Requirements

- Python 3.11+
- [Poetry](https://python-poetry.org/)
- pfSense CE with `pfSense-pkg-RESTAPI` ≥ v2.9.0 installed (see [SETUP.md](SETUP.md))
- Network path to the webGUI API (VPN + private reverse proxy recommended)

## Setup

```bash
cp .env.example .env   # set PFSENSE_URL, PFSENSE_API_KEY
poetry install
```

See [SETUP.md](SETUP.md) for creating user `mcp` and a read-only API key.

## Run (stdio)

```bash
poetry run mcp-pfsense
```

### MCP client config

Point your client at the in-project Poetry venv (after `poetry install` with `virtualenvs.in-project = true`):

```json
{
  "mcpServers": {
    "pfsense": {
      "command": "/absolute/path/to/mcp-pfsense/.venv/bin/python",
      "args": ["-m", "mcp_pfsense"],
      "envFile": "/absolute/path/to/mcp-pfsense/.env"
    }
  }
}
```

On Windows, use `.venv\\Scripts\\python.exe` instead of `.venv/bin/python`.

Works the same way for Cursor, Claude Desktop, Codex, or any stdio MCP client.

### Inspector

```bash
npx @modelcontextprotocol/inspector poetry run mcp-pfsense
```

## Connectivity check

```bash
poetry run mcp-pfsense-check
poetry run mcp-pfsense-check --check-write-denied   # optional ACL probe
```

## Tests

```bash
poetry run pytest
poetry run ruff check .
poetry run ruff format --check .
```

## Env vars

| Variable | Description |
|---|---|
| `PFSENSE_URL` | Base URL, no trailing slash (required) |
| `PFSENSE_API_KEY` | API key (required) |
| `PFSENSE_VERIFY_TLS` | `true` / `false` |
| `PFSENSE_TIMEOUT` | Seconds |

## Security model

- The HTTP wrapper exposes only `GET`; non-GET methods are not available on the client.
- Responses are recursively redacted for known secret keys (WireGuard private/preshared keys, passwords, bcrypt hashes, …).
- Prefer three locks: package **Read only**, a GET-only user, and this GET-only client.
- Do not expose the pfSense webGUI on the WAN; reach it over VPN or a private reverse proxy.

## License

MIT
