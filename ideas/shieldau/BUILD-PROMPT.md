# ShieldAU — Essential Eight Compliance for Australian SMBs

> "Vanta is worth $4.15B. They don't understand Essential Eight. That's your opening."
>
> **Score:** 20/25 | **Market:** $500M | **Price:** $199-499/mo | **AU Competitors in SME tier:** ZERO
>
> Paste this into Claude Code → write planning docs → run the builder → monitor.

---

## The Opportunity

Vanta ($504M raised), Drata ($328M), Secureframe ($102M) — all automate compliance for US frameworks (SOC 2, ISO 27001). None of them understand ASD Essential Eight, APRA CPS 234, or the Privacy Act. The $99-$499/mo SME tier in Australia is **completely empty**. Government suppliers are MANDATED to comply. 200 SMBs at $300/mo = $720K ARR.

## Tech Stack
Next.js 15, TypeScript, Tailwind v4, Supabase, Vercel, Stripe, Resend

## Planning Docs to Create

### PRODUCT.md
- AI-powered Essential Eight maturity assessment
- Automated evidence collection (screenshots, logs, config scans)
- Gap analysis with prioritised remediation steps
- Compliance dashboard with real-time maturity scores (0-3 per control)
- PDF compliance reports (auditor-ready)
- Continuous monitoring with drift alerts

### Key Decisions (DECISIONS.md)
- D001: Essential Eight first, add CPS 234 + Privacy Act later
- D002: Self-assessment first (no agent/scanner) — faster to ship
- D003: Maturity model 0-3 per ASD spec, not custom scoring
- D004: Evidence = uploaded screenshots + manual attestation (V1), automated scanning (V2)
- D005: PDF report is the product (like QuoteFast — the deliverable is what customers show auditors)
- D006: Freemium — free assessment, paid for monitoring + reports + evidence vault
- D007: Per-org pricing, not per-user (SMBs hate per-seat)

## 14 Sprints / 7 Stages

### Stage 0 (Sprint 0): Validation
Validate with 10 SMBs who are government suppliers or APRA-regulated

### Stage 1 — Foundation (Sprints 1-2)
- **Sprint 1 Backend:** Next.js scaffold, Supabase auth, organizations table, essential_eight_controls table (8 controls × 4 maturity levels = 32 requirements), assessment_responses table
- **Sprint 1 Frontend:** Login, signup, org onboarding (industry, size, government supplier Y/N)
- **Sprint 2 Backend:** Assessment engine — 8 controls with maturity-level questions, scoring algorithm (control_score = min maturity level achieved across all requirements)
- **Sprint 2 Frontend:** Assessment wizard — step-by-step questionnaire for each control, progress bar, save & resume

### Stage 2 — Core Assessment (Sprints 3-4)
- **Sprint 3 Backend:** Maturity scoring — calculate overall maturity per control (0-3), gap analysis (what's needed for next level), remediation priorities (effort vs impact matrix)
- **Sprint 3 Frontend:** Results dashboard — 8-control radar chart, maturity heatmap, gap list with severity badges
- **Sprint 4 Backend:** Evidence vault — file upload (screenshots, configs, policies), evidence linking to controls, evidence expiry tracking
- **Sprint 4 Frontend:** Evidence upload per control, evidence timeline, missing evidence alerts

### Stage 3 — Reports (Sprints 5-6)
- **Sprint 5 Backend:** PDF report generator — executive summary, control-by-control breakdown, gap analysis, remediation roadmap, evidence references. Auditor-ready format
- **Sprint 5 Frontend:** Report preview, customisation (logo, cover page text), download/share
- **Sprint 6 Backend:** Remediation task system — auto-generated tasks from gaps, assignment, due dates, completion tracking
- **Sprint 6 Frontend:** Remediation board (Kanban), task detail with linked control, progress tracking

### Stage 4 — Monitoring (Sprints 7-9)
- **Sprint 7 Backend:** Continuous monitoring — scheduled re-assessment reminders, evidence expiry alerts, maturity drift detection
- **Sprint 7 Frontend:** Monitoring dashboard — compliance timeline, drift alerts, upcoming deadlines
- **Sprint 8 Backend:** Alert system — email (Resend) + Slack for: evidence expiring, maturity regression, assessment due, new ASD guidance
- **Sprint 8 Frontend:** Alert preferences, notification center, Slack integration setup
- **Sprint 9 Backend:** Multi-framework readiness — data model supports CPS 234, ISM, Privacy Act (future). Framework selector in assessment
- **Sprint 9 Frontend:** Framework comparison view (if assessed against multiple)

### Stage 5 — Revenue (Sprints 10-12)
- **Sprint 10 Backend:** Team management — invite users, role-based access (admin/assessor/viewer), audit log of all changes
- **Sprint 10 Frontend:** Team settings, invite flow, role management, audit log viewer
- **Sprint 11 Backend:** Stripe billing — Free (1 assessment), Pro ($199/mo — monitoring + reports + evidence vault), Enterprise ($499/mo — multi-framework + API + SSO)
- **Sprint 11 Frontend:** Pricing page, checkout, billing portal, usage limits
- **Sprint 12 Backend:** API — REST endpoints for assessment status, maturity scores, evidence upload. Webhook events for compliance changes
- **Sprint 12 Frontend:** API docs page, API key management, webhook configuration

### Stage 6 — Scale (Sprints 13-14)
- **Sprint 13 Backend:** Trust center — public compliance page (shareable URL showing maturity status), embeddable badge
- **Sprint 13 Frontend:** Trust center builder, public page preview, badge generator
- **Sprint 14 Backend:** Landing page API (testimonials, stats)
- **Sprint 14 Frontend:** Marketing site — hero, problem/solution, pricing, Essential Eight explainer, trust badges, CTA

## Key Contract Types

```typescript
export interface Organization {
  id: string;
  name: string;
  industry: string;
  employee_count: string;
  is_government_supplier: boolean;
  plan: 'free' | 'pro' | 'enterprise';
  created_at: string;
}

export interface EssentialEightControl {
  id: string;
  control_number: number; // 1-8
  name: string; // "Application Control", "Patch Applications", etc.
  description: string;
  maturity_levels: MaturityLevel[];
}

export interface MaturityLevel {
  level: 0 | 1 | 2 | 3;
  requirements: string[];
}

export interface AssessmentResponse {
  id: string;
  org_id: string;
  control_number: number;
  maturity_level: number;
  requirement_index: number;
  answer: 'yes' | 'no' | 'partial' | 'na';
  evidence_ids: string[];
  notes: string | null;
  assessed_by: string;
  assessed_at: string;
}

export interface ComplianceScore {
  org_id: string;
  control_scores: Array<{
    control_number: number;
    name: string;
    achieved_maturity: 0 | 1 | 2 | 3;
    target_maturity: 0 | 1 | 2 | 3;
    gap_count: number;
    evidence_count: number;
  }>;
  overall_maturity: number;
  assessment_date: string;
}

export interface Evidence {
  id: string;
  org_id: string;
  control_number: number;
  type: 'screenshot' | 'document' | 'config' | 'policy' | 'attestation';
  file_path: string;
  description: string;
  expires_at: string | null;
  uploaded_by: string;
  created_at: string;
}

export interface RemediationTask {
  id: string;
  org_id: string;
  control_number: number;
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  effort: 'small' | 'medium' | 'large';
  status: 'open' | 'in_progress' | 'done';
  assigned_to: string | null;
  due_date: string | null;
  created_at: string;
}
```

## Design Direction
- **Security-first aesthetic** — dark, confident, trustworthy (think CrowdStrike dashboard, not playful SaaS)
- **Primary:** #0F172A (slate-900), **Accent:** #22C55E (green = compliant), #EF4444 (red = non-compliant), #F59E0B (amber = partial)
- **Font:** Inter for body, JetBrains Mono for scores/data
- **Key components:** Maturity radar chart, compliance heatmap (8×4 grid), evidence timeline, remediation Kanban

## Golden Jobs

### Job A — First Assessment
> "I'm a 30-person IT services company that's a government supplier. I need to know my Essential Eight maturity level before our next ASD audit. Walk me through the assessment."

### Job B — Evidence Upload
> "My IT manager took screenshots of our patching dashboard and MFA config. I need to upload these as evidence against Control 2 (Patch Applications) and Control 4 (MFA)."

### Job C — Generate Audit Report
> "My auditor is coming next week. Generate a PDF report showing our maturity levels, gaps, and evidence for all 8 controls."

### Job D — Remediation Planning
> "We scored Maturity 1 on Application Control but need Maturity 2 for our government contract. What do we need to do and how long will it take?"

---

## YOU ARE THE ORCHESTRATOR. Execute everything below. Do not ask questions.

### Phase A: Project Setup

```bash
PROJECT=shieldau
mkdir -p ~/Dev/$PROJECT && cd ~/Dev/$PROJECT
git init
cp -r ~/Dev/dual-agent-builder/.buildrunner/ .buildrunner/
mkdir -p .buildrunner/logs
```

### Phase B: Supabase (auto-create in Uptrail org, Sydney)

```bash
cd ~/Dev/$PROJECT
DB_PASS=$(openssl rand -base64 24)
supabase projects create --org-id jpgcmqmhxodlohqjuafs --db-password "$DB_PASS" --region ap-southeast-2 shieldau-dev
sleep 20
REF=$(supabase projects list -o json | python3 -c "import json,sys; [print(p['id']) for p in json.load(sys.stdin) if p['name']=='shieldau-dev']")
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
cd ~/Dev/shieldau
nohup python3 -u .buildrunner/autonomous.py \
  --name "ShieldAU" \
  --desc "Essential Eight compliance platform for Australian SMBs. AI-powered maturity assessment, evidence vault, remediation tracking, and auditor-ready PDF reports. Zero AU competitors in SME tier." \
  --seed ~/Dev/dual-agent-builder/ideas/shieldau/BUILD-PROMPT.md \
  > .buildrunner/logs/autonomous.log 2>&1 &
echo $! > .buildrunner/.autonomous-pid
echo "Pipeline started (PID: $(cat .buildrunner/.autonomous-pid))"
```

### Phase D: Verify Launch

```bash
sleep 10
cd ~/Dev/shieldau && python3 .buildrunner/monitor.py
tail -5 .buildrunner/logs/autonomous.log
```

### Phase E: YOU BECOME THE MONITOR

Set up a cron to check every 5 minutes. You stay in this session as the supervisor.

Use CronCreate with cron "*/5 * * * *" and this prompt:

Run the ShieldAU pipeline monitor and report status:
```bash
cd ~/Dev/shieldau && python3 .buildrunner/monitor.py 2>&1
```
Also check the last 5 lines of the autonomous log:
```bash
tail -5 ~/Dev/shieldau/.buildrunner/logs/autonomous.log 2>/dev/null
```
If status is DEAD, restart immediately:
```bash
cd ~/Dev/shieldau && nohup python3 -u .buildrunner/autonomous.py --resume > .buildrunner/logs/autonomous.log 2>&1 & echo $! > .buildrunner/.autonomous-pid
```
If STUCK (>45 min), kill and restart:
```bash
kill $(cat ~/Dev/shieldau/.buildrunner/.autonomous-pid) 2>/dev/null; sleep 5; cd ~/Dev/shieldau && nohup python3 -u .buildrunner/autonomous.py --resume > .buildrunner/logs/autonomous.log 2>&1 & echo $! > .buildrunner/.autonomous-pid
```
If RUNNING, give a one-line summary. If COMPLETE, report final status and stop the cron.

After setting up the cron, confirm: "Monitoring active. ShieldAU pipeline running. Checking every 5 minutes."

### What happens (no action needed)
- **Phase 1 (6-9 hours):** Codex runs 12 planning passes
- **Phase 2 (4-8 hours):** Codex backend + Claude frontend, 14 sprints, 5-pass design iteration
- **You** check every 5 min, auto-restart if dead, kill+restart if stuck
