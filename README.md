# Dual-Agent Builder

Two AI agents build your full-stack app while you sleep. Codex handles backend, Claude handles frontend. A shared TypeScript contract layer keeps them in sync. 20-pass Playwright design iteration makes it look premium.

**Born from:** Building [QuoteFast](https://quotefast.com.au) — 14 sprints, 5 completed autonomously in one session, total cost under $50.

## The Pipeline

```
┌─────────────────────────────────────────────────────┐
│                    Per Sprint                        │
│                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐   │
│  │  Codex   │───▶│ Contract │───▶│   Claude     │   │
│  │ Backend  │    │  Sync    │    │  Frontend    │   │
│  └──────────┘    └──────────┘    └──────────────┘   │
│       │                                │             │
│       │         ┌──────────┐          │             │
│       └────────▶│  Build   │◀─────────┘             │
│                 │  Verify  │                         │
│                 └────┬─────┘                         │
│                      │                               │
│              ┌───────▼───────┐                       │
│              │ 20-Pass Design│                       │
│              │  Iteration    │                       │
│              └───────┬───────┘                       │
│                      │                               │
│              ┌───────▼───────┐                       │
│              │  Git Commit   │                       │
│              └───────┬───────┘                       │
│                      │                               │
│              ┌───────▼───────┐                       │
│              │ Stage Review  │ (at boundaries)       │
│              │ + Commercial  │                       │
│              │    Gate       │                       │
│              └───────────────┘                       │
└─────────────────────────────────────────────────────┘
```

## Install as Claude Code Skill

```bash
# Add to your Claude Code settings
claude skill install /path/to/dual-agent-builder/SKILL.md
```

Or copy `SKILL.md` into your `~/.claude/skills/` directory.

## Manual Setup

```bash
# 1. Clone this repo
git clone https://github.com/Mitsi-ag/dual-agent-builder.git

# 2. Copy orchestrator into your project
cp -r dual-agent-builder/.buildrunner/ your-project/.buildrunner/

# 3. Edit config
$EDITOR your-project/.buildrunner/config.py

# 4. Write your planning docs (PRODUCT.md, ARCHITECTURE.md, etc.)
# See METHOD.md for the full documentation structure

# 5. Run
cd your-project
python3 .buildrunner/run.py preflight    # Verify prerequisites
python3 .buildrunner/run.py sprint 1     # Run one sprint
python3 .buildrunner/run.py unattended   # Run all sprints
```

## Live Development Viewing

Run the builder in one terminal, watch it work in another:

### Terminal 1 — Start the builder
```bash
cd your-project
nohup python3 -u .buildrunner/run.py unattended > .buildrunner/logs/run.log 2>&1 &
echo $! > .buildrunner/.runner-pid
echo "Runner started (PID: $(cat .buildrunner/.runner-pid))"
```

### Terminal 2 — Watch live output
```bash
cd your-project
# See all agent output in real-time (color-coded [codex] and [claude] prefixes)
tail -f .buildrunner/logs/codex-live.log .buildrunner/logs/claude-live.log

# Or follow the main runner log
tail -f .buildrunner/logs/run.log

# Or follow a specific sprint
tail -f .buildrunner/logs/sprint-3-frontend-1.log
```

### Terminal 3 (or Claude Code REPL) — Health monitor
```bash
# One-shot status check
python3 .buildrunner/monitor.py

# Or set up 5-minute cron in Claude Code:
# CronCreate: */5 * * * *
# Prompt: cd /path/to/project && python3 .buildrunner/monitor.py
```

Monitor output:
```
══════════════════════════════════════════════════
  Build Monitor [14:35]
══════════════════════════════════════════════════
  Status:    RUNNING
  Sprint:    5 of 14
  Phase:     Frontend (Claude)
  PID:       79414
  Commits:   4
  Last log:  2.3m ago
  Log file:  sprint-5-frontend-1.log

  Recent:
    [claude] Creating quote-wizard.tsx...
    [claude] Added 3 components, running pnpm build...
══════════════════════════════════════════════════
```

If the runner dies or gets stuck, the monitor gives you the exact restart command.

## What's in This Repo

```
dual-agent-builder/
├── SKILL.md                 ← Claude Code skill (install this)
├── METHOD.md                ← Full methodology (8 phases)
├── README.md                ← You are here
├── .buildrunner/            ← Copy into your project
│   ├── config.py            ← Edit for your project
│   ├── run.py               ← Main orchestrator
│   ├── cli.py               ← Agent CLI wrappers
│   ├── contracts.py         ← Contract generator
│   ├── prompts.py           ← Prompt builders
│   ├── state.py             ← Sprint state tracker
│   ├── preflight.py         ← Prerequisites checker
│   └── monitor.py           ← Health monitor (cron/standalone)
├── examples/
│   └── quotefast/
│       └── config.py        ← Real config from QuoteFast
└── ideas/                   ← Product ideas to build with this
    ├── README.md            ← Top 5 ideas overview
    ├── 01-agent-cost-controller.md
    ├── 02-agent-regression-preventer.md
    ├── 03-mcp-server-hosting.md
    ├── 04-voice-agent-testing.md
    ├── 05-vertical-intel-dashboard.md
    └── basagent/            ← Full build prompt example
        └── BUILD-PROMPT.md  ← Paste this to build BasAgent
```

## Product Ideas (Built With This Method)

The `ideas/` directory contains 5 validated product ideas, each scorable on the TEMPO framework (Timing, Ecosystem, Monetizable, Personal fit, Opportunity window). Each has a gap analysis, buyer persona, V1 scope, and pricing.

**BasAgent** (`ideas/basagent/BUILD-PROMPT.md`) includes a complete build prompt — paste it into a new project and run `python3 .buildrunner/run.py unattended` to build an Agent Cost Controller SaaS from scratch.

## Key Concepts

### Contract Layer
TypeScript files that both agents import. Eliminates the #1 integration bug: mismatched types and routes between backend and frontend.

### 20-Pass Design Iteration
After code is built, Claude uses Playwright to screenshot every page, review against the design guide, fix issues, and repeat 20 times. Focuses rotate from layout → details → edge cases → final polish.

### Circuit Breaker
3-state (CLOSED → HALF_OPEN → OPEN). Opens after 5 identical errors or 3 loops with no progress. Prevents runaway API spend on unrecoverable errors.

### Commercial Gates
Human checkpoints at stage boundaries. Prevents the founder trap of building 14 sprints and launching to silence. Each gate requires proof of real customer traction.

### File Protection
Before every agent call, validates that critical planning docs exist. If an agent accidentally deletes PRODUCT.md, it's restored from git before the next call.

## Prerequisites

| Tool | Install |
|------|---------|
| Claude Code | `npm install -g @anthropic-ai/claude-code` |
| Codex CLI | `npm install -g @openai/codex` |
| pnpm | `npm install -g pnpm` |
| Node.js | >= 18 |
| Python | >= 3.10 |

API keys needed in `.env.local`:
- `ANTHROPIC_API_KEY` (for Claude Code)
- `OPENAI_API_KEY` (for Codex)
- Plus any project-specific keys (Supabase, Stripe, etc.)

## Methodology

See [METHOD.md](METHOD.md) for the full 8-phase methodology:
1. Opportunity Research & Selection
2. Planning Documentation (~14,000 lines)
3. Contract Layer Setup
4. Automated Build Runner
5. Execution (`python3 .buildrunner/run.py unattended`)
6. Validation (Golden Jobs regression testing)
7. Commercial Gates (human checkpoints)
8. Post-Sprint Retrospective

## License

MIT
