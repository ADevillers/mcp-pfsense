# mcp-pfsense

Read-only [MCP](https://modelcontextprotocol.io/) server for the
[pfSense REST API](https://pfrest.org/) (community package `pfSense-pkg-RESTAPI`).

**Scope is intentional and finished:** GET-only tools, aggressive secret redaction, least-privilege API key. There is no roadmap to add write/mutate operations. If you need an agent that changes firewall rules, VPN, DHCP, or DNS, use a different project (see [Alternatives](#alternatives)).

Designed for local MCP clients against a pfSense box reached over a private network (VPN / reverse proxy recommended).

## When to use this

- You want structured, current pfSense state in an MCP client (Cursor, Claude Desktop, Codex, …).
- You want a hard read-only boundary (HTTP client cannot issue non-GET; no write tools registered).
- You accept a small fixed tool catalog instead of hundreds of mutate endpoints.

**When not to:** if your agent already has a shell and you can call pfrest with env-backed wrappers / `curl`, that is often simpler and more flexible than maintaining an MCP server. Prefer that when the goal is personal automation, not a shared MCP tool surface.

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

## Alternatives

- **Shell + API (often better for personal use):** env file + GET-only `curl` / small wrappers. More flexible path coverage; no MCP process to maintain. Secrets stay in the environment instead of a separate MCP config if you already work that way.
- **Write / manage pfSense:** [gensecaihq/pfsense-mcp-server](https://github.com/gensecaihq/pfsense-mcp-server) — broad pfrest MCP surface with mutate tools and safety guardrails. Prefer that (or pfrest directly) if you need changes, not just inventory.

This repo stays read-only on purpose.

## License

MIT
