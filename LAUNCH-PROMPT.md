# Launch Prompt -- Start a New Autonomous Software Build

> **Paste this into a new Claude Code session to kick off a fully autonomous build.**
> Replace the variables in `[brackets]` with your product details.
> Everything runs via `exec` -- no interactive prompts, no human input needed.

---

## Instructions for Claude

You are launching a fully autonomous software development pipeline. This system:
1. **Phase 1 (Planning):** Runs 12 passes of Codex over 6-9 hours to produce research-backed planning docs
2. **Phase 2 (Building):** Runs 14 sprints with Codex (backend) + Claude (frontend) over 4-8 hours
3. **Phase 3 (Supervision):** Ralph monitors every 5 minutes, auto-restarts dead processes, fixes stuck builds

### Step 1: Create the project

```bash
mkdir -p ~/Dev/[project-name]
cd ~/Dev/[project-name]
git init
cp -r ~/Dev/dual-agent-builder/.buildrunner/ .buildrunner/
```

### Step 2: Launch the autonomous pipeline

If you have a BUILD-PROMPT.md seed file:
```bash
cd ~/Dev/[project-name]
mkdir -p .buildrunner/logs
nohup python3 -u .buildrunner/autonomous.py \
  --name "[ProductName]" \
  --desc "[One-line description of the product]" \
  --seed ~/Dev/dual-agent-builder/ideas/[idea-name]/BUILD-PROMPT.md \
  > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid
echo "Autonomous pipeline started (PID: $(cat .buildrunner/.autonomous-pid))"
```

Without seed (pure AI research):
```bash
cd ~/Dev/[project-name]
mkdir -p .buildrunner/logs
nohup python3 -u .buildrunner/autonomous.py \
  --name "[ProductName]" \
  --desc "[One-line description of the product]" \
  > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid
echo "Autonomous pipeline started (PID: $(cat .buildrunner/.autonomous-pid))"
```

### Step 3: Set up Ralph supervision (recommended)

Ralph is an autonomous monitoring loop that checks the build every 5 minutes, auto-restarts dead processes, and fixes stuck builds.

```bash
# Set up Ralph for this project
cd ~/Dev/[project-name]
bash ~/Dev/dual-agent-builder/.buildrunner/setup_ralph.sh ~/Dev/[project-name]

# Start Ralph supervisor (tmux 3-pane: loop | live output | dashboard)
cd ~/Dev/[project-name] && ralph --monitor
```

Ralph will:
- Check pipeline health every 5 minutes
- Auto-restart if the pipeline dies
- Detect stuck processes (>45 min no progress)
- Kill and restart stuck agents
- Log everything to `.ralph/logs/`
- Exit only when all 14 sprints are complete

### Step 3 (alternative): Simple cron monitor

If Ralph is not installed, use a basic cron:
```
CronCreate: */5 * * * *
Prompt: cd ~/Dev/[project-name] && python3 .buildrunner/monitor.py
```

### Step 4: Watch live (optional)

```bash
# All agent output
tail -f ~/Dev/[project-name]/.buildrunner/logs/codex-live.log ~/Dev/[project-name]/.buildrunner/logs/claude-live.log

# Planning progress
tail -f ~/Dev/[project-name]/.buildrunner/logs/autonomous.log

# One-shot status
cd ~/Dev/[project-name] && python3 .buildrunner/monitor.py

# Ralph status
cd ~/Dev/[project-name] && ralph --status
```

### Step 5: If it dies (without Ralph), resume manually

```bash
cd ~/Dev/[project-name]
nohup python3 -u .buildrunner/autonomous.py --resume > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid
```

With Ralph running, this happens automatically.

---

## Available Seed Ideas (in ~/Dev/dual-agent-builder/ideas/)

| Idea | Description | Seed File |
|------|-------------|-----------|
| ShieldAU | Essential Eight compliance for AU SMBs | `ideas/shieldau/BUILD-PROMPT.md` |
| StrataFlow | AI strata management | `ideas/strataflow/BUILD-PROMPT.md` |
| SpendPilot | Ramp for AU expense management | `ideas/spendpilot/BUILD-PROMPT.md` |
| BriefMate | AI legal assistant | `ideas/briefmate/BUILD-PROMPT.md` |

---

## Prerequisites

Ensure these are installed and authenticated:
- `codex` CLI: `npm install -g @openai/codex` + OPENAI_API_KEY in env
- `claude` CLI: `npm install -g @anthropic-ai/claude-code` + ANTHROPIC_API_KEY in env
- `ralph`: `git clone https://github.com/frankbria/ralph-claude-code.git && cd ralph-claude-code && ./install.sh`
- `pnpm`: `npm install -g pnpm`
- `node` >= 18
- `python3` >= 3.10
- `brew install coreutils` (macOS, for Ralph's timeout)
- `tmux` (recommended, for Ralph's 3-pane monitor view)

---

## Full Example: Build ShieldAU with Ralph Supervision

```bash
# 1. Create project
mkdir -p ~/Dev/shieldau && cd ~/Dev/shieldau
git init
cp -r ~/Dev/dual-agent-builder/.buildrunner/ .buildrunner/

# 2. Launch autonomous pipeline
mkdir -p .buildrunner/logs
nohup python3 -u .buildrunner/autonomous.py \
  --name "ShieldAU" \
  --desc "Essential Eight compliance platform for Australian SMBs. AI-powered maturity assessment, evidence vault, remediation tracking, and auditor-ready PDF reports." \
  --seed ~/Dev/dual-agent-builder/ideas/shieldau/BUILD-PROMPT.md \
  > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid

# 3. Set up Ralph supervision
bash ~/Dev/dual-agent-builder/.buildrunner/setup_ralph.sh ~/Dev/shieldau

# 4. Start Ralph (monitors every 5 min, auto-restarts, auto-recovers)
cd ~/Dev/shieldau && ralph --monitor
```

Then walk away. Ralph watches the build. You come back to a finished app.
