# Internet-Exposed MCP Servers: Research Notes

Source starting point: Knostic, ["How to Find an MCP Server with Shodan"](https://www.knostic.ai/blog/find-mcp-server-shodan),
their [MCP-Scanner](https://github.com/knostic/MCP-Scanner) tool, and their related study
["Exposing the Unseen: Mapping MCP Servers Across the Internet"](https://www.knostic.ai/blog/mapping-mcp-servers-study).
Cross-referenced with independent research from Trend Micro, arXiv, and Practical DevSecOps.

## 1. Why MCP servers end up exposed

MCP (Model Context Protocol) servers bridge LLM clients (agents, IDEs, chat apps) to tools,
files, databases, and internal APIs. Many implementations:

- Default to binding on `0.0.0.0` on common dev ports (3000, 5000, 8000, 8080), so a container
  or cloud VM with an open security group is internet-reachable from first deploy.
- Predate the November 2025 MCP spec revision that made **OAuth 2.1 mandatory** for remote
  servers — a huge installed base still ships with no auth at all, or auth that's disabled by
  default "for local dev" and never re-enabled in prod.
- Are stood up quickly (FastMCP, `mcp-framework`, hand-rolled FastAPI/uvicorn wrappers) by teams
  optimizing for "get the agent working," not for external exposure review.

## 2. How researchers find them (Shodan methodology)

MCP has recognizable fingerprints at the protocol and transport layer, which is what makes it
Shodan-searchable at scale. Knostic's scanner ships 100+ filter strings; the categories are:

| Category | Example filters |
|---|---|
| Literal protocol name | `"Model Context Protocol"`, `MCP server`, `mcp-server`, `MCPServer` |
| Transport (SSE) | `text/event-stream`, `Server-Sent Events`, `event-stream` |
| JSON-RPC markers | `"jsonrpc": "2.0"`, `"method": "initialize"`, `"method": "tools/list"`, `"method": "tools/call"` |
| Protocol version banner | `"protocolVersion": "2024-11-05"` |
| Known endpoint paths | `GET /mcp`, `POST /mcp`, `GET /sse`, `POST /messages`, `/mcp/sse`, `/api/mcp`, `/v1/mcp` |
| Handshake fields | `clientInfo`, `serverInfo`, `capabilities tools resources` |
| Framework fingerprints | `FastMCP`, `fastmcp`, `uvicorn mcp`, `mcp-framework`, `python-mcp`, `anthropic/mcp` |
| Port + protocol combo | `port:3000-8080` AND (`jsonrpc` OR `text/event-stream`) |
| PaaS/edge hosting | `cloudflare mcp`, `workers.dev mcp`, `vercel mcp`, `heroku mcp`, `railway mcp` |
| MCP method names | `tools/list`, `tools/call`, `resources/list`, `resources/read`, `prompts/list` |

Workflow: run the filters via the Shodan API (concurrent calls, one worker per query string) →
dedupe by `IP:port` → for each candidate, send a real MCP `initialize` request over HTTP and SSE
transports to confirm protocol compliance (not just a banner match) → if confirmed, attempt
unauthenticated `tools/list` / `resources/list` to see what's exposed.

## 3. Scale and findings across the research

- Knostic's initial pass found **1,800–1,862** MCP servers exposed with no authentication;
  of 119 manually sampled, **100% (119/119)** allowed unauthenticated listing of internal
  tools.
- Follow-on tracking (cited via Medium/aggregator coverage) put the count at **8,000+**
  internet-visible MCP servers by early 2026, with a separate scan reporting **21,000+**
  detectable instances and another reporting growth to **1,467 → ~3x** in a short window —
  the exact numbers vary by methodology/date, but the trend is consistent: fast, uncontrolled
  growth.
- An academic dynamic-assessment paper ("Exposed by Design", arXiv 2608.00150) found
  **91.8%** of dynamically audited internet-facing servers lack OAuth, and reported 68
  concrete reportable vulnerabilities across the sample: SQL injection, SSRF against cloud
  metadata endpoints (`169.254.169.254`), prompt/template injection, and path traversal via
  cursor/pagination parameter manipulation.
- Trend Micro's follow-up noted the exposure surface widening into cloud-hosted/managed MCP
  deployments, not just self-hosted dev boxes.
- What an unauthenticated `tools/list`/`resources/list` typically leaks: full tool schemas
  (which often reveal internal API shapes and credentials-adjacent parameters), agent
  conversation history, and — when tools are actually invoked — direct read access to files,
  database tables, and internal service APIs the MCP server was configured to reach.
  Environment-variable leakage (API keys, DB credentials, internal tokens) via debug/log tools
  is a recurring theme.

## 4. Attacker path

1. Discover via Shodan/port scan using the fingerprints above (no auth needed to find them).
2. Connect as a normal MCP client — no exploit required if auth is absent.
3. Call `tools/list` / `resources/list` to enumerate capabilities.
4. Invoke tools directly: read files, query DBs, call internal APIs, or pivot via SSRF if a
   tool proxies outbound requests (cloud metadata theft is the most damaging observed
   pattern).

## 5. Mitigations (what "good" looks like)

- **Auth is not optional**: implement OAuth 2.1 (with PKCE) per the current MCP spec; treat
  the MCP server as an OAuth *resource server* validating tokens from a real IdP (Entra ID,
  Auth0, Okta, GitHub OAuth) rather than rolling custom auth.
- **Never bind to `0.0.0.0` in prod** without a gateway in front of it. Default to loopback or
  a private interface; put a reverse proxy/API gateway in front for TLS, auth, and rate
  limiting if it must be reachable from other hosts.
- **Network segmentation**: place MCP servers in private subnets/VLANs with no direct inbound
  internet path; allowlist only the specific callers and egress destinations the server
  actually needs (this also limits SSRF blast radius — block outbound access to
  `169.254.169.254` and other metadata endpoints unless explicitly required).
- **Least privilege for tools**: scope each tool's backing credentials to only what that tool
  needs; don't hand an MCP server a service account with broad DB/API access "to be safe."
  Validate/sanitize all tool parameters server-side (the path-traversal-via-cursor and SQLi
  findings above were both parameter-validation failures).
- **Monitoring**: log and alert on `initialize`, `tools/list`, and `tools/call` requests from
  unexpected source IPs/identities; treat an unauthenticated successful `tools/list` as an
  incident, not background noise.
- **Attack-surface hygiene**: periodically run the same Shodan-style fingerprint queries
  against your own ASN/IP ranges (or use a tool like MCP-Scanner in an authorized,
  self-scanning capacity) as part of external attack surface management, since these servers
  are frequently stood up outside normal change control.

## 6. Sources

- [Knostic — How to Find an MCP Server with Shodan](https://www.knostic.ai/blog/find-mcp-server-shodan)
- [Knostic — Exposing the Unseen: Mapping MCP Servers Across the Internet](https://www.knostic.ai/blog/mapping-mcp-servers-study)
- [Knostic — Automating MCP Server Discovery with Claude Sonnet 4](https://www.knostic.ai/blog/automating-model-context-protocol-discovery)
- [knostic/MCP-Scanner (GitHub)](https://github.com/knostic/MCP-Scanner)
- [Exposed by Design: A Dynamic Security Assessment of Internet-Facing MCP Servers at Scale (arXiv:2608.00150)](https://arxiv.org/html/2608.00150)
- [Trend Micro — Update on Exposed MCP Servers: The Threat Widens to the Cloud](https://www.trendmicro.com/vinfo/us/security/news/vulnerabilities-and-exploits/update-on-exposed-mcp-servers-the-threat-widens-to-the-cloud)
- [Practical DevSecOps — MCP Security Statistics 2026](https://www.practical-devsecops.com/mcp-security-statistics-2026-report/)
- [Anvilogic — MCP Servers Found Exposed Without Access Controls](https://www.anvilogic.com/threat-reports/mcp-server-auth-flaws)
- [Doppler — Exposed remote MCP servers](https://www.doppler.com/guides/mcp-server-security-risks-attack-scenarios/exposed-remote-mcp-servers)
