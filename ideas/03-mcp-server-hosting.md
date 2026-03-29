# MCP Server Hosting

**TEMPO Score: 23/25** (T:5 E:5 M:5 P:4 O:4)

## The Signal
19,400+ MCP servers on glama.ai. Explosive ecosystem, but infrastructure layer barely exists. Everyone builds MCP servers locally, nobody has a good way to deploy and host them.

## The Gap
- No "Vercel for MCP servers" exists
- OpenTools.com: API-only, beta stage
- Composio: only their own platform
- Railway/Fly: generic hosting, not MCP-aware
- stdio→HTTP conversion is manual and painful

## The Product
One-click deploy for MCP servers. `mcp deploy ./server` → live URL with auth, analytics, and marketplace listing.

### V1 Features
- CLI: `mcp deploy` from any MCP server directory
- Auto stdio→HTTP bridge (SSE transport)
- Built-in OAuth2 authentication
- Usage analytics dashboard
- Marketplace listing (discover and connect)
- Custom domains on paid plans

## The Buyer
- MCP server authors wanting distribution
- Companies consuming MCP servers (need reliability + auth)
- Agent platform builders needing hosted MCP infra

## Pricing
| Tier | Price |
|------|-------|
| Free | 1 server, 100 req/day |
| Pro | $29/mo, 10 servers, unlimited requests |
| Team | $99/mo, unlimited servers, custom domains |
| Enterprise | $499/mo, SLA, private marketplace |
