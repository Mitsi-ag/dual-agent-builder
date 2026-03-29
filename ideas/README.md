# Product Ideas — Build These With Dual-Agent Builder

From the [uptrail-ventures](https://github.com/Mitsi-ag/uptrail-ventures) research: 20 AU-focused SaaS ideas scored by opportunity, ranked by **fastest path to meaningful money**.

QuoteFast (AI quoting for tradies) is already building autonomously — 5 sprints completed, runner active.

## Top 4 Next Builds (by speed-to-revenue)

| # | Venture | Score | Market | Price | Why Fast |
|---|---------|-------|--------|-------|----------|
| 1 | **ShieldAU** | 20/25 | $500M | $199-499/mo | Zero AU competitors in SME tier. Regulatory mandate (Essential Eight). Compliance = checklists + reports = pure software |
| 2 | **StrataFlow** | 20/25 | $400M | $100-500/mo | 300K strata schemes. Aging workforce. Per-lot pricing. Well-defined workflows |
| 3 | **SpendPilot** | 19/25 | $500M-1B | $200/mo avg | Ramp model proven ($32B val). 2.5M AU SMBs still on spreadsheets |
| 4 | **BriefMate** | —/25 | $8B | $49-200/mo | AI legal research = Claude API + document processing. Self-serve law firms |

## Full 20 Ventures (from uptrail-ventures research)

| Venture | What | Market | Score |
|---------|------|--------|-------|
| QuoteFast | AI quoting for tradies | $300M | **BUILDING** |
| ShieldAU | Vanta for AU (Essential Eight) | $500M | 20/25 |
| StrataFlow | AI strata management | $400M | 20/25 |
| SpendPilot | Ramp for AU expense management | $500M-1B | 19/25 |
| BasPilot | AI tax compliance | $500M | —/25 |
| BriefMate | AI legal assistant | $8B | —/25 |
| BuildPay | Construction payment automation | $315M | —/25 |
| CarbonLens | Carbon accounting for SMBs | $200M | —/25 |
| ClaimFlow | Insurance claims AI | $376M | —/25 |
| CoverNow | Parametric climate insurance | $8B | —/25 |
| EnrichAU | AU data enrichment | $200M | —/25 |
| EquityStack | Equity management | $1.2B | —/25 |
| MedMatch | Healthcare staffing | $80M | —/25 |
| OrderDirect | Restaurant direct ordering | $120M | —/25 |
| PermitPro | Construction permits | $215M | —/25 |
| PropStack | Property data platform | $200-500M | —/25 |
| RentReward | Rental rewards | $6B | —/25 |
| SkillBridge | Workforce skills platform | $2B | —/25 |
| TeachMate | Teacher tools (ACARA) | $110M | —/25 |
| TradeHire | Trades recruitment | $200-300M | 17/25 |

## How to Build Any of These

Each `BUILD-PROMPT.md` contains everything needed:
1. Product vision + pricing + decisions
2. 14 sprints with backend/frontend tasks
3. TypeScript contract types per sprint
4. Design direction
5. Golden jobs (test scenarios)
6. Exact run commands with monitoring + live logging

```bash
mkdir my-venture && cd my-venture
git init
cp -r /path/to/dual-agent-builder/.buildrunner/ .buildrunner/
# Follow the BUILD-PROMPT.md for your chosen venture
# Write planning docs (PRODUCT.md, ARCHITECTURE.md, etc.)
# Edit .buildrunner/config.py with the sprint/contract config from BUILD-PROMPT.md

# Terminal 1 — Build autonomously
nohup python3 -u .buildrunner/run.py unattended > .buildrunner/logs/run.log 2>&1 &
echo $! > .buildrunner/.runner-pid

# Terminal 2 — Watch live development
tail -f .buildrunner/logs/codex-live.log .buildrunner/logs/claude-live.log

# Terminal 3 — Health monitor every 5 min
watch -n 300 python3 .buildrunner/monitor.py
```
