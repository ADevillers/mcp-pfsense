# Setup pfSense read-only access

Do this once in the pfSense UI. Keep the API key secret.

Use a **generic** local user (`mcp`) so any local MCP client (Cursor, Claude Desktop, Codex, …) can share the same identity.

## 1. Install pfSense-pkg-RESTAPI (pfrest)

Pick the [pfrest release](https://github.com/pfrest/pfSense-pkg-RESTAPI/releases) that matches your pfSense CE version. Use **pfrest ≥ 2.9.0** (fixes [GHSA-8q8g-9f77-8g8g](https://github.com/advisories/GHSA-8q8g-9f77-8g8g)).

Install from Diagnostics → Command Prompt (or SSH as admin) with `pkg-static add` and the release asset URL for your OS version.

After a pfSense system upgrade, unofficial packages are removed. Reinstall the matching `.pkg` for the new version.

## 2. REST API settings

System → REST API → Settings:

| Setting | Value |
|---|---|
| Enable | yes |
| Read only | **yes** (global write block) |
| Authentication methods | **Key** only (disable Basic / JWT if offered) |
| Allowed interfaces | only the interface your client or reverse proxy uses to reach pfSense |
| Login protection | leave enabled |

Save. Do **not** assign HA settings-sync privileges to non-admin users.

## 3. Group `mcp-readonly` (GET-only privileges)

System → User Manager → Groups → Add:

- Name: `mcp-readonly`
- Description: `MCP / automation read-only`
- Assigned Privileges: only the REST API **GET** privileges needed below.

Privilege names look like `RESTAPI - <Area>: <Resource> - GET` (exact labels depend on package version). Assign GET for:

- System: Version / Status (or System Information)
- Interfaces (config)
- Status: Interfaces
- Routing: Gateways (+ Status Gateways if separate)
- Firewall: Rules
- Firewall: Aliases
- Firewall: NAT Port Forwards
- Firewall: NAT Outbound
- Services: DHCP Server (+ static mappings if listed separately)
- Services: DNS Resolver (host overrides)
- VPN: WireGuard tunnels / peers
- Diagnostics: ARP Table

Do **not** assign `WebCfg - All pages`, any POST/PATCH/DELETE RESTAPI privileges, HA sync privileges, or write-capable roles.

## 4. User `mcp`

System → User Manager → Users → Add:

| Field | Value |
|---|---|
| Username | `mcp` |
| Password | long random (unused — key auth only) |
| Group membership | `mcp-readonly` |
| Disabled | no |

Save.

## 5. API key

System → REST API → Keys → Add / Generate for user `mcp`.

Copy the key **once**. Put it in `.env` as `PFSENSE_API_KEY`.

## 6. Reverse proxy (optional)

If you reach pfSense through a reverse proxy, confirm it forwards client headers, including `X-API-Key`. Do not strip custom headers.

## 7. Local `.env` + deps

```bash
cp .env.example .env
# Edit .env — set PFSENSE_URL and PFSENSE_API_KEY
poetry install
```

Requires [Poetry](https://python-poetry.org/) and Python 3.11+.

## 8. Smoke test

With network access to the pfSense API:

```bash
poetry run mcp-pfsense-check
```

Expect system info and OK on read endpoints.

To confirm the API cannot write (optional):

```bash
poetry run mcp-pfsense-check --check-write-denied
```

Expect HTTP 4xx on `POST /firewall/rules`.

### Manual curl

```bash
curl -sS -H "X-API-Key: ${PFSENSE_API_KEY}" \
  "${PFSENSE_URL}/api/v2/system/version"
```

### Manual PowerShell

```powershell
$h = @{ "X-API-Key" = $env:PFSENSE_API_KEY }
Invoke-RestMethod "$env:PFSENSE_URL/api/v2/system/version" -Headers $h
```

## Security model (three locks)

1. Package **Read only** → pfSense rejects non-GET at the API layer.
2. User `mcp` → only GET privileges.
3. MCP client → refuses every HTTP method except GET.

Plus: use **pfrest ≥ 2.9.0** (GHSA-8q8g-9f77-8g8g).
