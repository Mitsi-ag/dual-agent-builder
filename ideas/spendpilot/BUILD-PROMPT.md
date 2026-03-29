# SpendPilot — Ramp for Australia

> Ramp hit $32B valuation and $1B ARR. Australia's 2.5M SMBs still track expenses on spreadsheets.
>
> **Score:** 19/25 | **Market:** $500M-1B | **Price:** $15-30/user/mo | **80% SMBs still manual**
>
> Paste this → write planning docs → run the builder → monitor.

---

## The Opportunity

Ramp grew from zero to $1B ARR in 5 years building AI expense management. Brex sold for $5.15B. In Australia: Cape (beta), Weel (tiny), and 2.5M SMBs still tracking expenses on spreadsheets and shoebox receipts. The Xero ecosystem is dominant — any solution MUST integrate. 500 companies at $200/mo avg = $1.2M ARR. Long-term: interchange on card spend adds $1.5-2.5M.

## Tech Stack
Next.js 15, TypeScript, Tailwind v4, Supabase, Vercel, Stripe, Resend, Xero API

## 14 Sprints / 7 Stages

### Stage 1 — Foundation (Sprints 1-2)
- **Sprint 1 Backend:** Auth, companies table, users (role: admin/approver/submitter), expense_policies table (per-category limits, approval thresholds)
- **Sprint 1 Frontend:** Login, signup, company onboarding (ABN, team size, Xero connected Y/N)
- **Sprint 2 Backend:** Expense submission — expenses table (amount_cents, category, merchant, receipt_url, status), receipt OCR via Claude Vision (extract merchant, amount, date, GST), duplicate detection
- **Sprint 2 Frontend:** Expense submission form, receipt photo capture (mobile camera), OCR result editor, expense list

### Stage 2 — Smart Processing (Sprints 3-4)
- **Sprint 3 Backend:** AI categorisation — auto-categorise expenses by merchant + description, learn from corrections, map to Xero chart of accounts, GST detection (10% extraction from receipt)
- **Sprint 3 Frontend:** Category picker with AI suggestion, GST toggle, category correction feedback
- **Sprint 4 Backend:** Approval workflow — approval_rules table (threshold-based: <$100 auto, $100-500 manager, >$500 finance), approval chain, policy violation flags, auto-approve for compliant expenses
- **Sprint 4 Frontend:** Approval queue, approve/reject with notes, policy violation banner, bulk approve

### Stage 3 — Reporting (Sprints 5-6)
- **Sprint 5 Backend:** Expense reports — report periods, per-employee totals, per-category breakdown, GST summary (BAS-ready), export CSV/PDF, reimbursement tracking
- **Sprint 5 Frontend:** Report builder (date range, filters), visualisations (Recharts), PDF preview, BAS summary view
- **Sprint 6 Backend:** Xero integration — OAuth2 connect, sync expenses as bills/spend money transactions, map categories to Xero accounts, reconciliation status
- **Sprint 6 Frontend:** Xero connect flow, account mapping UI, sync status, reconciliation dashboard

### Stage 4 — Budgets & Alerts (Sprints 7-9)
- **Sprint 7 Backend:** Budget management — budgets table (per-team, per-category, per-project), budget vs actual tracking, forecast based on spend velocity
- **Sprint 7 Frontend:** Budget dashboard, budget cards with progress bars, forecast charts
- **Sprint 8 Backend:** Alerts & notifications — budget threshold alerts (50/80/100%), policy violations, missing receipts, overdue approvals. Email + Slack delivery
- **Sprint 8 Frontend:** Alert preferences, notification center, Slack integration setup
- **Sprint 9 Backend:** Team management — teams table, department-based permissions, per-team spend limits, team comparison analytics
- **Sprint 9 Frontend:** Team management, invite flow, team spend overview

### Stage 5 — Revenue (Sprints 10-12)
- **Sprint 10 Backend:** AI insights — spending anomalies, duplicate subscription detection, cost-saving recommendations, month-over-month trends with AI commentary
- **Sprint 10 Frontend:** Insights dashboard, anomaly cards, subscription tracker, savings opportunities
- **Sprint 11 Backend:** Stripe billing — Free (5 users, 50 expenses/mo), Pro ($15/user/mo, unlimited), Business ($30/user/mo, Xero sync + insights + API)
- **Sprint 11 Frontend:** Pricing page, checkout, billing portal, usage limits enforcement
- **Sprint 12 Backend:** API + webhooks — REST API for expense submission, approval status, reports. Webhook events for new expenses, approvals, policy violations
- **Sprint 12 Frontend:** API docs, API key management, webhook setup

### Stage 6 — Scale (Sprints 13-14)
- **Sprint 13 Backend:** MYOB integration (alongside Xero), multi-currency support (AUD primary, USD/GBP for international expenses), tax receipt compliance (ATO requirements)
- **Sprint 13 Frontend:** Accounting software switcher, currency display, tax compliance checklist
- **Sprint 14:** Landing page, pricing, feature comparison vs Ramp/Brex, AU-specific positioning, onboarding demo

## Key Contract Types

```typescript
export interface Expense {
  id: string; company_id: string; user_id: string;
  amount_cents: number; gst_cents: number;
  currency: 'AUD' | 'USD' | 'GBP';
  merchant: string; description: string;
  category: string; category_confidence: number;
  receipt_url: string | null;
  receipt_ocr: ReceiptOCR | null;
  status: 'draft' | 'submitted' | 'approved' | 'rejected' | 'reimbursed';
  policy_violations: string[];
  approved_by: string | null;
  xero_transaction_id: string | null;
  created_at: string;
}

export interface ReceiptOCR {
  merchant: string; amount_cents: number;
  date: string; gst_cents: number;
  confidence: number;
  raw_text: string;
}

export interface ApprovalRule {
  id: string; company_id: string;
  min_amount_cents: number;
  max_amount_cents: number | null;
  approver_role: 'auto' | 'manager' | 'finance' | 'ceo';
  category: string | null;
}

export interface Budget {
  id: string; company_id: string;
  name: string;
  scope: 'company' | 'team' | 'category' | 'project';
  scope_id: string | null;
  amount_cents: number;
  period: 'monthly' | 'quarterly' | 'yearly';
  spent_cents: number;
}

export interface XeroConnection {
  id: string; company_id: string;
  tenant_id: string;
  access_token_encrypted: string;
  refresh_token_encrypted: string;
  account_mappings: Record<string, string>;
  last_sync_at: string | null;
}
```

## Design Direction
- **Finance-app clean** — Ramp/Mercury aesthetic, light mode default, precise data presentation
- **Primary:** #111827, **Accent:** #6366F1 (indigo), #10B981 (green = under budget), #EF4444 (red = over)
- **Font:** Inter, tabular-nums on ALL numbers
- **Key components:** Expense card with receipt thumbnail, approval queue, budget gauge, BAS summary

## Golden Jobs

### Job A — Submit a Receipt
> "Just had lunch with a client, $85.50 at Cafe Sydney. Take a photo of the receipt and submit it for approval."

### Job B — Approve a Batch
> "I'm the finance manager. Show me all pending expenses over $100 that need my approval this week."

### Job C — BAS Quarter Report
> "It's end of quarter. Generate a GST summary showing total GST paid on expenses, broken down by category, ready for my BAS lodgement."

### Job D — Xero Reconciliation
> "Sync all approved expenses from March to Xero. Map them to the correct accounts. Show me what reconciled and what didn't."
