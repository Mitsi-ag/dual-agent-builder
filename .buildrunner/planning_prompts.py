"""
Planning phase prompts for autonomous research + documentation.

Each prompt is a deep-work brief for a 45-minute Codex session.
Prompts tell the agent to READ previous outputs and WRITE new files.
12 passes, cumulative — each builds on what came before.
"""

# ─── Pass 1: Market Intelligence ─────────────────────────────────────

MARKET_INTEL_PROMPT = """You are a world-class product strategist and market researcher.

You are planning a new SaaS product: {product_name} — {product_description}

{seed_section}

## Your Task

Conduct exhaustive market intelligence research. Write your findings to docs/research/MARKET-INTEL.md

Your research MUST cover ALL of these sections with SPECIFIC data points:

### 1. Market Sizing
- TAM, SAM, SOM with methodology and sources
- Growth rate and growth drivers
- Geographic specifics (Australia-first, then expansion potential)
- Revenue per customer benchmarks from analogous companies

### 2. Competitor Landscape (minimum 10 competitors)
For EACH competitor, document:
- Name, URL, country, founding year, funding raised
- Pricing model and price points
- Core features (list top 5)
- Strengths (what they do well)
- Weaknesses (where they fail)
- Customer reviews sentiment (positive and negative themes)

Also cover:
- Adjacent competitors who could pivot into this space
- Open source alternatives
- Market gaps — what NO existing player does

### 3. Regulatory Environment
- Relevant legislation with act names and section numbers
- Government mandates that create demand
- Compliance deadlines and enforcement actions
- Upcoming regulatory changes (next 24 months)
- Penalties for non-compliance

### 4. Customer Analysis
- 5 distinct buyer personas (title, company size, pain, budget)
- Pain points ranked by severity and frequency
- Current solutions each persona uses and why they fail
- Willingness to pay signals (what they pay for similar tools)
- Decision-making process: who evaluates, who approves, who pays
- Sales cycle length by company size

### 5. Pricing Intelligence
- Competitor pricing comparison table (feature × price matrix)
- Pricing model analysis (per-seat vs per-unit vs flat vs usage)
- Optimal entry price for fastest adoption
- Price anchoring strategy
- Expansion revenue playbook (how to grow ARPU over time)
- Free tier strategy: what to give away, what to gate

### 6. Distribution Channels
- How top 3 competitors acquire customers (ranked by effectiveness)
- Untapped channels specific to this market
- Partnership opportunities (integrations, resellers, consultancies)
- Community and content opportunities
- Conference and event calendar (next 12 months)

### 7. Timing Analysis
- Why NOW (3 specific tailwinds)
- Technology enablers (what's newly possible)
- Market headwinds (3 specific risks)
- 18-month window assessment: what must happen by when

### 8. Unit Economics Model
- Target CAC by channel
- Expected LTV at different price points
- Payback period targets
- Churn benchmarks from similar products
- Break-even customer count

Write this as a comprehensive research document with real names, real numbers, and real analysis. Do not use placeholder data. This document informs ALL subsequent planning decisions.

Create the file: docs/research/MARKET-INTEL.md
Also create directory: mkdir -p docs/research
"""

# ─── Pass 2: Product Definition ──────────────────────────────────────

PRODUCT_PROMPT = """You are a senior product manager defining a new SaaS product.

You are defining: {product_name} — {product_description}

## FIRST: Read these files from disk
1. docs/research/MARKET-INTEL.md — your market research

{seed_section}

## Your Task

Write a comprehensive PRODUCT.md that will serve as the north star for two AI agents building this product. Every feature, every decision, every priority must be crystal clear.

Your PRODUCT.md MUST include:

### Vision & Positioning
- One-sentence positioning statement
- 3-sentence elevator pitch
- How this is different from EVERY competitor (from market intel)
- The "10x better" claim — what specific thing is 10x better

### Target Customers (from market intel, refined)
- Primary persona (the person who BUYS)
- Secondary persona (the person who USES daily)
- Anti-persona (who this is NOT for)
- ICP definition with firmographic criteria

### Features — Full Specification
For EVERY feature, define:
- Feature name
- User story: "As a [persona], I want to [action] so that [outcome]"
- Acceptance criteria (testable conditions)
- Priority: P0 (must-have for launch), P1 (needed within 30 days), P2 (nice to have)
- Which sprint it belongs to (1-14)
- Dependencies on other features

### Pricing Strategy (from market intel)
- Tier names, prices, and feature breakdown
- What's in the free tier (must be valuable enough to attract, limited enough to convert)
- Upgrade triggers (what makes free users hit the paywall)
- Annual discount strategy

### Success Metrics
- North star metric
- Per-stage KPIs
- 30/60/90 day targets after launch
- Revenue milestones: $1K, $5K, $10K, $50K MRR

### Kill Signals
- 3 specific signals that mean "stop building, pivot"
- Timeframes for each signal
- Sunk cost threshold (max investment before kill decision)

### Competitive Moats (from market intel)
- What's defensible about this product
- Network effects (if any)
- Data advantages
- Switching costs you create

Write this as the definitive product document. Be extremely specific. No vague statements like "easy to use" — instead "onboarding completes in under 3 minutes with zero configuration."

Create the file: PRODUCT.md
"""

# ─── Pass 3: Key Decisions ───────────────────────────────────────────

DECISIONS_PROMPT = """You are a senior technical architect making foundational decisions for a new product.

You are deciding for: {product_name} — {product_description}

## FIRST: Read these files from disk
1. docs/research/MARKET-INTEL.md
2. PRODUCT.md

## Your Task

Write DECISIONS.md — a numbered decision log documenting every non-obvious technical and business decision. Each decision must have rationale and alternatives considered.

Format each decision as:

### D001: [Decision Title]
**Decision:** [What we're doing]
**Alternatives considered:**
1. [Option A] — [why rejected]
2. [Option B] — [why rejected]
**Rationale:** [Why this option wins, referencing market intel or product requirements]
**Implications:** [What this means for architecture, timeline, cost]
**Reversibility:** [Easy/Medium/Hard to change later]

You need MINIMUM 25 decisions covering:

**Technical Decisions (D001-D010)**
- Tech stack choices and why
- Database design philosophy (relational vs document, row-level security)
- Authentication approach
- API design (REST vs GraphQL, versioning)
- File storage approach
- AI model selection and fallback strategy
- Caching strategy
- Error handling philosophy
- Logging and monitoring approach
- Deployment strategy

**Product Decisions (D011-D018)**
- MVP scope (what's in, what's explicitly OUT)
- Pricing model details
- Free tier limits (exact numbers with rationale)
- Onboarding flow approach
- Mobile strategy (PWA vs native vs responsive-only)
- Multi-tenancy approach
- Data retention and deletion policy
- Internationalisation approach

**Business Decisions (D019-D025)**
- Go-to-market sequence
- First 10 customers acquisition strategy
- Support model (self-serve vs touch)
- Compliance and legal requirements
- Data privacy approach (especially AU Privacy Act)
- Third-party dependency risks
- Vendor lock-in assessment

Be specific and reference PRODUCT.md and MARKET-INTEL.md findings.

Create the file: DECISIONS.md
"""

# ─── Pass 4: Architecture ────────────────────────────────────────────

ARCHITECTURE_PROMPT = """You are a senior software architect designing a production system.

You are architecting: {product_name} — {product_description}
Tech stack: Next.js 15, TypeScript, Tailwind v4, Supabase (Postgres + Auth + Storage), Vercel, Stripe

## FIRST: Read these files from disk
1. docs/research/MARKET-INTEL.md
2. PRODUCT.md
3. DECISIONS.md

## Your Task

Write docs/ARCHITECTURE.md — the complete technical architecture document.

Your architecture MUST include:

### 1. System Overview
- Architecture diagram (ASCII art)
- Request flow for the 3 most common user actions
- Data flow diagram

### 2. Database Schema
For EVERY table:
```sql
CREATE TABLE table_name (
  -- complete column definitions with types, constraints, defaults
  -- including RLS policies
);
```
Include:
- All indexes with rationale
- Row-level security policies (who can read/write what)
- Foreign key relationships
- Created_at/updated_at triggers

### 3. API Design
For EVERY endpoint:
| Method | Path | Auth | Request Body | Response | Description |
Include:
- Request validation rules (Zod schemas)
- Error response format (consistent across all endpoints)
- Rate limiting strategy
- Pagination approach

### 4. Authentication & Authorization
- Auth flow (Supabase Auth with Magic Link + OAuth)
- Session management
- Role-based access control (exact roles and permissions matrix)
- API key authentication (for API tier)

### 5. AI Integration
- Which AI model for which task
- Prompt templates (full text, not summaries)
- Fallback chain if primary model fails
- Cost estimation per operation
- Rate limiting for AI calls
- Caching strategy for AI responses

### 6. File Storage
- Supabase Storage buckets and access policies
- File size limits
- Accepted file types
- Image processing pipeline (if applicable)

### 7. Email System
- Transactional emails (list all with triggers)
- Email templates
- Resend configuration

### 8. Security
- Input sanitisation approach
- CSRF protection
- Content Security Policy
- Secrets management
- Audit logging (what events, what data)

### 9. Performance
- Caching layers (React Query + edge)
- Database query optimization notes
- Bundle size budget
- Core Web Vitals targets

### 10. Cost Model
- Supabase tier and expected cost
- Vercel tier and expected cost
- AI API cost per user per month
- Stripe fees
- Total cost at 100, 500, 1000 users

Be production-ready. Every table, every endpoint, every policy must be defined. No TODOs, no "will define later."

Create the file: docs/ARCHITECTURE.md
"""

# ─── Pass 5: Design System ───────────────────────────────────────────

DESIGN_SYSTEM_PROMPT = """You are a senior UI/UX designer creating a comprehensive design system.

You are designing: {product_name} — {product_description}

## FIRST: Read these files from disk
1. PRODUCT.md
2. docs/research/MARKET-INTEL.md (competitor aesthetics)
3. DECISIONS.md

{seed_section}

## Your Task

Write docs/DESIGN-GUIDE.md — the complete visual design system.

This guide will be used by an AI agent (Claude) to build every page. It must be specific enough that two different developers reading it would produce visually identical UIs.

### 1. Design Philosophy
- 3 design principles (e.g., "Data density over whitespace")
- Emotional tone (what should users FEEL)
- Reference products (2-3 existing products whose aesthetic to channel)

### 2. Color System
```
Primary:     #XXXXXX  (use case: ___)
Secondary:   #XXXXXX  (use case: ___)
Accent:      #XXXXXX  (use case: ___)
Success:     #XXXXXX
Warning:     #XXXXXX
Error:       #XXXXXX
Background:  #XXXXXX
Surface:     #XXXXXX
Border:      #XXXXXX
Text:        #XXXXXX
Text Muted:  #XXXXXX
```
- Dark mode variants for every color
- Color contrast ratios (WCAG AA minimum)

### 3. Typography
- Font family: heading, body, mono
- Size scale: xs through 4xl with exact rem values
- Line heights for each size
- Font weights used
- Letter spacing for headings

### 4. Spacing System
- Base unit (4px or 8px grid)
- Spacing scale: 0 through 20 with exact px values
- Section padding rules
- Card padding rules
- Form field spacing

### 5. Layout
- Max content width
- Sidebar width (if applicable)
- Grid system (12-column?)
- Breakpoints: mobile, tablet, desktop, wide
- Container padding per breakpoint

### 6. Components (full specification for each)

For EACH component, specify:
- Visual description with dimensions
- States: default, hover, active, focus, disabled, loading, error
- Variants (primary, secondary, ghost, etc.)
- Dark mode appearance
- Touch target size (minimum 44px)

Components to define:
- Button (primary, secondary, ghost, icon)
- Input (text, select, textarea, checkbox, radio, toggle)
- Card (standard, interactive, stat)
- Modal / Dialog
- Toast / Alert
- Navigation (sidebar, topbar, breadcrumb)
- Table / Data grid
- Badge / Tag
- Avatar
- Loading skeleton
- Empty state
- Error state
- Progress indicator
- Dropdown menu
- Tooltip
- Tabs

### 7. Animation
- Transition duration: fast (150ms), normal (200ms), slow (300ms)
- Easing function
- What animates (page transitions, modals, hovers)
- What does NOT animate (data updates, form validation)

### 8. Iconography
- Icon library (Lucide React recommended)
- Icon sizes per context
- Icon + text alignment rules

### 9. Page Templates
For each major page type, describe the layout:
- Dashboard: sidebar + header + card grid
- Form page: centered card, max-width
- List page: search/filter bar + table + pagination
- Detail page: header + tabs + content

### 10. Mobile Adaptations
- What collapses on mobile
- Bottom sheet vs modal on mobile
- Touch-specific interactions
- Font size adjustments

Be extremely specific. Measurements in pixels, colors in hex, fonts by name. No ambiguity.

Create the file: docs/DESIGN-GUIDE.md
"""

# ─── Pass 6: Developer Guide ─────────────────────────────────────────

DEVELOPER_GUIDE_PROMPT = """You are a senior developer writing conventions for a Next.js 15 TypeScript project.

You are guiding: {product_name} — {product_description}

## FIRST: Read these files from disk
1. PRODUCT.md
2. DECISIONS.md
3. docs/ARCHITECTURE.md

## Your Task

Write docs/DEVELOPER-GUIDE.md — the complete developer conventions and patterns guide.

This will be read by AI agents building the code. Every pattern must be explicit.

### 1. Project Structure
```
src/
├── app/                 # Next.js App Router pages
│   ├── (auth)/         # Auth-required layout group
│   ├── (public)/       # Public layout group
│   ├── api/            # API routes
│   └── layout.tsx
├── components/
│   ├── ui/             # Reusable UI primitives
│   ├── forms/          # Form components
│   ├── layouts/        # Layout components
│   └── [feature]/      # Feature-specific components
├── contracts/          # Shared types and routes (auto-generated)
├── hooks/              # Custom React hooks
├── lib/                # Utility functions
│   ├── supabase/       # Supabase client configs
│   ├── ai/             # AI integration
│   └── utils/          # General utilities
├── styles/             # Global styles
└── types/              # Additional TypeScript types
```

### 2. Naming Conventions
- Files: kebab-case (quote-wizard.tsx)
- Components: PascalCase (QuoteWizard)
- Hooks: camelCase with use prefix (useQuotes)
- Utils: camelCase (formatCurrency)
- Types: PascalCase (QuoteResponse)
- API routes: kebab-case (/api/auth/callback)
- Database tables: snake_case (quote_items)
- Environment variables: SCREAMING_SNAKE_CASE

### 3. Component Patterns
Show the EXACT pattern for:
- Server component (default)
- Client component ("use client" — when and why)
- Form component with validation (react-hook-form + Zod)
- Data fetching component (loading, error, empty states)
- Protected page (auth check)

Include complete code examples for each.

### 4. API Route Patterns
Show the EXACT pattern for:
- GET endpoint with query params
- POST endpoint with body validation
- Protected endpoint (auth check)
- Error handling
- Response format

Include complete code examples.

### 5. Supabase Patterns
- Server client creation
- Browser client creation
- RLS-aware queries
- Realtime subscriptions
- Storage file operations
- Auth helpers

### 6. State Management
- Server state: React Query / SWR configuration
- Client state: React context (when to use)
- Form state: react-hook-form
- URL state: searchParams

### 7. Error Handling
- API errors: consistent ErrorResponse type
- Client errors: Error boundaries + toast notifications
- Form validation: Zod schemas + inline messages
- Network errors: retry logic + offline detection

### 8. Testing Strategy
- What to test (API routes, critical business logic)
- What NOT to test (UI components, Supabase queries)
- Test file naming: *.test.ts

### 9. Pre-Ship Checklist
Before ANY sprint ships:
- [ ] pnpm build passes with zero warnings
- [ ] All API endpoints return proper error responses
- [ ] Loading states on every async operation
- [ ] Empty states on every list/grid
- [ ] Mobile responsive (375px)
- [ ] Dark mode on every component
- [ ] No console.log statements
- [ ] No any types
- [ ] All secrets in env vars, not hardcoded

Create the file: docs/DEVELOPER-GUIDE.md
"""

# ─── Pass 7: Sprint Planning ─────────────────────────────────────────

SPRINT_PLANNING_PROMPT = """You are a senior engineering manager breaking a product into implementable sprints.

You are planning: {product_name} — {product_description}

## FIRST: Read ALL these files from disk
1. PRODUCT.md
2. DECISIONS.md
3. docs/ARCHITECTURE.md
4. docs/DESIGN-GUIDE.md
5. docs/DEVELOPER-GUIDE.md
6. docs/research/MARKET-INTEL.md

## Your Task

Write sprint planning documents for 14 sprints across 7 stages. Create one file per stage.

CRITICAL RULES:
1. Every sprint MUST have a "### Backend" section and a "### Frontend" section
2. Backend tasks list EXACT API endpoints to build, EXACT database tables to create, EXACT validations
3. Frontend tasks list EXACT pages to create, EXACT components, EXACT states (loading, error, empty)
4. Tasks reference docs/ARCHITECTURE.md for schema and API design
5. Tasks reference docs/DESIGN-GUIDE.md for visual specs
6. Each task is small enough for one AI agent session (under 45 minutes)
7. Dependencies between sprints are explicit

### Stage Structure

**Stage 0 (Sprint 0): Validation** — No code. Customer discovery only.
**Stage 1 (Sprints 1-2): Foundation** — Auth, database, onboarding, core data model
**Stage 2 (Sprints 3-4): Core Feature A** — The primary value proposition
**Stage 3 (Sprints 5-6): Core Feature B** — The second major feature
**Stage 4 (Sprints 7-9): Delivery & Integration** — Polish, alerts, third-party integrations
**Stage 5 (Sprints 10-12): Revenue** — Teams, billing, API
**Stage 6 (Sprints 13-14): Scale** — Advanced features, landing page, launch

### Sprint Doc Format

Each stage file should look like:

```markdown
# Stage N: [Stage Name]

## Sprint X: [Sprint Name]

### Backend
- [ ] Create table `table_name` (see ARCHITECTURE.md section Y)
- [ ] Build POST /api/resource — validate with Zod schema, insert to DB, return ApiResponse<Resource>
- [ ] Build GET /api/resource — paginated list, RLS filter by org_id
- [ ] Add RLS policy: users can only access their org's data
- [ ] Run pnpm build to verify

### Frontend
- [ ] Create page /path — server component with data fetching
- [ ] Build ResourceCard component (see DESIGN-GUIDE.md section Z)
- [ ] Add loading skeleton for resource list
- [ ] Add empty state: "No resources yet" with CTA button
- [ ] Add error state with retry button
- [ ] Mobile responsive at 375px
- [ ] Dark mode support
- [ ] Run pnpm build to verify

### Acceptance Criteria
- [ ] User can create a resource via the UI
- [ ] Data persists across page reloads
- [ ] RLS prevents cross-org access
- [ ] All states render correctly (loading, empty, error, populated)
```

Be EXTREMELY specific. "Build the dashboard" is NOT a task. "Build GET /api/dashboard/stats returning DashboardStats with total_count, active_count, revenue_cents, trend_percentage, filtered by org_id with 30-day window" IS a task.

Create these files:
- docs/sprints/stage-0-validation.md
- docs/sprints/stage-1-foundation.md
- docs/sprints/stage-2-core-a.md
- docs/sprints/stage-3-core-b.md
- docs/sprints/stage-4-delivery.md
- docs/sprints/stage-5-revenue.md
- docs/sprints/stage-6-scale.md

Create directory first: mkdir -p docs/sprints
"""

# ─── Pass 8: Contract Types & Config ─────────────────────────────────

CONTRACT_CONFIG_PROMPT = """You are a TypeScript architect defining the contract layer between backend and frontend.

You are defining contracts for: {product_name} — {product_description}

## FIRST: Read ALL these files from disk
1. PRODUCT.md
2. docs/ARCHITECTURE.md (database schema and API endpoints)
3. docs/sprints/stage-1-foundation.md
4. docs/sprints/stage-2-core-a.md
5. docs/sprints/stage-3-core-b.md
6. docs/sprints/stage-4-delivery.md
7. docs/sprints/stage-5-revenue.md
8. docs/sprints/stage-6-scale.md

## Your Task

Generate the .buildrunner/config.py file with COMPLETE sprint contracts, stage mapping, and all configuration.

The config.py must define:

### 1. SPRINT_CONTRACTS
For EVERY sprint that introduces new types or routes, define the TypeScript interfaces and API routes:

```python
SPRINT_CONTRACTS = {{
    1: {{
        "types": {{
            "TypeName": '''export interface TypeName {{
  field: type;
  // ... complete interface
}}''',
        }},
        "routes": {{
            "domain": {{
                "endpoint_name": {{"method": "POST", "path": "/api/...", "auth": True}},
            }},
        }},
    }},
    # ... all sprints
}}
```

EVERY interface from ARCHITECTURE.md must appear in the correct sprint.
EVERY API endpoint from the sprint docs must appear in routes.
Types must match the database schema exactly.

### 2. Full config.py
Generate the COMPLETE config.py including:
- PROJECT_NAME, PROJECT_DESCRIPTION, TECH_STACK
- SPRINT_STAGES mapping (14 sprints → 7 stages)
- STAGE_NAMES
- SPRINT_NAMES (descriptive name for each sprint)
- STAGE_BOUNDARIES
- COMMERCIAL_GATES (specific, measurable gates per stage)
- SPRINT_STAGE_FILES
- SPRINT_PAGES (which URLs to screenshot per sprint)
- ENV_REQUIREMENTS (which env vars needed by which sprint)
- PROTECTED_FILES
- REQUIRED_DOCS
- DESIGN_MAX_PASSES = 5
- DESIGN_ITERATION_FOCUSES
- CIRCUIT_BREAKER_THRESHOLDS
- INIT_PROMPT (Next.js scaffold command with project-specific deps)
- CONSTANTS_TS (shared business constants)
- All prompt templates (BACKEND_PROMPT_TEMPLATE, FRONTEND_PROMPT_TEMPLATE, DESIGN_REVIEW_TEMPLATE, STAGE_REVIEW_TEMPLATE)

Model this after the QuoteFast example but fully populated with this product's data.

IMPORTANT: Write the COMPLETE file. Do not leave any section as TODO or placeholder.

Overwrite the file: .buildrunner/config.py
"""

# ─── Pass 9: CLAUDE.md ───────────────────────────────────────────────

CLAUDE_MD_PROMPT = """You are writing the AI agent rulebook for a dual-agent build system.

You are writing rules for: {product_name} — {product_description}

## FIRST: Read ALL these files from disk
1. PRODUCT.md
2. DECISIONS.md
3. docs/ARCHITECTURE.md
4. docs/DESIGN-GUIDE.md
5. docs/DEVELOPER-GUIDE.md

## Your Task

Write CLAUDE.md — the rules file that both AI agents (Codex backend + Claude frontend) read before every sprint.

Your CLAUDE.md must include:

### Project Identity
- What this is (1 sentence)
- Tech stack
- Target users

### Absolute Rules (violations = instant failure)
- Never expose server-side keys to client
- Never skip input validation on API endpoints
- Never use `any` type
- Never hardcode secrets
- Always use RLS policies from ARCHITECTURE.md
- Always import types from src/contracts/ — NEVER duplicate
- Always import routes from src/contracts/ — NEVER invent URLs
- Backend agent: NEVER touch frontend files
- Frontend agent: NEVER touch backend files

### Design Axioms (from DESIGN-GUIDE.md, condensed)
- Mobile-first (375px is the primary viewport)
- Every async operation: loading skeleton, error state with retry, empty state with CTA
- Dark mode on every component
- Touch targets: minimum 44px
- Consistent spacing from the spacing scale
- No orphaned text, no layout shift

### Code Patterns
- Reference DEVELOPER-GUIDE.md for all patterns
- Server components by default, client components only when needed
- Zod validation on all API inputs
- Consistent error response format

### Pre-Ship Checklist (run before every pnpm build)
- [ ] No TypeScript errors
- [ ] No console.log in production code
- [ ] All API endpoints validate input
- [ ] All pages have loading/error/empty states
- [ ] Mobile responsive
- [ ] Dark mode works
- [ ] Contracts match implementation
- [ ] No hardcoded strings (use constants.ts)

### What NOT to Do
- Do not refactor existing working code unless the sprint doc says to
- Do not add features not in the sprint doc
- Do not change the database schema unless the sprint doc says to
- Do not install new dependencies without clear justification
- Do not create new files outside the project structure

Be concise and direct. Agents have limited context windows. Every word must earn its place.

Create the file: CLAUDE.md
"""

# ─── Pass 10: Self-Review & Fix ──────────────────────────────────────

SELF_REVIEW_PROMPT = """You are a principal engineer and product director reviewing a complete planning package.

You are reviewing: {product_name} — {product_description}

## FIRST: Read EVERY file in this project carefully
1. PRODUCT.md
2. DECISIONS.md
3. CLAUDE.md
4. docs/research/MARKET-INTEL.md
5. docs/ARCHITECTURE.md
6. docs/DESIGN-GUIDE.md
7. docs/DEVELOPER-GUIDE.md
8. docs/sprints/stage-0-validation.md
9. docs/sprints/stage-1-foundation.md
10. docs/sprints/stage-2-core-a.md
11. docs/sprints/stage-3-core-b.md
12. docs/sprints/stage-4-delivery.md
13. docs/sprints/stage-5-revenue.md
14. docs/sprints/stage-6-scale.md
15. .buildrunner/config.py

## Your Task

Conduct a ruthless cross-document review. Find and FIX:

### Consistency Checks
- Does every API endpoint in ARCHITECTURE.md appear in a sprint doc?
- Does every table in the schema have CRUD endpoints?
- Does every sprint's Backend section reference real endpoints from ARCHITECTURE.md?
- Does every sprint's Frontend section reference real pages and components?
- Do sprint docs reference features that are in PRODUCT.md?
- Does config.py SPRINT_CONTRACTS cover every type from ARCHITECTURE.md?
- Do COMMERCIAL_GATES in config.py match the product's growth assumptions?

### Completeness Checks
- Are there features in PRODUCT.md with no sprint assigned?
- Are there database tables with no API endpoints?
- Are there API endpoints with no frontend consumer?
- Are there pages mentioned in sprint docs but not in SPRINT_PAGES in config.py?
- Is the pricing implementation in the sprint docs consistent with PRODUCT.md pricing?

### Quality Checks
- Are sprint tasks specific enough for an AI agent to execute without ambiguity?
- Are acceptance criteria testable?
- Is the architecture production-ready (not just MVP)?
- Are there security gaps (missing RLS, unvalidated inputs, exposed secrets)?
- Is the design system complete enough to build consistent UIs?

### Fix Everything
For every issue found:
1. Identify which file(s) need updating
2. Make the fix directly in the file
3. Log the fix in docs/research/PLANNING-REVIEW.md

Write your review to docs/research/PLANNING-REVIEW.md with:
- PASS/FAIL for each check category
- Issues found and how you fixed them
- Overall quality score (1-10) for each document
- Remaining risks or concerns

Then update ALL files that need fixing. Do not just document issues — FIX THEM.
"""

# ─── Pass 11: Golden Jobs ────────────────────────────────────────────

GOLDEN_JOBS_PROMPT = """You are a QA architect defining canonical test scenarios.

You are testing: {product_name} — {product_description}

## FIRST: Read these files from disk
1. PRODUCT.md
2. docs/ARCHITECTURE.md
3. docs/sprints/stage-1-foundation.md through stage-6-scale.md

## Your Task

Write docs/research/GOLDEN-JOBS.md — 6 canonical end-to-end scenarios that prove the product works.

For EACH golden job:

### Job [Letter]: [Name]
**Persona:** [Who is doing this]
**Scenario:** [Quoted first-person narrative of what they want]
**Preconditions:** [What must exist before this job runs]
**Steps:**
1. [Exact user action] → [Expected system response]
2. [Next action] → [Expected response]
... (8-15 steps per job)
**Success Criteria:**
- [Specific, measurable outcome 1]
- [Specific, measurable outcome 2]
**Validates Sprints:** [Which sprint numbers this tests]
**API Calls Made:** [List exact endpoints hit during this job]

### Job Selection Criteria
- Job A: Core value proposition (the "aha moment")
- Job B: Complete workflow from start to finish
- Job C: Edge case / error recovery
- Job D: Multi-user / collaboration scenario
- Job E: Billing / upgrade flow
- Job F: Data export / deliverable generation

These jobs will be used after Sprint 5+ to validate the product actually works end-to-end.

Create the file: docs/research/GOLDEN-JOBS.md
"""

# ─── Pass 12: Final Quality Gate ─────────────────────────────────────

FINAL_GATE_PROMPT = """You are the final quality gate before autonomous code generation begins.

You are gating: {product_name} — {product_description}

## FIRST: Read EVERY file — this is your last chance to catch issues

Read ALL of these:
1. PRODUCT.md
2. DECISIONS.md
3. CLAUDE.md
4. docs/research/MARKET-INTEL.md
5. docs/research/GOLDEN-JOBS.md
6. docs/research/PLANNING-REVIEW.md
7. docs/ARCHITECTURE.md
8. docs/DESIGN-GUIDE.md
9. docs/DEVELOPER-GUIDE.md
10. All docs/sprints/stage-*.md files
11. .buildrunner/config.py

## Your Task

Score each document 1-10 and decide: SHIP IT or BLOCK.

### Scoring Criteria

| Document | Min Score | What 10 looks like |
|----------|-----------|---------------------|
| MARKET-INTEL.md | 7 | 10+ named competitors with real pricing, real market size data |
| PRODUCT.md | 8 | Every feature has user story + acceptance criteria + sprint number |
| DECISIONS.md | 7 | 25+ decisions, each with alternatives and rationale |
| ARCHITECTURE.md | 8 | Every table, every endpoint, every RLS policy defined |
| DESIGN-GUIDE.md | 7 | Pixel-precise specs, all components, all states |
| DEVELOPER-GUIDE.md | 7 | Complete code patterns with examples |
| Sprint docs | 8 | Every task specific enough for an AI to execute unambiguously |
| config.py | 8 | All contracts, all routes, all types match architecture |
| CLAUDE.md | 7 | Clear rules, no ambiguity |
| GOLDEN-JOBS.md | 7 | 6 jobs with step-by-step validation |

### Actions

1. Score each document
2. For ANY document scoring below its minimum:
   - Identify exactly what's missing or weak
   - FIX IT directly in the file
   - Re-score after fixing
3. Run final consistency check across all documents
4. Write final gate report to docs/research/FINAL-GATE.md

### Final Gate Report Format
```
# Final Quality Gate — {product_name}

## Scores
| Document | Score | Status |
|----------|-------|--------|
| ... | 8/10 | PASS |

## Overall: SHIP / BLOCK
## Issues Fixed: [count]
## Remaining Risks: [list]
## Confidence Level: [HIGH/MEDIUM/LOW]
## Estimated Build Time: [hours]
## Estimated API Cost: [$XX]
```

If ALL documents meet minimum scores: write "SHIP IT" at the top of FINAL-GATE.md.
If any document is unfixable: write "BLOCK" with specific reason.

Create/update: docs/research/FINAL-GATE.md
"""


# ─── Prompt Registry ─────────────────────────────────────────────────

PLANNING_PASSES = [
    {
        "name": "Market Intelligence",
        "prompt": MARKET_INTEL_PROMPT,
        "output_files": ["docs/research/MARKET-INTEL.md"],
        "timeout": 2700,
        "critical": True,
    },
    {
        "name": "Product Definition",
        "prompt": PRODUCT_PROMPT,
        "output_files": ["PRODUCT.md"],
        "timeout": 2700,
        "critical": True,
    },
    {
        "name": "Key Decisions",
        "prompt": DECISIONS_PROMPT,
        "output_files": ["DECISIONS.md"],
        "timeout": 2700,
        "critical": True,
    },
    {
        "name": "Architecture",
        "prompt": ARCHITECTURE_PROMPT,
        "output_files": ["docs/ARCHITECTURE.md"],
        "timeout": 2700,
        "critical": True,
    },
    {
        "name": "Design System",
        "prompt": DESIGN_SYSTEM_PROMPT,
        "output_files": ["docs/DESIGN-GUIDE.md"],
        "timeout": 2700,
        "critical": True,
    },
    {
        "name": "Developer Guide",
        "prompt": DEVELOPER_GUIDE_PROMPT,
        "output_files": ["docs/DEVELOPER-GUIDE.md"],
        "timeout": 2700,
        "critical": False,
    },
    {
        "name": "Sprint Planning",
        "prompt": SPRINT_PLANNING_PROMPT,
        "output_files": [
            "docs/sprints/stage-0-validation.md",
            "docs/sprints/stage-1-foundation.md",
            "docs/sprints/stage-2-core-a.md",
            "docs/sprints/stage-3-core-b.md",
            "docs/sprints/stage-4-delivery.md",
            "docs/sprints/stage-5-revenue.md",
            "docs/sprints/stage-6-scale.md",
        ],
        "timeout": 3600,
        "critical": True,
    },
    {
        "name": "Contract Types & Config",
        "prompt": CONTRACT_CONFIG_PROMPT,
        "output_files": [".buildrunner/config.py"],
        "timeout": 2700,
        "critical": True,
    },
    {
        "name": "CLAUDE.md Rules",
        "prompt": CLAUDE_MD_PROMPT,
        "output_files": ["CLAUDE.md"],
        "timeout": 2700,
        "critical": True,
    },
    {
        "name": "Self-Review & Fix",
        "prompt": SELF_REVIEW_PROMPT,
        "output_files": ["docs/research/PLANNING-REVIEW.md"],
        "timeout": 3600,
        "critical": True,
    },
    {
        "name": "Golden Jobs",
        "prompt": GOLDEN_JOBS_PROMPT,
        "output_files": ["docs/research/GOLDEN-JOBS.md"],
        "timeout": 2700,
        "critical": False,
    },
    {
        "name": "Final Quality Gate",
        "prompt": FINAL_GATE_PROMPT,
        "output_files": ["docs/research/FINAL-GATE.md"],
        "timeout": 3600,
        "critical": True,
    },
]
