# API Keys & Service Setup Guide

Everything you need to connect a new project to Vercel, Supabase, Stripe, and AI providers.

## 1. AI Agent API Keys (Required)

### Anthropic (for Claude Code)
```bash
# Get key: https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=sk-ant-...
```

### OpenAI (for Codex)
```bash
# Get key: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-...
```

## 2. Supabase (Database + Auth + Storage)

### Create project
1. Go to https://supabase.com/dashboard
2. New Project → pick a name, region (Sydney for AU), generate DB password
3. Wait for provisioning (~2 minutes)

### Get keys
```bash
# Settings → API → Project URL
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co

# Settings → API → anon public key
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# Settings → API → service_role key (NEVER expose to client)
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Settings → Database → Connection string (for migrations)
DATABASE_URL=postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

### Supabase CLI (for local dev + migrations)
```bash
brew install supabase/tap/supabase
supabase login
supabase link --project-ref xxxxx
supabase db push  # Run migrations
```

## 3. Vercel (Deployment)

### Connect repo
1. Go to https://vercel.com/new
2. Import Git Repository → select your repo
3. Framework Preset: Next.js (auto-detected)
4. Add environment variables (all from above)
5. Deploy

### Vercel CLI
```bash
npm install -g vercel
vercel login
vercel link  # Connect to existing project
vercel env pull .env.local  # Pull env vars
vercel --prod  # Deploy to production
```

### Vercel Pro (recommended)
$20/mo — needed for 60s function timeout (AI API calls can take 10-30s)

## 4. Stripe (Payments)

### Setup
1. Go to https://dashboard.stripe.com
2. Developers → API Keys

```bash
# Test keys (for development)
STRIPE_SECRET_KEY=sk_test_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...

# Webhook secret (for /api/webhooks/stripe)
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Create Products + Prices
```bash
# Using Stripe CLI
stripe products create --name="Free" --description="5 items/month"
stripe prices create --product=prod_xxx --unit-amount=0 --currency=aud --recurring[interval]=month

stripe products create --name="Pro" --description="Unlimited"
stripe prices create --product=prod_xxx --unit-amount=4900 --currency=aud --recurring[interval]=month
```

### Webhook Setup
```bash
# Local testing
stripe listen --forward-to localhost:3000/api/webhooks/stripe
# Copy the webhook signing secret → STRIPE_WEBHOOK_SECRET

# Production: Stripe Dashboard → Webhooks → Add endpoint
# URL: https://your-domain.com/api/webhooks/stripe
# Events: checkout.session.completed, customer.subscription.updated, customer.subscription.deleted
```

## 5. Resend (Email)

```bash
# Get key: https://resend.com/api-keys
RESEND_API_KEY=re_...

# Verify domain: Resend Dashboard → Domains → Add Domain → Add DNS records
```

## 6. Twilio (SMS — if needed)

```bash
# Get from: https://console.twilio.com
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+61...  # Buy an AU number
```

## 7. Groq (Fast Whisper — for voice transcription)

```bash
# Get key: https://console.groq.com/keys
GROQ_API_KEY=gsk_...
```

## 8. PostHog (Analytics — optional)

```bash
# Get from: https://app.posthog.com → Project Settings
NEXT_PUBLIC_POSTHOG_KEY=phc_...
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

## 9. Slack (Notifications — optional)

```bash
# Create incoming webhook: https://api.slack.com/apps → Create App → Incoming Webhooks
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...
```

## Complete .env.local Template

```bash
# === AI Agents ===
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# === Supabase ===
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# === Stripe ===
STRIPE_SECRET_KEY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=

# === Email ===
RESEND_API_KEY=

# === Voice (optional) ===
GROQ_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# === Analytics (optional) ===
NEXT_PUBLIC_POSTHOG_KEY=
NEXT_PUBLIC_POSTHOG_HOST=

# === Notifications (optional) ===
SLACK_WEBHOOK_URL=

# === App Config ===
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Quick Setup Script

```bash
#!/bin/bash
# Run this after cloning your project
# Usage: ./setup-env.sh

echo "Setting up environment..."

# Check required CLIs
for cmd in claude codex pnpm node supabase vercel stripe; do
  if command -v $cmd &> /dev/null; then
    echo "  [ok] $cmd"
  else
    echo "  [missing] $cmd"
  fi
done

# Create .env.local from example
if [ ! -f .env.local ]; then
  if [ -f .env.example ]; then
    cp .env.example .env.local
    echo "Created .env.local from .env.example — fill in your keys"
  else
    echo "No .env.example found"
  fi
fi

# Install dependencies
pnpm install

# Link Supabase (if supabase CLI available)
if command -v supabase &> /dev/null; then
  echo "Run: supabase link --project-ref YOUR_PROJECT_REF"
fi

echo "Done. Fill in .env.local and run: python3 .buildrunner/run.py preflight"
```
