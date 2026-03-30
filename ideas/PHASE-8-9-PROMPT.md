# Phase 8+9 Prompt -- Testing, Deployment & Production Readiness

> **Paste this into a Claude Code session after the build completes (14/14 sprints done).**
> Replace `[brackets]` with your product details.
> This handles: automated tests, Supabase prod migration, Vercel deployment.

---

## YOU ARE THE DEPLOYMENT ENGINEER. Execute everything below. Do not ask questions.

### Phase 8: Automated Testing (Codex)

Launch Codex to write and run comprehensive tests:

```bash
cd ~/Dev/[project-name]
codex exec --full-auto --ephemeral - << 'TESTEOF'
You are a senior test engineer for [ProductName].

Read these files first:
1. CLAUDE.md -- project rules
2. docs/ARCHITECTURE.md -- database schema, API endpoints
3. docs/research/GOLDEN-JOBS.md -- canonical test scenarios
4. src/contracts/api-types.ts -- all TypeScript interfaces
5. src/contracts/api-routes.ts -- all API routes

## Step 1: Install test dependencies
pnpm add -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom @vitejs/plugin-react happy-dom playwright @playwright/test
npx playwright install chromium
Create vitest.config.ts with proper Next.js path aliases.

## Step 2: API Integration Tests
For EVERY route in src/app/v1/, create a test file:
- Happy path (correct input -> correct response)
- Auth required (no session -> 401)
- Invalid input (bad body -> 400 with Zod errors)
- RLS enforcement (org A can't access org B data)

## Step 3: Business Logic Unit Tests
Test core logic in src/lib/:
- All scoring/calculation functions
- Validation edge cases
- Entitlement/plan gating logic

## Step 4: Contract Tests
Verify API response shapes match TypeScript interfaces in src/contracts/api-types.ts.

## Step 5: E2E Smoke Tests (Playwright)
Write Playwright tests for the Golden Jobs from docs/research/GOLDEN-JOBS.md.
At minimum: signup flow, core feature flow, billing flow.

## Step 6: Run all tests
pnpm test
Fix any failures until all pass. Then run pnpm build.

## Rules
- Use vitest for unit/integration, Playwright for E2E
- Mock external services (Supabase/Stripe/Resend) in unit tests
- Test files next to source: src/lib/feature/logic.test.ts
- E2E tests in tests/e2e/
- No flaky tests
TESTEOF
```

Wait for Codex to finish. Check with:
```bash
tail -20 ~/Dev/[project-name]/.buildrunner/logs/phase8-testing.log
```

### Phase 9: Deployment

#### Step 1: Create prod Supabase project

```bash
cd ~/Dev/[project-name]
supabase projects create --org-id jpgcmqmhxodlohqjuafs --db-password "$(openssl rand -base64 24)" --region ap-southeast-2 [project-name]-prod
sleep 20
PROD_REF=$(supabase projects list -o json | python3 -c "import json,sys; [print(p['id']) for p in json.load(sys.stdin) if p['name']=='[project-name]-prod']")
supabase link --project-ref $PROD_REF
```

#### Step 2: Fix common migration issues and push

Common fixes needed before pushing:
```bash
# Fix pgcrypto digest calls (Supabase puts extensions in extensions schema)
find supabase/migrations -name "*.sql" -exec sed -i '' 's/encode(digest(/encode(extensions.digest(/g' {} +

# Fix smallint parameter mismatches
find supabase/migrations -name "*.sql" -exec sed -i '' 's/p_maturity_level smallint/p_maturity_level integer/g; s/p_display_order smallint/p_display_order integer/g' {} +
```

Push migrations:
```bash
echo "y" | supabase db reset --linked
```

Verify all migrations applied:
```bash
supabase db push 2>&1 | grep -E "Applying|ERROR"
```

#### Step 3: Get prod keys and write env

```bash
PROD_REF=[ref-from-step-1]
KEYS=$(supabase projects api-keys --project-ref $PROD_REF -o json)
ANON=$(echo "$KEYS" | python3 -c "import json,sys; [print(k['api_key']) for k in json.load(sys.stdin) if k.get('id')=='anon']" | head -1)
SVC=$(echo "$KEYS" | python3 -c "import json,sys; [print(k['api_key']) for k in json.load(sys.stdin) if k.get('id')=='service_role']" | head -1)

cat > .env.production << ENVEOF
NEXT_PUBLIC_SUPABASE_URL=https://${PROD_REF}.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=${ANON}
SUPABASE_SERVICE_ROLE_KEY=${SVC}
STRIPE_SECRET_KEY=placeholder
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=placeholder
STRIPE_WEBHOOK_SECRET=placeholder
RESEND_API_KEY=placeholder
RESEND_FROM_EMAIL=noreply@[domain]
APP_ENVELOPE_ENCRYPTION_KEY=$(openssl rand -hex 32)
NEXT_PUBLIC_APP_URL=https://[project-name].vercel.app
ENVEOF
```

#### Step 4: Deploy to Vercel

```bash
cd ~/Dev/[project-name]
vercel link  # If not already linked
vercel env pull .env.local  # Or push env vars:

# Push each env var to Vercel
while IFS='=' read -r key value; do
  [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
  echo "$value" | vercel env add "$key" production
done < .env.production

# Deploy
vercel --prod
```

#### Step 5: Verify production

```bash
PROD_URL=$(vercel inspect --json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('url',''))" 2>/dev/null || echo "https://[project-name].vercel.app")
curl -s "$PROD_URL" | head -20
curl -s "$PROD_URL/v1/auth/session" -w "\n%{http_code}"
```

### Stripe Setup (when ready)

Document for later -- needs real Stripe keys:

1. Create products in Stripe Dashboard matching PRODUCT.md pricing tiers
2. Create monthly + annual prices for each product
3. Set env vars: STRIPE_SECRET_KEY, NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
4. Create webhook endpoint: `https://[domain]/v1/billing/webhook`
5. Subscribe to events: checkout.session.completed, customer.subscription.updated, customer.subscription.deleted, invoice.payment_failed
6. Set STRIPE_WEBHOOK_SECRET from the webhook config

### Monitoring (post-deploy)

```bash
# Set up Ralph for continuous health checking
cd ~/Dev/[project-name]
bash ~/Dev/dual-agent-builder/.buildrunner/setup_ralph.sh ~/Dev/[project-name]

# Ralph checks build + tests every 15 min, fixes if broken
ralph --monitor
```

### DNS (when ready)

1. Add custom domain in Vercel: Settings > Domains > Add
2. Point DNS: CNAME record to cname.vercel-dns.com
3. Update NEXT_PUBLIC_APP_URL in Vercel env vars
4. Update Supabase Auth redirect URLs
5. Update Stripe webhook URL
