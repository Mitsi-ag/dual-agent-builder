# Agent Cost Controller

**TEMPO Score: 24/25** (T:5 E:5 M:5 P:5 O:4)

## The Signal
Every team running AI agents is getting surprise API bills. AgentOps exists for retrospective analysis, but nothing enforces budgets in real-time. The "Day 2 agent problems" wave is just starting.

## The Gap
- AgentOps: observability only, no budget enforcement
- LangSmith: traces and debugging, not cost control
- Manual monitoring: checking dashboards after the damage is done
- No tool intercepts API calls and says "STOP, budget exceeded"

## The Product (BasAgent)
MCP server that intercepts LLM API calls. Dashboard showing cost per agent/task/team. Budget alerts + auto-kill for runaway agents. Think "CloudWatch billing alarms but for AI agents."

### V1 Features (ship in 2 weeks)
- MCP server that proxies Anthropic + OpenAI calls
- Real-time cost tracking per agent/session/team
- Budget limits with auto-pause (soft) and auto-kill (hard)
- Dashboard: cost breakdown, top spenders, trend charts
- Slack/email alerts at 50%, 80%, 100% of budget
- Team management: invite members, set per-team budgets

## The Buyer
- **Primary:** Engineering leads running 5+ agents in production
- **Secondary:** DevOps teams managing LLM infrastructure costs
- **Tertiary:** CTOs who got a surprise $10K API bill last month
- **Signal:** Every "my agent spent $500 overnight" Reddit post

## Pricing
| Tier | Price | Limits |
|------|-------|--------|
| Free | $0 | 1 agent, 1K tracked calls/mo |
| Team | $49/mo | 20 agents, unlimited calls, 5 team members |
| Org | $199/mo | Unlimited agents, SSO, audit logs, API |
| Enterprise | $499/mo | Custom, SLA, dedicated support |

## The Moat
- Cost benchmark data across customers (anonymized)
- Integration depth with every LLM provider
- Switching cost once teams build workflows around budget alerts
- First mover in "agent cost governance"

## Stack
Next.js 15 + TypeScript + Supabase + Vercel + Stripe

## Competitors
| Competitor | Gap |
|-----------|-----|
| AgentOps | Retrospective only, no enforcement |
| LangSmith | Traces, not costs |
| Helicone | Logging, no budget control |
| Manual dashboards | No real-time alerts, no auto-pause |

## Validation Steps
1. [ ] Post on r/LocalLLaMA + r/ClaudeAI about agent cost pain
2. [ ] DM 20 people who complained about API bills on Twitter
3. [ ] Build landing page + waitlist (1 day)
4. [ ] Get 50 signups or pivot
5. [ ] Ship V1, get 3 paying teams in 30 days
