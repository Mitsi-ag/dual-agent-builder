<!--
  THIS IS THE TEMPLATE. Each idea's BUILD-PROMPT.md appends this at the bottom.
  Variables filled per-project: {PROJECT}, {PRODUCT_NAME}, {PRODUCT_DESC}, {IDEA_NAME}
-->

---

## Autonomous Build Instructions

> **You are an autonomous software development agent. Execute every step below without asking questions.**
> Everything runs via exec. No interactive prompts. No human input needed.
> This pipeline: researches → plans → builds → monitors. You walk away.

### Step 1: Create project

```bash
PROJECT={PROJECT}
mkdir -p ~/Dev/$PROJECT && cd ~/Dev/$PROJECT
git init
cp -r ~/Dev/dual-agent-builder/.buildrunner/ .buildrunner/
mkdir -p .buildrunner/logs
```

### Step 2: Create Supabase project

```bash
cd ~/Dev/$PROJECT
DB_PASS=$(openssl rand -base64 24)
supabase projects create --org-id jpgcmqmhxodlohqjuafs --db-password "$DB_PASS" --region ap-southeast-2 ${PROJECT}-dev
sleep 20
REF=$(supabase projects list -o json | python3 -c "import json,sys; [print(p['id']) for p in json.load(sys.stdin) if p['name']=='${PROJECT}-dev']")
KEYS=$(supabase projects api-keys --project-ref $REF -o json)
ANON=$(echo "$KEYS" | python3 -c "import json,sys; [print(k['api_key']) for k in json.load(sys.stdin) if k.get('id')=='anon']" | head -1)
SVC=$(echo "$KEYS" | python3 -c "import json,sys; [print(k['api_key']) for k in json.load(sys.stdin) if k.get('id')=='service_role']" | head -1)
cat > .env.local << ENVEOF
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
NEXT_PUBLIC_SUPABASE_URL=https://${REF}.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=${ANON}
SUPABASE_SERVICE_ROLE_KEY=${SVC}
STRIPE_SECRET_KEY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=
RESEND_API_KEY=
NEXT_PUBLIC_APP_URL=http://localhost:3000
ENVEOF
supabase link --project-ref $REF
```

### Step 3: Launch autonomous pipeline

```bash
cd ~/Dev/$PROJECT
nohup python3 -u .buildrunner/autonomous.py \
  --name "{PRODUCT_NAME}" \
  --desc "{PRODUCT_DESC}" \
  --seed ~/Dev/dual-agent-builder/ideas/{IDEA_NAME}/BUILD-PROMPT.md \
  > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid
echo "Pipeline started (PID: $(cat .buildrunner/.autonomous-pid))"
```

### Step 4: Ralph supervision

```bash
export PATH="$HOME/.local/bin:$PATH"
bash ~/Dev/dual-agent-builder/.buildrunner/setup_ralph.sh ~/Dev/$PROJECT
cd ~/Dev/$PROJECT && ralph --monitor
```

If Ralph is not installed:
```bash
git clone https://github.com/frankbria/ralph-claude-code.git /tmp/ralph-claude-code
cd /tmp/ralph-claude-code && ./install.sh
export PATH="$HOME/.local/bin:$PATH"
# Then retry Step 4
```

### Step 5: Verify

```bash
cd ~/Dev/$PROJECT && python3 .buildrunner/monitor.py
tail -5 .buildrunner/logs/autonomous.log
```

### What happens next (no action needed)
- **Phase 1 (6-9 hours):** Codex runs 12 planning passes: market research, product spec, architecture, design system, developer guide, sprint plans, contract types, CLAUDE.md rules, self-review, golden jobs, final quality gate
- **Phase 2 (4-8 hours):** Per sprint: Codex builds backend → contracts sync → Claude builds frontend → 5-pass Playwright design iteration → git commit → stage review
- **Ralph** checks every 5 min, auto-restarts dead processes, detects stuck agents, logs everything

### If it dies (without Ralph), resume

```bash
cd ~/Dev/$PROJECT
nohup python3 -u .buildrunner/autonomous.py --resume > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid
```

### Prerequisites
- `codex` CLI + OPENAI_API_KEY in env
- `claude` CLI + ANTHROPIC_API_KEY in env
- `supabase` CLI (logged in)
- `pnpm`, `node` >= 18, `python3` >= 3.9
- `ralph` (recommended): frankbria/ralph-claude-code
- `brew install coreutils` (macOS, for Ralph)
