# Autonomous Execution Block
# Appended to every BUILD-PROMPT.md. This section turns the Claude session
# into the orchestrator AND ongoing monitor.

---

## YOU ARE THE ORCHESTRATOR. Execute everything below. Do not ask questions.

### Phase A: Project Setup

```bash
PROJECT={PROJECT}
mkdir -p ~/Dev/$PROJECT && cd ~/Dev/$PROJECT
git init
cp -r ~/Dev/dual-agent-builder/.buildrunner/ .buildrunner/
mkdir -p .buildrunner/logs
```

### Phase B: Supabase (auto-create project in Uptrail org, Sydney)

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

### Phase C: Launch Autonomous Pipeline

```bash
cd ~/Dev/$PROJECT
nohup python3 -u .buildrunner/autonomous.py \
  --name "{PRODUCT_NAME}" \
  --desc "{PRODUCT_DESC}" \
  --seed ~/Dev/dual-agent-builder/ideas/{IDEA}/BUILD-PROMPT.md \
  > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid
echo "Pipeline started (PID: $(cat .buildrunner/.autonomous-pid))"
```

### Phase D: Verify Launch

```bash
sleep 10
cd ~/Dev/$PROJECT && python3 .buildrunner/monitor.py
tail -5 .buildrunner/logs/autonomous.log
```

### Phase E: YOU BECOME THE MONITOR

Set up a cron to check every 5 minutes. You stay in this session as the supervisor.

```
CronCreate: */5 * * * *
Prompt: |
  Run the pipeline monitor and report status:
  ```bash
  cd ~/Dev/{PROJECT} && python3 .buildrunner/monitor.py 2>&1
  ```
  Also check the last 5 lines of the autonomous log:
  ```bash
  tail -5 ~/Dev/{PROJECT}/.buildrunner/logs/autonomous.log 2>/dev/null
  ```
  If status is DEAD, restart immediately:
  ```bash
  cd ~/Dev/{PROJECT} && nohup python3 -u .buildrunner/autonomous.py --resume > .buildrunner/logs/autonomous.log 2>&1 & echo $! > .buildrunner/.autonomous-pid
  ```
  If STUCK (>45 min), kill and restart:
  ```bash
  kill $(cat ~/Dev/{PROJECT}/.buildrunner/.autonomous-pid) 2>/dev/null; sleep 5; cd ~/Dev/{PROJECT} && nohup python3 -u .buildrunner/autonomous.py --resume > .buildrunner/logs/autonomous.log 2>&1 & echo $! > .buildrunner/.autonomous-pid
  ```
  If RUNNING, give a one-line summary.
  If COMPLETE, report final status and stop the cron.
```

After setting up the cron, confirm: "Monitoring active. Pipeline running. Checking every 5 minutes."

### What happens (no action needed)
- **Phase 1 (6-9 hours):** Codex runs 12 planning passes -- market research, product spec, architecture, design system, sprint plans, contracts, quality gate
- **Phase 2 (4-8 hours):** Per sprint -- Codex backend, contract sync, Claude frontend, 5-pass Playwright design iteration, git commit, stage review
- **You** check every 5 min, auto-restart if dead, kill+restart if stuck, report when complete
