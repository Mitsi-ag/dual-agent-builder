# Product Ideas — Build These With Dual-Agent Builder

5 validated product ideas from March 2026 trend research. Each scored on the TEMPO framework, with gap analysis, buyer persona, V1 scope, and pricing.

All of these can be built using the dual-agent-builder orchestrator in under 30 days.

## The Ideas

| # | Idea | TEMPO | First Dollar | Who Pays | Price |
|---|------|-------|-------------|----------|-------|
| 1 | **Agent Cost Controller** | 24/25 | Week 3 | Engineering leads, DevOps, CTOs | $49-199/mo |
| 2 | **Agent Regression Preventer** | 22/25 | Week 4 | Dev teams (10+ devs) | $29-99/dev/mo |
| 3 | **MCP Server Hosting** | 23/25 | Week 3 | MCP server authors, companies | $29-499/mo |
| 4 | **Voice Agent Testing** | 21/25 | Week 4 | Companies with voice agents | $99-999/mo |
| 5 | **Vertical Intel Dashboard** | 20/25 | Week 3 | Analysts, VPs, hedge funds | $79-999/mo |

## TEMPO Scoring Framework

| Criteria | Question |
|----------|----------|
| **T**iming | Is this early enough? (1=saturated, 5=emerging) |
| **E**cosystem | Growing ecosystem around it? (repos, tools, community) |
| **M**onetizable | Will someone pay? Who specifically? |
| **P**ersonal fit | Can we build this? (skills, stack, interest) |
| **O**pportunity window | How long until crowded? (1=months, 5=years) |

20-25=HOT, 15-19=WARM, 10-14=COOL, <10=PASS

## Full Build Example: BasAgent

See `basagent/BUILD-PROMPT.md` for a complete, paste-ready build prompt that creates the Agent Cost Controller from scratch using the dual-agent-builder pipeline. Includes:
- All 14 sprint definitions
- Contract types per sprint
- Planning doc structure
- Monitoring setup
- Live development viewing

Run it:
```bash
mkdir basagent && cd basagent
cp -r /path/to/dual-agent-builder/.buildrunner/ .buildrunner/
# Follow BUILD-PROMPT.md instructions
python3 .buildrunner/run.py unattended
```
