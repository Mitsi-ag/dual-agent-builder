# BriefMate — AI Legal Assistant for Australian Law Firms

> Australia's legal tech market is $8B. Most firms still research manually on AustLII.
>
> **Market:** $8B | **Price:** $49-200/mo | **Self-serve law firms**
>
> Paste this → write planning docs → run the builder → monitor.

---

## The Opportunity

Australian law firms spend 30-40% of billable hours on legal research, document drafting, and precedent searching. AustLII (free) is comprehensive but unsearchable by AI. LexisNexis ($$$) is expensive and enterprise-only. The $49-200/mo tier for small-to-mid firms (5-50 lawyers) is underserved. AI can draft legal memos, find relevant precedents, and summarise legislation in seconds. 300 firms at $150/mo = $540K ARR.

## Tech Stack
Next.js 15, TypeScript, Tailwind v4, Supabase, Vercel, Stripe, Resend, Claude API (Opus for legal reasoning)

## 14 Sprints / 7 Stages

### Stage 1 — Foundation (Sprints 1-2)
- **Sprint 1 Backend:** Auth, firms table, users (role: partner/associate/paralegal), matters table (client, matter type, status), chat_sessions per matter
- **Sprint 1 Frontend:** Login, signup, firm onboarding (practice areas, size, state), matter list
- **Sprint 2 Backend:** AI legal chat — Claude API with legal system prompt (AU jurisdiction, cite format, disclaimer), conversation history per matter, context injection (matter details, uploaded docs)
- **Sprint 2 Frontend:** Chat interface per matter, message history, new conversation, matter context sidebar

### Stage 2 — Legal Research (Sprints 3-4)
- **Sprint 3 Backend:** Document upload & analysis — upload contracts/briefs/judgments (PDF), Claude extracts: parties, dates, key terms, obligations, risks. Store as structured data
- **Sprint 3 Frontend:** Document upload (drag & drop), AI analysis results, document library per matter
- **Sprint 4 Backend:** Legal memo generator — input: question + jurisdiction + practice area. Output: structured memo (issue, rule, application, conclusion — IRAC format), with cited legislation and case references
- **Sprint 4 Frontend:** Memo request form, AI-generated memo editor (rich text), export PDF

### Stage 3 — Document Drafting (Sprints 5-6)
- **Sprint 5 Backend:** Contract clause library — pre-built clauses per practice area (commercial, property, employment), AI-generated clause variations, clause comparison
- **Sprint 5 Frontend:** Clause browser, clause editor, insert-into-document, clause comparison side-by-side
- **Sprint 6 Backend:** Document templates — letter of advice, demand letter, affidavit, contract, NDA. AI fills template from matter data + user prompts. Version tracking
- **Sprint 6 Frontend:** Template picker, AI-filled preview, inline editing, version history

### Stage 4 — Matter Management (Sprints 7-9)
- **Sprint 7 Backend:** Time tracking — time_entries per matter, AI auto-categorises time (research, drafting, correspondence, court), suggested time from chat/document activity
- **Sprint 7 Frontend:** Time entry, timer, AI-suggested time, time summary per matter
- **Sprint 8 Backend:** Deadline tracking — court dates, limitation periods, filing deadlines per state. Auto-calculated from matter creation date + matter type. Alert system
- **Sprint 8 Frontend:** Deadline calendar, upcoming deadlines dashboard, overdue alerts
- **Sprint 9 Backend:** Client communications — email drafts from matter context, correspondence log, client portal (read-only matter status)
- **Sprint 9 Frontend:** Email composer with AI drafts, correspondence timeline, client portal

### Stage 5 — Revenue (Sprints 10-12)
- **Sprint 10 Backend:** Team features — per-lawyer activity, matter assignment, workload view, knowledge sharing (memos accessible to team)
- **Sprint 10 Frontend:** Team dashboard, workload chart, knowledge base search
- **Sprint 11 Backend:** Stripe billing — Solo ($49/mo, 1 user, 50 AI queries), Firm ($99/mo, 5 users, unlimited), Practice ($200/mo, unlimited + API + templates)
- **Sprint 11 Frontend:** Pricing page, checkout, billing portal
- **Sprint 12 Backend:** API + integrations — LEAP, Clio, Smokeball integration prep (AU practice management systems), webhook events
- **Sprint 12 Frontend:** Integration settings, API docs

### Stage 6 — Scale (Sprints 13-14)
- **Sprint 13 Backend:** Precedent database — firm-specific precedent search across all matters/memos, AI-powered similarity matching, most-cited internal documents
- **Sprint 13 Frontend:** Precedent search, related matters, citation network
- **Sprint 14:** Landing page, practice-area-specific demos, pricing, compliance/security page, onboarding

## Key Contract Types

```typescript
export interface Matter {
  id: string; firm_id: string;
  matter_number: string;
  client_name: string;
  matter_type: 'commercial' | 'property' | 'employment' | 'litigation' | 'family' | 'criminal' | 'planning';
  jurisdiction: 'NSW' | 'VIC' | 'QLD' | 'SA' | 'WA' | 'TAS' | 'NT' | 'ACT' | 'federal';
  status: 'active' | 'on_hold' | 'closed' | 'archived';
  assigned_to: string[];
  created_at: string;
}

export interface LegalMemo {
  id: string; matter_id: string;
  question: string;
  memo_html: string;
  citations: Citation[];
  practice_area: string;
  jurisdiction: string;
  created_by: string;
  created_at: string;
}

export interface Citation {
  type: 'legislation' | 'case' | 'regulation' | 'commentary';
  title: string;
  reference: string; // e.g. "[2024] HCA 12" or "Corporations Act 2001 (Cth) s 180"
  relevance: string;
  url: string | null;
}

export interface Document {
  id: string; matter_id: string;
  name: string; type: 'contract' | 'brief' | 'judgment' | 'letter' | 'affidavit' | 'memo' | 'other';
  file_path: string;
  ai_analysis: DocumentAnalysis | null;
  version: number;
  created_at: string;
}

export interface DocumentAnalysis {
  parties: string[];
  date: string | null;
  key_terms: string[];
  obligations: Array<{ party: string; obligation: string }>;
  risks: Array<{ description: string; severity: 'high' | 'medium' | 'low' }>;
  summary: string;
}

export interface TimeEntry {
  id: string; matter_id: string; user_id: string;
  duration_minutes: number;
  category: 'research' | 'drafting' | 'correspondence' | 'court' | 'meeting' | 'admin';
  description: string;
  is_ai_suggested: boolean;
  date: string;
}
```

## Design Direction
- **Professional, law-firm appropriate** — clean, authoritative, not techy
- **Primary:** #1C1917 (stone-900), **Accent:** #7C3AED (violet for AI features), #059669 (green for safe)
- **Font:** Merriweather for headings (serif = authority), Inter for body
- **Key components:** Chat panel, memo editor, citation card with badge, deadline calendar

## Golden Jobs

### Job A — Legal Research Question
> "Does a company director owe a duty of care to individual creditors under Australian law? I need a memo with relevant High Court cases."

### Job B — Contract Review
> "Upload this commercial lease agreement. Identify the key obligations, unusual clauses, and any risks for the tenant."

### Job C — Draft a Letter of Advice
> "Draft a letter of advice to our client about their options for unfair dismissal under the Fair Work Act. They were dismissed after 2 years with no written warning."

### Job D — Find Precedents
> "Find any memos or documents in our firm's history related to director's duties or insolvent trading."

---

## YOU ARE THE ORCHESTRATOR. Execute everything below. Do not ask questions.

### Phase A: Project Setup

```bash
PROJECT=briefmate
mkdir -p ~/Dev/$PROJECT && cd ~/Dev/$PROJECT
git init
cp -r ~/Dev/dual-agent-builder/.buildrunner/ .buildrunner/
mkdir -p .buildrunner/logs
```

### Phase B: Supabase (auto-create in Uptrail org, Sydney)

```bash
cd ~/Dev/$PROJECT
DB_PASS=$(openssl rand -base64 24)
supabase projects create --org-id jpgcmqmhxodlohqjuafs --db-password "$DB_PASS" --region ap-southeast-2 briefmate-dev
sleep 20
REF=$(supabase projects list -o json | python3 -c "import json,sys; [print(p['id']) for p in json.load(sys.stdin) if p['name']=='briefmate-dev']")
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
cd ~/Dev/briefmate
nohup python3 -u .buildrunner/autonomous.py \
  --name "BriefMate" \
  --desc "AI legal assistant for Australian law firms. Legal research chat, document analysis, memo generation (IRAC format), contract clause library, time tracking, and deadline management. Claude API for legal reasoning." \
  --seed ~/Dev/dual-agent-builder/ideas/briefmate/BUILD-PROMPT.md \
  > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid
echo "Pipeline started (PID: $(cat .buildrunner/.autonomous-pid))"
```

### Phase D: Verify Launch

```bash
sleep 10
cd ~/Dev/briefmate && python3 .buildrunner/monitor.py
tail -5 .buildrunner/logs/autonomous.log
```

### Phase E: YOU BECOME THE MONITOR

Set up a cron to check every 5 minutes. You stay in this session as the supervisor.

Use CronCreate with cron "*/5 * * * *" and this prompt:

Run the BriefMate pipeline monitor and report status:
```bash
cd ~/Dev/briefmate && python3 .buildrunner/monitor.py 2>&1
```
Also check the last 5 lines of the autonomous log:
```bash
tail -5 ~/Dev/briefmate/.buildrunner/logs/autonomous.log 2>/dev/null
```
If status is DEAD, restart immediately:
```bash
cd ~/Dev/briefmate && nohup python3 -u .buildrunner/autonomous.py --resume > .buildrunner/logs/autonomous.log 2>&1 & echo $! > .buildrunner/.autonomous-pid
```
If STUCK (>45 min), kill and restart:
```bash
kill $(cat ~/Dev/briefmate/.buildrunner/.autonomous-pid) 2>/dev/null; sleep 5; cd ~/Dev/briefmate && nohup python3 -u .buildrunner/autonomous.py --resume > .buildrunner/logs/autonomous.log 2>&1 & echo $! > .buildrunner/.autonomous-pid
```
If RUNNING, give a one-line summary. If COMPLETE, report final status and stop the cron.

After setting up the cron, confirm: "Monitoring active. BriefMate pipeline running. Checking every 5 minutes."

### What happens (no action needed)
- **Phase 1 (6-9 hours):** Codex runs 12 planning passes
- **Phase 2 (4-8 hours):** Codex backend + Claude frontend, 14 sprints, 5-pass design iteration
- **You** check every 5 min, auto-restart if dead, kill+restart if stuck
