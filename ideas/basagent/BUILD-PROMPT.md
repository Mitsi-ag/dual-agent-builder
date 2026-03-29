# BasAgent — Agent Cost Controller

> Paste this entire prompt into Claude Code to generate the full planning suite and build the product.
> Then run: `python3 .buildrunner/run.py unattended`
>
> **Monitoring (Terminal 2):** `tail -f .buildrunner/logs/codex-live.log .buildrunner/logs/claude-live.log`
> **Health check (Terminal 3):** `python3 .buildrunner/monitor.py` (or CronCreate */5)

---

## Step 1: Generate Planning Docs

Create ALL of these files before any code. Read the Dual-Agent Builder METHOD.md first.

### PRODUCT.md

```markdown
# BasAgent — Agent Cost Controller

## Thesis
Every team running AI agents gets surprise API bills. BasAgent is budget management middleware for AI agents — set limits, track spend in real-time, auto-pause runaway agents. "CloudWatch billing alarms for AI."

## Target User
Engineering leads running 5+ AI agents in production. They've been burned by a $2K overnight API bill from a stuck agent loop.

## Core Features (V1)
1. **MCP Server Proxy** — intercepts Anthropic, OpenAI, Google API calls transparently
2. **Real-time Cost Dashboard** — cost per agent, per task, per team, per hour
3. **Budget Enforcement** — soft limits (alert), hard limits (auto-pause/kill)
4. **Alert System** — Slack/email at 50%, 80%, 100% of budget
5. **Team Management** — invite members, per-team budgets, admin controls
6. **Usage Analytics** — trend charts, top spenders, cost breakdown by model

## Pricing
- Free: 1 agent, 1K tracked calls/mo
- Team ($49/mo): 20 agents, unlimited calls, 5 members, Slack alerts
- Org ($199/mo): Unlimited agents, SSO, audit logs, API access
- Enterprise ($499/mo): Custom SLA, dedicated support, on-prem option

## Kill Signals
- Can't intercept API calls reliably across providers → pivot to log-based
- Users don't care about cost (unlikely — every complaint thread says otherwise)
- Big provider ships native budgets (unlikely — not their incentive)

## Tech Stack
Next.js 15, TypeScript, Tailwind v4, Supabase, Vercel, Stripe, Resend

## Competitive Landscape
| Competitor | What They Do | Our Advantage |
|-----------|-------------|---------------|
| AgentOps | Retrospective observability | We enforce budgets in real-time |
| LangSmith | Trace debugging | We focus on cost, not debugging |
| Helicone | Request logging | We have auto-pause + team budgets |
```

### DECISIONS.md

Create with these initial decisions:

- **D001:** MCP server architecture (proxy pattern) — intercept at the transport layer, not SDK wrapper
- **D002:** Supabase for auth + DB + realtime — proven stack, free tier for dev
- **D003:** Start with Anthropic + OpenAI support only — 90% of the market
- **D004:** Amounts in integer microdollars ($0.001 = 1000) — avoids float rounding in cost calculation
- **D005:** Soft + hard budget limits — soft alerts, hard auto-pauses. User controls which
- **D006:** Freemium, not usage-based — predictable pricing wins trust
- **D007:** Dashboard-first, not CLI-first — buyers are engineering leads, not solo devs
- **D008:** Cost estimation uses provider pricing APIs — auto-updates when pricing changes
- **D009:** Agent identification via API key prefix — each agent gets a unique proxy key
- **D010:** Supabase Realtime for live cost updates — no polling needed

### docs/ARCHITECTURE.md

Include:
- **Database schema:** organizations, teams, agents, api_calls (high-write table), budgets, alerts, users
- **MCP Server:** TypeScript, proxies calls to Anthropic/OpenAI, meters tokens, enforces budgets
- **Cost calculation:** input_tokens * rate + output_tokens * rate, rates fetched from providers
- **Budget enforcement flow:** call arrives → check budget → if under: proxy to provider, log cost → if over soft: proxy + alert → if over hard: reject with 429 + budget_exceeded error
- **Realtime:** Supabase channels push cost updates to dashboard
- **API routes:** 15+ endpoints for agents, budgets, teams, analytics, billing

### docs/DESIGN-GUIDE.md

- **Aesthetic:** Bloomberg terminal meets modern SaaS. Dark mode default. Data-dense but readable.
- **Primary:** #0F172A (slate-900), **Accent:** #22C55E (green-500) for under-budget, #EF4444 (red-500) for over-budget
- **Font:** JetBrains Mono for numbers/costs, Inter for body text
- **Key components:** Cost ticker (live updating), budget gauge (circular progress), spark charts, alert timeline
- **Mobile:** responsive but desktop-first (this is a dashboard product)

### docs/sprints/ (14 sprints, 7 stages)

**Stage 0 (Sprint 0): Validation**
- Talk to 8 engineering leads about agent cost pain
- Find 3 who'd pay $49/mo for budget enforcement

**Stage 1 (Sprints 1-2): Foundation**
- Sprint 1: Next.js scaffold, Supabase auth, organizations table, basic dashboard layout
- Sprint 2: MCP server skeleton, API key generation, proxy stub (echo mode)

**Stage 2 (Sprints 3-4): Core Proxy**
- Sprint 3: Anthropic API proxy — intercept, meter tokens, log to api_calls table
- Sprint 4: OpenAI API proxy — same pattern, plus cost calculation engine

**Stage 3 (Sprints 5-6): Budget Enforcement**
- Sprint 5: Budget CRUD, soft/hard limit logic, 429 rejection for hard limits
- Sprint 6: Alert system — Slack webhook, email (Resend), budget threshold triggers

**Stage 4 (Sprints 7-9): Dashboard**
- Sprint 7: Real-time cost dashboard — live ticker, cost breakdown by agent/model/team
- Sprint 8: Analytics — trend charts (Recharts), top spenders, cost per task, date range picker
- Sprint 9: Team management — invite members, per-team budgets, admin roles

**Stage 5 (Sprints 10-12): Revenue**
- Sprint 10: Agent management — create/edit/delete agents, usage stats per agent
- Sprint 11: Stripe billing — checkout, portal, usage tracking, plan enforcement
- Sprint 12: API + webhooks — REST API for programmatic access, webhook events for budget alerts

**Stage 6 (Sprints 13-14): Scale**
- Sprint 13: Google/Gemini API proxy support, audit log, export (CSV/JSON)
- Sprint 14: Landing page, docs, SEO, pricing page, onboarding wizard

## Step 2: Configure .buildrunner/config.py

```python
PROJECT_NAME = "BasAgent"
PROJECT_DESCRIPTION = "Agent Cost Controller — budget management for AI agents"
TECH_STACK = "Next.js 15 + Supabase + Vercel"

SPRINT_CONTRACTS = {
    1: {
        "types": {
            "Organization": '''export interface Organization {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
  plan: 'free' | 'team' | 'org' | 'enterprise';
  created_at: string;
  updated_at: string;
}''',
        },
        "routes": {
            "auth": {
                "callback": {"method": "POST", "path": "/api/auth/callback", "auth": False},
            },
        },
    },
    2: {
        "types": {
            "Agent": '''export interface Agent {
  id: string;
  org_id: string;
  name: string;
  api_key_prefix: string;
  api_key_hash: string;
  provider: 'anthropic' | 'openai' | 'google';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}''',
            "ProxyConfig": '''export interface ProxyConfig {
  agent_id: string;
  provider: 'anthropic' | 'openai' | 'google';
  target_api_key_encrypted: string;
  budget_id: string | null;
}''',
        },
        "routes": {
            "agents": {
                "list": {"method": "GET", "path": "/api/agents", "auth": True},
                "create": {"method": "POST", "path": "/api/agents", "auth": True},
                "rotateKey": {"method": "POST", "path": "/api/agents/[id]/rotate-key", "auth": True},
            },
        },
    },
    3: {
        "types": {
            "ApiCall": '''export interface ApiCall {
  id: string;
  agent_id: string;
  org_id: string;
  provider: 'anthropic' | 'openai' | 'google';
  model: string;
  input_tokens: number;
  output_tokens: number;
  cost_microdollars: number;
  latency_ms: number;
  status: 'success' | 'error' | 'budget_exceeded';
  created_at: string;
}''',
        },
        "routes": {
            "proxy": {
                "anthropic": {"method": "POST", "path": "/api/proxy/anthropic/v1/messages", "auth": False},
            },
        },
    },
    4: {
        "types": {},
        "routes": {
            "proxy": {
                "openai": {"method": "POST", "path": "/api/proxy/openai/v1/chat/completions", "auth": False},
            },
        },
    },
    5: {
        "types": {
            "Budget": '''export interface Budget {
  id: string;
  org_id: string;
  name: string;
  scope: 'org' | 'team' | 'agent';
  scope_id: string | null;
  limit_microdollars: number;
  period: 'daily' | 'weekly' | 'monthly';
  soft_limit_pct: number;
  hard_limit_pct: number;
  current_spend_microdollars: number;
  is_active: boolean;
  created_at: string;
}''',
        },
        "routes": {
            "budgets": {
                "list": {"method": "GET", "path": "/api/budgets", "auth": True},
                "create": {"method": "POST", "path": "/api/budgets", "auth": True},
                "update": {"method": "PATCH", "path": "/api/budgets/[id]", "auth": True},
                "delete": {"method": "DELETE", "path": "/api/budgets/[id]", "auth": True},
            },
        },
    },
    6: {
        "types": {
            "Alert": '''export interface Alert {
  id: string;
  org_id: string;
  budget_id: string;
  type: 'soft_limit' | 'hard_limit' | 'anomaly';
  channel: 'slack' | 'email' | 'webhook';
  message: string;
  acknowledged: boolean;
  created_at: string;
}''',
            "AlertConfig": '''export interface AlertConfig {
  id: string;
  org_id: string;
  channel: 'slack' | 'email' | 'webhook';
  slack_webhook_url: string | null;
  email_address: string | null;
  webhook_url: string | null;
  is_active: boolean;
}''',
        },
        "routes": {
            "alerts": {
                "list": {"method": "GET", "path": "/api/alerts", "auth": True},
                "acknowledge": {"method": "POST", "path": "/api/alerts/[id]/acknowledge", "auth": True},
                "config": {"method": "GET", "path": "/api/alerts/config", "auth": True},
                "updateConfig": {"method": "PATCH", "path": "/api/alerts/config", "auth": True},
            },
        },
    },
    7: {
        "types": {
            "DashboardStats": '''export interface DashboardStats {
  total_spend_microdollars: number;
  spend_trend_pct: number;
  active_agents: number;
  total_calls: number;
  avg_cost_per_call_microdollars: number;
  top_model: string;
  budget_utilization_pct: number;
  alerts_unacknowledged: number;
}''',
            "CostBreakdown": '''export interface CostBreakdown {
  by_agent: Array<{ agent_id: string; name: string; cost: number }>;
  by_model: Array<{ model: string; cost: number; calls: number }>;
  by_hour: Array<{ hour: string; cost: number }>;
}''',
        },
        "routes": {
            "dashboard": {
                "stats": {"method": "GET", "path": "/api/dashboard/stats", "auth": True},
                "costBreakdown": {"method": "GET", "path": "/api/dashboard/cost-breakdown", "auth": True},
                "liveUpdates": {"method": "GET", "path": "/api/dashboard/live", "auth": True},
            },
        },
    },
    10: {
        "types": {
            "Team": '''export interface Team {
  id: string;
  org_id: string;
  name: string;
  budget_id: string | null;
  member_count: number;
  created_at: string;
}''',
        },
        "routes": {
            "teams": {
                "list": {"method": "GET", "path": "/api/teams", "auth": True},
                "create": {"method": "POST", "path": "/api/teams", "auth": True},
                "addMember": {"method": "POST", "path": "/api/teams/[id]/members", "auth": True},
                "removeMember": {"method": "DELETE", "path": "/api/teams/[id]/members/[userId]", "auth": True},
            },
        },
    },
    11: {
        "types": {
            "UsageData": '''export interface UsageData {
  agents: { used: number; limit: number };
  calls_this_month: number;
  plan: 'free' | 'team' | 'org' | 'enterprise';
  billing_period_end: string | null;
}''',
        },
        "routes": {
            "billing": {
                "createCheckout": {"method": "POST", "path": "/api/billing/create-checkout", "auth": True},
                "portal": {"method": "POST", "path": "/api/billing/portal", "auth": True},
                "usage": {"method": "GET", "path": "/api/billing/usage", "auth": True},
            },
            "webhooks": {
                "stripe": {"method": "POST", "path": "/api/webhooks/stripe", "auth": False},
            },
        },
    },
}
```

## Step 3: Run

```bash
# Terminal 1 — Start the builder
nohup python3 -u .buildrunner/run.py unattended > .buildrunner/logs/run.log 2>&1 &
echo $! > .buildrunner/.runner-pid

# Terminal 2 — Watch it build live
tail -f .buildrunner/logs/codex-live.log .buildrunner/logs/claude-live.log

# Terminal 3 — Health monitor every 5 minutes
watch -n 300 python3 .buildrunner/monitor.py

# Or from Claude Code REPL:
# CronCreate: */5 * * * *
# Prompt: cd $(pwd) && python3 .buildrunner/monitor.py
```

## Golden Jobs (Test After Sprint 5+)

### Job A — Single Agent, Daily Budget
> "I have one Claude agent that runs customer support overnight. Set a $5/day budget with Slack alert at 80%. If it exceeds $5, pause the agent."

Expected: Agent created, budget set to $5/day, Slack webhook configured, proxy key generated.

### Job B — Team of 5 Agents, Monthly Budget
> "My team runs 5 different Codex agents for code review. I want a $200/month team budget. Alert me at $150. Kill at $200."

Expected: Team created, 5 agents, budget $200/mo, soft limit 75%, hard limit 100%.

### Job C — Cost Anomaly Detection
> "One of my agents normally costs $0.50/day but yesterday it spent $15. I want to be alerted if any agent exceeds 3x its 7-day average."

Expected: Anomaly detection configured, historical analysis shows spike, alert fired.

### Job D — Multi-Provider Dashboard
> "I use Claude for reasoning and GPT-4 for embeddings. Show me total cost across both, broken down by model and by agent."

Expected: Dashboard shows combined view, model breakdown, agent breakdown, trend chart.
