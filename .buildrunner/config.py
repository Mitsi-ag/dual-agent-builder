"""
Project configuration for the Dual-Agent Builder.

EDIT THIS FILE for your project. All orchestrator modules read from here.
Copy this template, fill in your project details, sprint plan, contracts,
and commercial gates.
"""

# ─── Project Identity ───────────────────────────────────────────────
PROJECT_NAME = "MyProject"
PROJECT_DESCRIPTION = "One-line description of your product"
TECH_STACK = "Next.js 15 + Supabase + Vercel"

# ─── Agent Configuration ────────────────────────────────────────────
# Which agent builds what. Options: "codex", "claude"
BACKEND_AGENT = "codex"
FRONTEND_AGENT = "claude"

# ─── Sprint / Stage Mapping ─────────────────────────────────────────
# Map each sprint number to its stage number.
# Stages group sprints into logical phases with commercial gates.
SPRINT_STAGES: dict[int, int] = {
    0: 0,
    1: 1, 2: 1,
    3: 2, 4: 2,
    5: 3, 6: 3,
    7: 4, 8: 4, 9: 4,
    10: 5, 11: 5, 12: 5,
    13: 6, 14: 6,
}

STAGE_NAMES: dict[int, str] = {
    0: "Validation",
    1: "Foundation",
    2: "Core Feature A",
    3: "Core Feature B",
    4: "Delivery",
    5: "Revenue",
    6: "Scale",
}

# Sprint descriptions for status display
SPRINT_NAMES: dict[int, str] = {
    0: "Validation (no code)",
    1: "Repo, Auth & Database",
    2: "Onboarding & Settings",
    3: "Feature A - Part 1",
    4: "Feature A - Part 2",
    5: "Feature B - Part 1",
    6: "Feature B - Part 2",
    7: "Feature C - Part 1",
    8: "Feature C - Part 2",
    9: "Feature C - Part 3",
    10: "Dashboard & Analytics",
    11: "Templates & Management",
    12: "Billing & Usage",
    13: "PWA & Offline",
    14: "Landing Page & Launch",
}

# Sprints that mark the END of a stage (trigger review + commercial gate)
STAGE_BOUNDARIES: set[int] = {0, 2, 4, 6, 9, 12, 14}

# ─── Commercial Gates ───────────────────────────────────────────────
# Human checkpoints at stage boundaries. Build pauses until gate is met.
COMMERCIAL_GATES: dict[int, str] = {
    0: "Discovery calls completed across target personas",
    1: "1 real person signed up with real data",
    2: "1 real user completed core workflow",
    3: "3 AI outputs edited to production quality (< 30% rewrite)",
    4: "1 output delivered to real customer",
    5: "3 paying customers",
    6: "10 paying customers, $500+ MRR",
}

# ─── Sprint Doc Files ───────────────────────────────────────────────
# Maps sprint number to the planning doc filename in docs/sprints/
SPRINT_STAGE_FILES: dict[int, str] = {
    0: "stage-0-validation.md",
    1: "stage-1-foundation.md",
    2: "stage-1-foundation.md",
    3: "stage-2-core-a.md",
    4: "stage-2-core-a.md",
    5: "stage-3-core-b.md",
    6: "stage-3-core-b.md",
    7: "stage-4-delivery.md",
    8: "stage-4-delivery.md",
    9: "stage-4-delivery.md",
    10: "stage-5-revenue.md",
    11: "stage-5-revenue.md",
    12: "stage-5-revenue.md",
    13: "stage-6-scale.md",
    14: "stage-6-scale.md",
}

# ─── Pages Per Sprint (for Design Iteration) ────────────────────────
# Which pages to screenshot and review after each sprint's frontend work.
SPRINT_PAGES: dict[int, list[str]] = {
    1: ["/login", "/signup", "/dashboard"],
    2: ["/onboarding", "/settings"],
    3: [],
    4: [],
    5: ["/new"],
    6: ["/new"],
    7: ["/settings/brand"],
    8: [],
    9: [],
    10: ["/dashboard"],
    11: ["/templates"],
    12: ["/settings/billing", "/pricing"],
    13: [],
    14: ["/", "/pricing", "/features"],
}

# ─── Environment Variables ───────────────────────────────────────────
# Required env vars per sprint (cumulative — sprint 5 requires all from 1-5)
ENV_REQUIREMENTS: dict[int, list[str]] = {
    1: [
        "NEXT_PUBLIC_SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
    ],
}

# ─── Protected Files ────────────────────────────────────────────────
# Restored from git if accidentally deleted by an agent during a run.
PROTECTED_FILES: list[str] = [
    "PRODUCT.md",
    "CLAUDE.md",
    "DECISIONS.md",
    "docs/ARCHITECTURE.md",
    "docs/DESIGN-GUIDE.md",
    "docs/DEVELOPER-GUIDE.md",
    "src/contracts/api-types.ts",
    "src/contracts/api-routes.ts",
    "src/contracts/constants.ts",
]

# ─── Required Planning Docs ─────────────────────────────────────────
# Preflight checks these exist before running any sprint.
REQUIRED_DOCS: list[str] = [
    "CLAUDE.md",
    "PRODUCT.md",
    "docs/ARCHITECTURE.md",
    "docs/DESIGN-GUIDE.md",
]

# ─── Design Iteration ───────────────────────────────────────────────
DESIGN_MAX_PASSES = 5

DESIGN_ITERATION_FOCUSES: dict[int, str] = {
    1: "Layout, spacing, colors — elements aligned? Colors match DESIGN-GUIDE.md?",
    2: "Typography, touch targets, loading states — correct fonts? 48-56px targets? Skeletons?",
    3: "Error states, empty states, dark mode — every fetch has error UI? Dark mode works?",
    4: "Interactive states, edge cases — hover/active/focus look right? Long text handled?",
    5: "Final sweep — screenshot every page, professional trust check, fix ANY inconsistency",
}

# ─── Circuit Breaker ────────────────────────────────────────────────
CIRCUIT_BREAKER_THRESHOLDS = {
    "same_error": 5,        # Open after N identical errors
    "no_progress": 3,       # Open after N loops with 0 file changes
    "max_retries": 999,     # Hard cap on retries per phase
    "max_cost_per_sprint": 25.0,  # USD
}

# ─── Init Command (Sprint 1 Project Scaffold) ───────────────────────
# The prompt used to initialize the project on Sprint 1 if no package.json exists.
INIT_PROMPT = """Initialize a new Next.js 15 project in this directory:

1. Run: pnpm create next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --turbopack
   (Accept defaults, use pnpm)

2. Install core dependencies (edit for your stack):
   pnpm add @supabase/supabase-js @supabase/ssr zod lucide-react framer-motion
   pnpm add -D @types/node

3. Create tsconfig.json with strict: true

4. Verify: pnpm build passes

Do NOT create any application code. Just the project scaffold."""

# ─── Contracts ───────────────────────────────────────────────────────
# Define your TypeScript types and API routes per sprint.
# The contract generator builds cumulative src/contracts/ files.
# See examples/quotefast/config.py for a filled-in example.

SPRINT_CONTRACTS: dict[int, dict] = {
    # 1: {
    #     "types": {
    #         "User": '''export interface User {
    #   id: string;
    #   email: string;
    #   name: string;
    #   created_at: string;
    # }''',
    #     },
    #     "routes": {
    #         "auth": {
    #             "callback": {"method": "POST", "path": "/api/auth/callback", "auth": False},
    #         },
    #     },
    # },
}

# ─── Shared Constants Template ───────────────────────────────────────
# Written to src/contracts/constants.ts
CONSTANTS_TS = """// Shared constants used by both backend and frontend
// Edit this in .buildrunner/config.py CONSTANTS_TS

export const APP_NAME = 'MyProject';
"""

# ─── Backend Prompt Template ────────────────────────────────────────
# {sprint_num}, {stage_file}, {contracts}, {routes}, {constants} are interpolated
BACKEND_PROMPT_TEMPLATE = """You are the BACKEND developer for {project_name}.

BEFORE YOU START, read these files from disk (they are your instructions):
1. CLAUDE.md — rules and conventions
2. docs/ARCHITECTURE.md — database schema, API design
3. docs/sprints/{stage_file} — find Sprint {sprint_num}, read the "### Backend" section

Execute ALL backend tasks listed under "### Backend" in Sprint {sprint_num}.

## CONTRACT TYPES — You MUST import from src/contracts/api-types.ts
```typescript
{contracts}
```

## CONTRACT ROUTES — You MUST use these exact paths
```typescript
{routes}
```

## SHARED CONSTANTS
```typescript
{constants}
```

## CRITICAL RULES
1. Read the docs above FIRST before writing any code
2. Import ALL types from src/contracts/api-types.ts — do NOT create duplicate types
3. Use paths from src/contracts/api-routes.ts — do NOT invent your own URL paths
4. Import constants from src/contracts/constants.ts
5. After building each endpoint, UPDATE src/contracts/api-types.ts if your actual types differ
6. Do NOT touch frontend files
7. When done, run: pnpm build
"""

# ─── Frontend Prompt Template ───────────────────────────────────────
FRONTEND_PROMPT_TEMPLATE = """You are the FRONTEND developer for {project_name}.

BEFORE YOU START, read these files from disk (they are your instructions):
1. CLAUDE.md — rules, design axioms, UX rules, anti-patterns, pre-ship checklist
2. docs/DESIGN-GUIDE.md — colors, typography, spacing, component specs, animations
3. docs/sprints/{stage_file} — find Sprint {sprint_num}, read the "### Frontend" section

Execute ALL frontend tasks listed under "### Frontend" in Sprint {sprint_num}.

## API CONTRACTS — Import from src/contracts/ (backend endpoints already built)
```typescript
{contracts}
```

## ROUTES
```typescript
{routes}
```

## CONSTANTS
```typescript
{constants}
```

## CRITICAL RULES
1. Read the docs above FIRST before writing any code
2. Import ALL API types from src/contracts/api-types.ts — these match the backend exactly
3. Use API_ROUTES from src/contracts/api-routes.ts for ALL fetch URLs
4. Mobile-first design
5. Every page: loading skeleton, error state with retry, empty state with CTA
6. Dark mode on every component
7. Do NOT touch backend files
8. When done, run: pnpm build
"""

# ─── Design Review Prompt Template ──────────────────────────────────
DESIGN_REVIEW_TEMPLATE = """You are a senior UI/UX designer reviewing {project_name}.
This is design iteration {iteration} of {max_passes} for Sprint {sprint_num}.

Read docs/DESIGN-GUIDE.md first for the complete design system.

## Pages to review:
{pages}

## FOCUS FOR THIS PASS:
{focus}

## Instructions:
1. Use browser_navigate to go to each page
2. Use browser_resize to set width=375, height=812 (mobile viewport)
3. Use browser_take_screenshot to capture current state
4. Compare screenshot against docs/DESIGN-GUIDE.md
5. Fix EVERY issue by editing component source files
6. Screenshot again to verify fixes
7. Move to next page

Be {detail_level}.
"""

# ─── Stage Review Prompt Template ───────────────────────────────────
STAGE_REVIEW_TEMPLATE = """You are a senior architect reviewing {project_name} after Stage {stage} completion.

Read these files:
1. CLAUDE.md — rules
2. docs/ARCHITECTURE.md — schema, API design
3. docs/sprints/{stage_file} — acceptance criteria

Check:
1. TypeScript strict: any 'any' types or unsafe casts?
2. Input validation on every API endpoint?
3. Auth/authorization policies prevent cross-user access?
4. Error responses use consistent format?
5. Contract types in src/contracts/ match actual implementation?
6. All acceptance criteria in the stage file pass?

Write your review to .buildrunner/reviews/stage-{stage}-review.md with:
- PASS/FAIL for each criterion
- Issues: CRITICAL / IMPORTANT / MINOR
- Fix recommendations
"""
