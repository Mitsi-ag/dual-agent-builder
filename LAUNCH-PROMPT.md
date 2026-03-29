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

Execute ALL steps below. Do not ask questions. Do not explain. Just do it.

---

### Step 1: Pick the product

Choose ONE from the ideas in `~/Dev/dual-agent-builder/ideas/`:

```bash
ls ~/Dev/dual-agent-builder/ideas/
cat ~/Dev/dual-agent-builder/ideas/README.md
```

Available ideas:
| Idea | Description | Seed File |
|------|-------------|-----------|
| **shieldau** | Essential Eight compliance for AU SMBs ($500M market) | `ideas/shieldau/BUILD-PROMPT.md` |
| **strataflow** | AI strata management ($400M market) | `ideas/strataflow/BUILD-PROMPT.md` |
| **spendpilot** | Ramp for AU expense management ($500M-1B market) | `ideas/spendpilot/BUILD-PROMPT.md` |
| **briefmate** | AI legal assistant ($8B market) | `ideas/briefmate/BUILD-PROMPT.md` |

Or provide your own `--name` and `--desc` for a custom product (no seed file needed).

### Step 2: Create the project

```bash
PROJECT=[project-name]
mkdir -p ~/Dev/$PROJECT && cd ~/Dev/$PROJECT
git init
cp -r ~/Dev/dual-agent-builder/.buildrunner/ .buildrunner/
mkdir -p .buildrunner/logs
```

### Step 3: Create Supabase project

Use the Uptrail org (`jpgcmqmhxodlohqjuafs`). Sydney region.

```bash
DB_PASS=$(openssl rand -base64 24)
supabase projects create --org-id jpgcmqmhxodlohqjuafs --db-password "$DB_PASS" --region ap-southeast-2 ${PROJECT}-dev
```

Wait 15 seconds for provisioning, then get the project ref and keys:

```bash
sleep 15
REF=$(supabase projects list -o json | python3 -c "import json,sys; [print(p['id']) for p in json.load(sys.stdin) if p['name']=='${PROJECT}-dev']")
KEYS=$(supabase projects api-keys --project-ref $REF -o json)
ANON_KEY=$(echo "$KEYS" | python3 -c "import json,sys; [print(k['api_key']) for k in json.load(sys.stdin) if k.get('name')=='anon' or (k.get('type')=='legacy' and k.get('id')=='anon')]" | head -1)
SERVICE_KEY=$(echo "$KEYS" | python3 -c "import json,sys; [print(k['api_key']) for k in json.load(sys.stdin) if k.get('name')=='service_role' or (k.get('type')=='legacy' and k.get('id')=='service_role')]" | head -1)
```

Write `.env.local`:
```bash
cat > ~/Dev/$PROJECT/.env.local << ENVEOF
# === AI Agents ===
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}

# === Supabase (${PROJECT}-dev, Sydney) ===
NEXT_PUBLIC_SUPABASE_URL=https://${REF}.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=${ANON_KEY}
SUPABASE_SERVICE_ROLE_KEY=${SERVICE_KEY}

# === Stripe (add when needed at Sprint 12) ===
STRIPE_SECRET_KEY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=

# === Email (add when needed at Sprint 8) ===
RESEND_API_KEY=

# === App Config ===
NEXT_PUBLIC_APP_URL=http://localhost:3000
ENVEOF
```

Link Supabase to the project:
```bash
cd ~/Dev/$PROJECT && supabase link --project-ref $REF
```

### Step 4: Launch the autonomous pipeline

With a seed idea from the repo:
```bash
cd ~/Dev/$PROJECT
nohup python3 -u .buildrunner/autonomous.py \
  --name "[ProductName]" \
  --desc "[One-line description]" \
  --seed ~/Dev/dual-agent-builder/ideas/[idea-name]/BUILD-PROMPT.md \
  > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid
echo "Pipeline started (PID: $(cat .buildrunner/.autonomous-pid))"
```

Without seed (custom product):
```bash
cd ~/Dev/$PROJECT
nohup python3 -u .buildrunner/autonomous.py \
  --name "[ProductName]" \
  --desc "[One-line description]" \
  > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid
echo "Pipeline started (PID: $(cat .buildrunner/.autonomous-pid))"
```

### Step 5: Set up Ralph supervision

```bash
cd ~/Dev/$PROJECT
bash ~/Dev/dual-agent-builder/.buildrunner/setup_ralph.sh ~/Dev/$PROJECT
cd ~/Dev/$PROJECT && ralph --monitor
```

If Ralph is not installed:
```bash
git clone https://github.com/frankbria/ralph-claude-code.git /tmp/ralph-claude-code
cd /tmp/ralph-claude-code && ./install.sh
export PATH="$HOME/.local/bin:$PATH"
```

Then retry the Ralph setup above.

### Step 6: Verify everything is running

```bash
cd ~/Dev/$PROJECT && python3 .buildrunner/monitor.py
tail -5 .buildrunner/logs/autonomous.log
```

---

## Full Example: Build StrataFlow

```bash
# 1. Create project
PROJECT=strataflow
mkdir -p ~/Dev/$PROJECT && cd ~/Dev/$PROJECT
git init
cp -r ~/Dev/dual-agent-builder/.buildrunner/ .buildrunner/
mkdir -p .buildrunner/logs

# 2. Supabase
DB_PASS=$(openssl rand -base64 24)
supabase projects create --org-id jpgcmqmhxodlohqjuafs --db-password "$DB_PASS" --region ap-southeast-2 strataflow-dev
sleep 15
REF=$(supabase projects list -o json | python3 -c "import json,sys; [print(p['id']) for p in json.load(sys.stdin) if p['name']=='strataflow-dev']")
KEYS=$(supabase projects api-keys --project-ref $REF -o json)
ANON_KEY=$(echo "$KEYS" | python3 -c "import json,sys; [print(k['api_key']) for k in json.load(sys.stdin) if k.get('id')=='anon']" | head -1)
SERVICE_KEY=$(echo "$KEYS" | python3 -c "import json,sys; [print(k['api_key']) for k in json.load(sys.stdin) if k.get('id')=='service_role']" | head -1)

cat > .env.local << ENVEOF
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
NEXT_PUBLIC_SUPABASE_URL=https://${REF}.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=${ANON_KEY}
SUPABASE_SERVICE_ROLE_KEY=${SERVICE_KEY}
STRIPE_SECRET_KEY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=
RESEND_API_KEY=
NEXT_PUBLIC_APP_URL=http://localhost:3000
ENVEOF

supabase link --project-ref $REF

# 3. Launch pipeline
nohup python3 -u .buildrunner/autonomous.py \
  --name "StrataFlow" \
  --desc "AI-powered strata management platform for Australian strata schemes. Levy management, maintenance tracking, AI meeting minutes, compliance engine, owner portal." \
  --seed ~/Dev/dual-agent-builder/ideas/strataflow/BUILD-PROMPT.md \
  > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid

# 4. Ralph supervision
bash ~/Dev/dual-agent-builder/.buildrunner/setup_ralph.sh ~/Dev/strataflow
cd ~/Dev/strataflow && ralph --monitor
```

---

## Prerequisites

| Tool | Install | Required |
|------|---------|----------|
| `codex` CLI | `npm install -g @openai/codex` + `OPENAI_API_KEY` in env | Yes |
| `claude` CLI | `npm install -g @anthropic-ai/claude-code` + `ANTHROPIC_API_KEY` in env | Yes |
| `supabase` CLI | `brew install supabase/tap/supabase` + `supabase login` | Yes |
| `ralph` | `git clone frankbria/ralph-claude-code && ./install.sh` | Recommended |
| `pnpm` | `npm install -g pnpm` | Yes |
| `node` | >= 18 | Yes |
| `python3` | >= 3.9 | Yes |
| `coreutils` | `brew install coreutils` (macOS, for Ralph) | For Ralph |
| `tmux` | `brew install tmux` (for Ralph --monitor view) | Optional |

## Supabase Org

All projects go under the **Uptrail** org: `jpgcmqmhxodlohqjuafs`

Rename in dashboard if still showing as "quotefast": Settings > General > Organization name > "Uptrail"

## If it dies, resume

```bash
cd ~/Dev/$PROJECT
nohup python3 -u .buildrunner/autonomous.py --resume > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid
```

With Ralph running, this happens automatically.
