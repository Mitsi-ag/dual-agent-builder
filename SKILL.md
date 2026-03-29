---
name: dual-agent-builder
description: Orchestrate two AI agents (Codex backend + Claude frontend) to build full-stack apps sprint by sprint with shared contract layer, circuit breakers, 20-pass design iteration, and autonomous monitoring
---

# Dual-Agent Builder

Fully automated software development pipeline. Two AI agents build your app sprint by sprint while you sleep.

## What It Does

```
Per Sprint (automated):
  1. Preflight checks (tools, docs, env vars)
  2. Validate protected files (restore from git if deleted)
  3. Generate TypeScript contract skeleton
  4. Codex builds backend (reads planning docs from disk)
  5. Verify pnpm build passes (retry with error context if fails)
  6. Update contracts with what Codex actually built
  7. Claude builds frontend (reads docs + imports contracts)
  8. Verify pnpm build passes (retry with error context if fails)
  9. 20-pass Playwright design iteration (screenshot → review → fix)
  10. Git commit
  11. Stage review by Codex (at stage boundaries)
  12. Commercial gate check (human checkpoint)
  13. Advance to next sprint
```

## Quick Start

### 1. Copy orchestrator into your project

```bash
cp -r /path/to/dual-agent-builder/.buildrunner/ your-project/.buildrunner/
```

### 2. Edit config for your project

```bash
$EDITOR your-project/.buildrunner/config.py
```

Fill in: `PROJECT_NAME`, `SPRINT_STAGES`, `SPRINT_NAMES`, `COMMERCIAL_GATES`, `SPRINT_CONTRACTS` (TypeScript types and routes per sprint), `ENV_REQUIREMENTS`, `PROTECTED_FILES`.

See `examples/quotefast/config.py` for a fully filled-in example (14 sprints, 7 stages, 12 contract types, 30+ API routes).

### 3. Create planning docs BEFORE any code

Your project needs these files (the agents READ them from disk):

| File | Purpose |
|------|---------|
| `PRODUCT.md` | Vision, features, pricing, kill signals |
| `CLAUDE.md` | AI rules, design axioms, pre-ship checklist |
| `DECISIONS.md` | Numbered decision log (D001-D0XX) |
| `docs/ARCHITECTURE.md` | DB schema, API contracts, security |
| `docs/DESIGN-GUIDE.md` | Colors, typography, spacing, components |
| `docs/DEVELOPER-GUIDE.md` | Structure, conventions, patterns |
| `docs/sprints/stage-N-*.md` | Sprint tasks (### Backend / ### Frontend) |

Each sprint doc must have `### Backend` and `### Frontend` sections listing exactly what to build.

### 4. Run

```bash
# Check everything is ready
python3 .buildrunner/run.py preflight

# Run one sprint
python3 .buildrunner/run.py sprint 1

# Run everything unattended (auto-approve commercial gates)
nohup python3 -u .buildrunner/run.py unattended > .buildrunner/logs/run.log 2>&1 &
echo $! > .buildrunner/.runner-pid
```

### 5. Monitor (two terminal windows)

**Window 1 — Live build output:**
```bash
tail -f .buildrunner/logs/codex-live.log .buildrunner/logs/claude-live.log
```

**Window 2 — Health monitor (from Claude Code REPL):**
```
CronCreate: */5 * * * *
Prompt: cd /path/to/project && python3 .buildrunner/monitor.py
```

The monitor checks:
- Is the runner process alive? (PID file)
- Is it making progress? (file mtime on logs)
- Has it been stuck for 30+ minutes? (no log writes)
- What sprint/phase is it on?
- How many git commits so far?

If the runner dies, the monitor tells you how to restart it.

## The Contract Layer (Why This Works)

Without contracts, Codex builds `/api/quotes` and Claude fetches `/api/quote/list`. Types mismatch, nothing works.

The contract layer generates three TypeScript files that BOTH agents import:

```
src/contracts/
├── api-types.ts    ← All request/response interfaces
├── api-routes.ts   ← Route paths, methods, auth requirements
└── constants.ts    ← Shared business constants
```

Define your contracts in `config.py`:

```python
SPRINT_CONTRACTS = {
    1: {
        "types": {
            "User": '''export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}''',
        },
        "routes": {
            "auth": {
                "callback": {"method": "POST", "path": "/api/auth/callback", "auth": False},
            },
        },
    },
}
```

After Codex builds the backend, the runner updates contracts with what was actually implemented. Claude then imports these exact types for the frontend.

## Design Iteration (20-Pass Visual Polish)

After frontend code is built, the runner:
1. Starts `pnpm dev` server
2. Claude uses Playwright to screenshot every page at 375px mobile width
3. Reviews against DESIGN-GUIDE.md
4. Fixes issues in component source files
5. Screenshots again to verify
6. Repeats 20 times with rotating focus:

| Pass | Focus |
|------|-------|
| 1-3 | Layout, colors, typography |
| 4-6 | Touch targets, loading states, error states |
| 7-9 | Empty states, dark mode, animations |
| 10-14 | Edge cases, navigation flow, interactive states |
| 15-18 | Professional trust, visual rhythm, micro-spacing |
| 19-20 | Final sweep — screenshot every page, fix ANY inconsistency |

## Circuit Breaker

Prevents runaway loops and wasted API spend:
- 5 identical errors → stop retrying
- 3 loops with 0 file changes → skip to next phase
- Sprint exceeds cost threshold → halt

When the circuit opens: log the blocker, commit whatever progress was made, skip to next sprint or halt.

## Commercial Gates (Human Checkpoints)

At each stage boundary, the build pauses for a human checkpoint:

| Stage | Gate |
|-------|------|
| 0 | Discovery calls completed |
| 1 | 1 real person signed up |
| 2 | 1 real user completed core workflow |
| 3 | 3 AI outputs at production quality |
| 4 | 1 output delivered to real customer |
| 5 | 3 paying customers |
| 6 | $500+ MRR |

In `unattended` mode, gates are auto-approved (review when you return).

## File Structure

```
your-project/
├── .buildrunner/
│   ├── config.py          ← YOU EDIT THIS
│   ├── run.py             ← Main orchestrator
│   ├── cli.py             ← Codex/Claude CLI wrappers
│   ├── contracts.py       ← Contract generator
│   ├── prompts.py         ← Prompt builders
│   ├── state.py           ← Sprint progress tracker
│   ├── preflight.py       ← Prerequisites checker
│   ├── monitor.py         ← Health monitor (cron)
│   ├── .state             ← Last completed sprint (auto)
│   ├── .runner-pid        ← Runner process ID (auto)
│   ├── logs/              ← All agent output (auto)
│   ├── prompts/           ← Generated prompts (auto)
│   └── reviews/           ← Stage reviews (auto)
├── src/contracts/          ← Generated by runner
│   ├── api-types.ts
│   ├── api-routes.ts
│   └── constants.ts
├── PRODUCT.md
├── CLAUDE.md
├── DECISIONS.md
└── docs/
    ├── ARCHITECTURE.md
    ├── DESIGN-GUIDE.md
    ├── DEVELOPER-GUIDE.md
    └── sprints/
        ├── stage-1-foundation.md
        └── ...
```

## Prerequisites

- `claude` CLI (Claude Code) — `npm install -g @anthropic-ai/claude-code`
- `codex` CLI (OpenAI Codex) — `npm install -g @openai/codex`
- `pnpm` — `npm install -g pnpm`
- `node` >= 18
- Planning docs written and committed to git
- `.env.local` with required API keys
