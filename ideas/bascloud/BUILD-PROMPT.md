# BasCloud — MCP Server Hosting Platform

> Paste this into Claude Code to generate planning docs and build the product.
> Then run: `python3 .buildrunner/run.py unattended`

---

## Product Vision

BasCloud is "Vercel for MCP servers." One-click deploy from any MCP server directory. `mcp deploy ./server` → live URL with auth, analytics, and marketplace listing.

**Tagline:** "Deploy your MCP server in 30 seconds."

## Tech Stack
Next.js 15, TypeScript, Tailwind v4, Supabase, Vercel, Stripe, Docker (for server isolation)

## 14 Sprints / 7 Stages

### Stage 0 (Sprint 0): Validation
- Talk to 8 MCP server authors. Ask: how do you deploy? What's painful?

### Stage 1 (Sprints 1-2): Foundation
- Sprint 1: Next.js scaffold, Supabase auth, servers table, dashboard shell
- Sprint 2: CLI tool (`bascloud deploy`) — reads MCP config, packages server, uploads to platform

### Stage 2 (Sprints 3-4): Core Deploy
- Sprint 3: Server runtime — Docker container per MCP server, stdio→HTTP/SSE bridge, health checks
- Sprint 4: Auto-scaling + cold starts — scale to zero when idle, spin up on first request, connection pooling

### Stage 3 (Sprints 5-6): Auth & Security
- Sprint 5: OAuth2 gateway — API key auth for MCP clients, scoped permissions per tool, rate limiting
- Sprint 6: Secret management — encrypted env vars, server-side secrets injection, audit log

### Stage 4 (Sprints 7-9): Dashboard & Analytics
- Sprint 7: Server dashboard — deploy history, logs viewer, restart/rollback controls
- Sprint 8: Analytics — requests/day, latency p50/p95/p99, error rates, top tools used
- Sprint 9: Marketplace — server listing, search, categories, README rendering, one-click connect

### Stage 5 (Sprints 10-12): Revenue
- Sprint 10: Custom domains, SSL auto-provisioning, server versioning
- Sprint 11: Stripe billing — free/pro/team/enterprise, usage-based pricing for compute
- Sprint 12: API + webhooks — deploy API, webhook events for deploy success/failure, status checks

### Stage 6 (Sprints 13-14): Scale
- Sprint 13: Multi-region deployment, server templates (clone from marketplace), team access controls
- Sprint 14: Landing page, docs, CLI docs, pricing page, onboarding flow

## Key Contract Types

```typescript
export interface McpServer {
  id: string;
  org_id: string;
  name: string;
  slug: string;
  description: string | null;
  transport: 'stdio' | 'sse' | 'http';
  status: 'deploying' | 'running' | 'stopped' | 'error';
  url: string;
  custom_domain: string | null;
  version: string;
  tools: McpTool[];
  created_at: string;
  updated_at: string;
}

export interface McpTool {
  name: string;
  description: string;
  input_schema: Record<string, unknown>;
}

export interface Deployment {
  id: string;
  server_id: string;
  version: string;
  status: 'building' | 'deploying' | 'live' | 'failed' | 'rolled_back';
  build_log: string | null;
  duration_ms: number | null;
  created_at: string;
}

export interface ServerAnalytics {
  requests_24h: number;
  latency_p50_ms: number;
  latency_p99_ms: number;
  error_rate_pct: number;
  top_tools: Array<{ name: string; calls: number }>;
}
```

## Design Direction
- **Clean, developer-focused** — like Vercel's dashboard
- **Primary:** #000000 (black), **Accent:** #0070F3 (Vercel blue)
- **Font:** Geist Sans + Geist Mono
- **Key component:** Deploy card with status indicator, URL, last deploy time, live metrics sparkline

## Golden Jobs

### Job A — Deploy a Simple MCP Server
> "I built an MCP server that searches my company's docs. Deploy it so my whole team can connect from Claude Code."

### Job B — Add Auth to Existing Server
> "My MCP server is public right now. Add API key auth so only my team can use it."

### Job C — Monitor Server Health
> "My MCP server sometimes hangs. Show me latency and error rate. Alert me if p99 > 5s."

### Job D — Marketplace Discovery
> "I want to find an MCP server that does Jira integration. Search the marketplace, connect it to my Claude Code."
