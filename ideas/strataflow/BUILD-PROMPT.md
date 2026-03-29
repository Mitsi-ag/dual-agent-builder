# StrataFlow — AI Strata Management for Australia

> 300,000 strata schemes. Most managed with spreadsheets. EliseAI is worth $2.25B.
>
> **Score:** 20/25 | **Market:** $400M | **Price:** $2-5/lot/mo | **Workforce aging out**
>
> Paste this → write planning docs → run the builder → monitor.

---

## The Opportunity

300K+ Australian strata schemes across 8 states with 8 different legislations. Strata managers handle levies, maintenance, insurance, disputes, meetings, and compliance — mostly on spreadsheets or aging software (StrataMax, Strata Master from the '90s). The workforce is retiring with no succession plan. AI-native management is inevitable. Per-lot pricing: a 100-lot building = $200-500/mo. 500 schemes at $100/mo avg = $600K ARR.

## Tech Stack
Next.js 15, TypeScript, Tailwind v4, Supabase, Vercel, Stripe, Resend

## 14 Sprints / 7 Stages

### Stage 1 — Foundation (Sprints 1-2)
- **Sprint 1 Backend:** Auth, strata_schemes table (name, address, lot_count, state, legislation), lots table, owners_corporations table, users with role (manager/committee/owner)
- **Sprint 1 Frontend:** Login, signup, scheme onboarding wizard (state → legislation auto-detected)
- **Sprint 2 Backend:** Levy management — levy_schedules table, levy_items (admin fund, capital works fund, special levies), owner_levies (per-lot amounts), payment tracking
- **Sprint 2 Frontend:** Levy calculator, levy schedule editor, per-lot breakdown view

### Stage 2 — Core Management (Sprints 3-4)
- **Sprint 3 Backend:** Maintenance system — work_orders table, contractors table, quote_requests, approval workflow (committee vote threshold), job status tracking
- **Sprint 3 Frontend:** Maintenance board (Kanban), work order form, contractor directory, approval voting UI
- **Sprint 4 Backend:** AI meeting assistant — agenda generator from open issues/maintenance/levies, minute-taking from voice upload (Groq Whisper), action item extraction, motion tracking
- **Sprint 4 Frontend:** Meeting scheduler, agenda builder, voice upload, AI-generated minutes editor, motion voting

### Stage 3 — Communications (Sprints 5-6)
- **Sprint 5 Backend:** Owner communications — notice_board posts, announcements, document sharing (bylaws, insurance, financials), owner portal with read receipts
- **Sprint 5 Frontend:** Notice board, announcement composer, document library, owner portal (public, token-authenticated)
- **Sprint 6 Backend:** AI communication drafts — generate AGM notices, levy notices, maintenance updates, bylaw reminders from templates + scheme data. State-specific compliance wording
- **Sprint 6 Frontend:** Template picker, AI draft editor, preview, send via email/SMS

### Stage 4 — Compliance (Sprints 7-9)
- **Sprint 7 Backend:** State compliance engine — compliance_requirements per state (NSW: Strata Schemes Management Act 2015, VIC: Owners Corporations Act 2006, QLD: Body Corporate and Community Management Act 1997), due dates, auto-reminders
- **Sprint 7 Frontend:** Compliance dashboard per state, due date calendar, overdue alerts
- **Sprint 8 Backend:** Insurance tracking — policies table, renewal dates, sum insured vs replacement value, premium history, broker contacts
- **Sprint 8 Frontend:** Insurance overview, renewal reminders, policy document upload
- **Sprint 9 Backend:** Financial reporting — income/expense reports, budget vs actual, reserve fund projections, auditor export (CSV/PDF)
- **Sprint 9 Frontend:** Financial dashboard (Recharts), report generator, auditor export

### Stage 5 — Revenue (Sprints 10-12)
- **Sprint 10 Backend:** Multi-scheme management — portfolio view, cross-scheme search, bulk operations, scheme comparison analytics
- **Sprint 10 Frontend:** Portfolio dashboard, scheme switcher, bulk levy generation
- **Sprint 11 Backend:** Stripe billing — per-lot pricing tiers, scheme onboarding checkout, usage metering
- **Sprint 11 Frontend:** Pricing page, checkout, billing portal
- **Sprint 12 Backend:** API for integrations — accounting software sync (Xero/MYOB), contractor platforms, insurance brokers
- **Sprint 12 Frontend:** Integration settings, API key management, Xero connect

### Stage 6 — Scale (Sprints 13-14)
- **Sprint 13 Backend:** Owner self-service — owners view their levies, submit maintenance requests, vote on motions, access documents. No strata manager needed for basic queries
- **Sprint 13 Frontend:** Owner mobile-first portal, levy statement, maintenance request form
- **Sprint 14:** Landing page, pricing, feature tour, onboarding demo, SEO content

## Key Contract Types

```typescript
export interface StrataScheme {
  id: string; org_id: string;
  name: string; address: string;
  state: 'NSW' | 'VIC' | 'QLD' | 'SA' | 'WA' | 'TAS' | 'NT' | 'ACT';
  lot_count: number; plan_number: string;
  legislation: string;
  created_at: string;
}

export interface Lot {
  id: string; scheme_id: string;
  lot_number: string; unit_entitlement: number;
  owner_name: string; owner_email: string | null;
  is_owner_occupied: boolean;
}

export interface LevySchedule {
  id: string; scheme_id: string;
  financial_year: string;
  admin_fund_total_cents: number;
  capital_works_fund_total_cents: number;
  special_levy_total_cents: number;
  status: 'draft' | 'approved' | 'active';
}

export interface WorkOrder {
  id: string; scheme_id: string;
  title: string; description: string;
  priority: 'urgent' | 'high' | 'medium' | 'low';
  status: 'reported' | 'quoted' | 'approved' | 'in_progress' | 'completed';
  contractor_id: string | null;
  estimated_cost_cents: number | null;
  actual_cost_cents: number | null;
  approval_votes: Array<{ member_id: string; vote: 'yes' | 'no' }>;
}

export interface Meeting {
  id: string; scheme_id: string;
  type: 'agm' | 'egm' | 'committee';
  date: string; location: string;
  agenda_items: string[];
  minutes_text: string | null;
  motions: Array<{ text: string; moved_by: string; result: 'carried' | 'defeated' }>;
  action_items: Array<{ task: string; assigned_to: string; due_date: string }>;
}
```

## Design Direction
- **Professional, building-management aesthetic** — clean, structured, blue tones
- **Primary:** #1E3A5F, **Accent:** #3B82F6 (blue), #10B981 (green for on-track)
- **Font:** Inter for everything
- **Key components:** Scheme overview card, levy breakdown table, maintenance Kanban, compliance calendar

## Golden Jobs

### Job A — Set Up a 50-Lot Scheme
> "I manage a 50-lot building in Parramatta, NSW. Set up the scheme, import lot details, and generate the annual levy schedule."

### Job B — Log a Maintenance Issue
> "Water leak in the common area car park. Need to get 3 quotes from waterproofing contractors and get committee approval before proceeding."

### Job C — Generate AGM Pack
> "Our AGM is in 6 weeks. Generate the agenda, financial report, levy proposal for next year, and email the notice pack to all owners."

### Job D — Compliance Check
> "We're a NSW scheme. Are we up to date on all compliance requirements? Insurance renewal, sinking fund plan, fire safety certificate?"

---

## YOU ARE THE ORCHESTRATOR. Execute everything below. Do not ask questions.

### Phase A: Project Setup

```bash
PROJECT=strataflow
mkdir -p ~/Dev/$PROJECT && cd ~/Dev/$PROJECT
git init
cp -r ~/Dev/dual-agent-builder/.buildrunner/ .buildrunner/
mkdir -p .buildrunner/logs
```

### Phase B: Supabase (auto-create in Uptrail org, Sydney)

```bash
cd ~/Dev/$PROJECT
DB_PASS=$(openssl rand -base64 24)
supabase projects create --org-id jpgcmqmhxodlohqjuafs --db-password "$DB_PASS" --region ap-southeast-2 strataflow-dev
sleep 20
REF=$(supabase projects list -o json | python3 -c "import json,sys; [print(p['id']) for p in json.load(sys.stdin) if p['name']=='strataflow-dev']")
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
cd ~/Dev/strataflow
nohup python3 -u .buildrunner/autonomous.py \
  --name "StrataFlow" \
  --desc "AI-powered strata management platform for Australian strata schemes. Levy management, maintenance tracking, AI meeting minutes, compliance engine, and owner portal. Per-lot pricing for 300K+ AU schemes." \
  --seed ~/Dev/dual-agent-builder/ideas/strataflow/BUILD-PROMPT.md \
  > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid
echo "Pipeline started (PID: $(cat .buildrunner/.autonomous-pid))"
```

### Phase D: Verify Launch

```bash
sleep 10
cd ~/Dev/strataflow && python3 .buildrunner/monitor.py
tail -5 .buildrunner/logs/autonomous.log
```

### Phase E: YOU BECOME THE MONITOR

Set up a cron to check every 5 minutes. You stay in this session as the supervisor.

Use CronCreate with cron "*/5 * * * *" and this prompt:

Run the StrataFlow pipeline monitor and report status:
```bash
cd ~/Dev/strataflow && python3 .buildrunner/monitor.py 2>&1
```
Also check the last 5 lines of the autonomous log:
```bash
tail -5 ~/Dev/strataflow/.buildrunner/logs/autonomous.log 2>/dev/null
```
If status is DEAD, restart immediately:
```bash
cd ~/Dev/strataflow && nohup python3 -u .buildrunner/autonomous.py --resume > .buildrunner/logs/autonomous.log 2>&1 & echo $! > .buildrunner/.autonomous-pid
```
If STUCK (>45 min), kill and restart:
```bash
kill $(cat ~/Dev/strataflow/.buildrunner/.autonomous-pid) 2>/dev/null; sleep 5; cd ~/Dev/strataflow && nohup python3 -u .buildrunner/autonomous.py --resume > .buildrunner/logs/autonomous.log 2>&1 & echo $! > .buildrunner/.autonomous-pid
```
If RUNNING, give a one-line summary. If COMPLETE, report final status and stop the cron.

After setting up the cron, confirm: "Monitoring active. StrataFlow pipeline running. Checking every 5 minutes."

### What happens (no action needed)
- **Phase 1 (6-9 hours):** Codex runs 12 planning passes
- **Phase 2 (4-8 hours):** Codex backend + Claude frontend, 14 sprints, 5-pass design iteration
- **You** check every 5 min, auto-restart if dead, kill+restart if stuck
