"""
QuoteFast config — real example from production build.
AI quoting for Australian tradies. 14 sprints, 7 stages.
Copy this as a reference when setting up your own config.py.
"""

PROJECT_NAME = "QuoteFast"
PROJECT_DESCRIPTION = "AI quoting for Australian tradies. Mobile-first PWA."
TECH_STACK = "Next.js 15 + Supabase + Vercel"

BACKEND_AGENT = "codex"
FRONTEND_AGENT = "claude"

SPRINT_STAGES = {
    0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3,
    7: 4, 8: 4, 9: 4, 10: 5, 11: 5, 12: 5, 13: 6, 14: 6,
}

STAGE_NAMES = {
    0: "Validation", 1: "Foundation", 2: "Capture",
    3: "Intelligence", 4: "Delivery", 5: "Revenue", 6: "Scale",
}

SPRINT_NAMES = {
    0: "Validation (no code)",
    1: "Repo, Auth & Database",
    2: "Onboarding & Pricebook",
    3: "Photo Capture & AI Analysis",
    4: "Voice Recording & Transcription",
    5: "AI Quote Generation",
    6: "Quote Editor & Line Items",
    7: "PDF Generation & Branding",
    8: "SMS/Email Delivery & Portal",
    9: "Customer Acceptance & Signature",
    10: "Dashboard & Analytics",
    11: "Templates & Pricebook Management",
    12: "Stripe Billing & Usage",
    13: "PWA & Offline",
    14: "Landing Page, SEO & Launch",
}

STAGE_BOUNDARIES = {0, 2, 4, 6, 9, 12, 14}

COMMERCIAL_GATES = {
    0: "8 calls across 3+ trades, 4 quotes, 2 pricebooks",
    1: "1 person signed up with real business data + pricebook",
    2: "1 real job captured (photos + voice) by real tradie",
    3: "3 AI quotes edited to sendable quality (< 30% rewrite)",
    4: "1 quote sent to real customer, viewed, responded to",
    5: "3 paying customers across 2+ trades",
    6: "10 paying customers, $500+ MRR",
}

SPRINT_STAGE_FILES = {
    0: "stage-0-validation.md", 1: "stage-1-foundation.md",
    2: "stage-1-foundation.md", 3: "stage-2-capture.md",
    4: "stage-2-capture.md", 5: "stage-3-intelligence.md",
    6: "stage-3-intelligence.md", 7: "stage-4-delivery.md",
    8: "stage-4-delivery.md", 9: "stage-4-delivery.md",
    10: "stage-5-revenue.md", 11: "stage-5-revenue.md",
    12: "stage-5-revenue.md", 13: "stage-6-scale.md",
    14: "stage-6-scale.md",
}

SPRINT_PAGES = {
    1: ["/login", "/signup", "/dashboard"],
    2: ["/onboarding", "/pricebook", "/settings/profile"],
    3: [], 4: [],
    5: ["/quotes/new"], 6: ["/quotes/new"],
    7: ["/settings/brand"],
    8: ["/q/test-token"], 9: ["/q/test-token"],
    10: ["/dashboard", "/quotes", "/customers"],
    11: ["/templates"],
    12: ["/settings/billing", "/pricing"],
    13: [],
    14: ["/", "/pricing", "/features"],
}

ENV_REQUIREMENTS = {
    1: ["NEXT_PUBLIC_SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY", "ANTHROPIC_API_KEY"],
    4: ["GROQ_API_KEY"],
    8: ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER", "RESEND_API_KEY"],
    12: ["STRIPE_SECRET_KEY", "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY"],
}

PROTECTED_FILES = [
    "PRODUCT.md", "CLAUDE.md", "DECISIONS.md",
    "docs/ARCHITECTURE.md", "docs/DESIGN-GUIDE.md",
    "docs/DEVELOPER-GUIDE.md",
    "src/contracts/api-types.ts", "src/contracts/api-routes.ts",
    "src/contracts/constants.ts",
]

REQUIRED_DOCS = [
    "CLAUDE.md", "PRODUCT.md",
    "docs/ARCHITECTURE.md", "docs/DESIGN-GUIDE.md",
]

DESIGN_MAX_PASSES = 20

# See contracts.py in the main QuoteFast repo for all 12 sprint contracts
# (Profile, PricebookItem, PhotoAnalysis, VoiceNote, Job, Quote,
#  QuoteLineItem, QuoteSettings, SendQuoteRequest, Customer,
#  AcceptQuoteRequest, DashboardStats, QuoteTemplate, UsageData)
SPRINT_CONTRACTS = {}  # Full contracts in ~/Dev/quotefast-cc/.buildrunner/contracts.py

CONSTANTS_TS = """// QuoteFast shared constants
export const GST_RATE = 0.10;
export const PLAN_LIMITS = {
  free: { quotes_per_month: 5 },
  starter: { quotes_per_month: 30 },
  pro: { quotes_per_month: -1 },
  business: { quotes_per_month: -1 },
} as const;
export type PlanTier = keyof typeof PLAN_LIMITS;
export const QUOTE_STATUSES = ['draft', 'sent', 'viewed', 'accepted', 'declined', 'expired'] as const;
export type QuoteStatus = typeof QUOTE_STATUSES[number];
export const TRADE_TYPES = [
  'plumbing', 'electrical', 'painting', 'building', 'landscaping',
  'hvac', 'carpentry', 'roofing', 'tiling', 'fencing', 'concreting', 'handyman', 'other'
] as const;
"""
