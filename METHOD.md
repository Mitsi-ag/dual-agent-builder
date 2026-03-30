# Software Development Method — Dual-Agent Orchestration v2

**Established:** March 2026 with QuoteFast
**Validated:** 14 sprints, 5 completed autonomously, total cost under $50

## The Method (8 Phases)

### Phase 1: Opportunity Research & Selection
- Research 10-20 opportunities in parallel
- Score each on TEMPO: Timing, Ecosystem, Monetizable, Personal fit, Opportunity window
- Rank by "fastest meaningful dollar" not biggest TAM
- Pick ONE and go all-in

### Phase 2: Planning Documentation (~14,000 lines)

Create these BEFORE any code:

| File | Purpose |
|------|---------|
| PRODUCT.md | Vision, features, pricing, kill signals |
| DECISIONS.md | Every non-obvious decision (D001+) with rationale |
| CLAUDE.md | AI rules, design axioms, pre-ship checklist |
| docs/ARCHITECTURE.md | Schema, API contracts, AI prompts, cost model |
| docs/DESIGN-GUIDE.md | Colors, typography, spacing, components |
| docs/DEVELOPER-GUIDE.md | Structure, conventions, patterns |
| docs/sprints/stage-N-*.md | Sprint tasks with Backend/Frontend sections |
| docs/research/GOLDEN-JOBS.md | Canonical test scenarios |

### Phase 3: Contract Layer Setup

TypeScript files in `src/contracts/` that BOTH agents import:
- `api-types.ts` — request/response interfaces
- `api-routes.ts` — route paths, methods, auth
- `constants.ts` — shared business constants

Without contracts, Codex builds `/api/quotes` and Claude fetches `/api/quote/list`. Contracts eliminate this entire class of bugs.

### Phase 4: Automated Build Runner

Python orchestrator (`.buildrunner/run.py`) runs sprints sequentially:

1. Validate protected files (restore from git if deleted)
2. Generate contract skeleton
3. Codex builds backend (reads docs from disk)
4. Build verification (pnpm build)
5. Update contracts with actual implementation
6. Claude builds frontend (imports contracts)
7. Build verification
8. 5-pass Playwright design iteration
9. Git commit
10. Stage review + commercial gate

### Phase 5: Execution

```bash
nohup python3 -u .buildrunner/run.py unattended > .buildrunner/logs/run.log 2>&1 &
echo $! > .buildrunner/.runner-pid
```

### Phase 5.5: Monitoring

**Terminal 2 — Live output:**
```bash
tail -f .buildrunner/logs/codex-live.log .buildrunner/logs/claude-live.log
```

**Terminal 3 — Health monitor:**
```bash
python3 .buildrunner/monitor.py
```

Or from Claude Code REPL:
```
CronCreate: */5 * * * *
Prompt: cd /path/to/project && python3 .buildrunner/monitor.py
```

### Phase 6: Validation (Golden Jobs)

After Sprint 5+, test with canonical scenarios. 3 of 4 must produce acceptable output or the sprint fails.

### Phase 7: Commercial Gates

| Stage | Gate |
|-------|------|
| 0 | Discovery calls completed |
| 1 | 1 real signup |
| 2 | 1 real workflow completed |
| 3 | 3 outputs at production quality |
| 4 | 1 output delivered to customer |
| 5 | 3 paying customers |
| 6 | $500+ MRR |

### Phase 8: Automated Testing (Ralph Mode)

After all sprints complete, Codex writes tests autonomously:

1. **API Integration Tests** — Every route gets a test (happy path + error cases)
2. **Business Logic Tests** — Quote generation, pricebook matching, GST calculation, usage limits
3. **Contract Tests** — Verify API responses match `api-types.ts` interfaces
4. **E2E Smoke Tests** — Playwright tests for critical user flows (signup → create quote → send)

```bash
# Codex writes tests
codex exec --full-auto --ephemeral - <<'EOF'
Read the project at ~/Dev/project-name/. Write comprehensive tests:
1. Install vitest + @testing-library/react
2. Create tests for every API route in src/app/api/
3. Create tests for business logic in src/lib/
4. Create Playwright E2E tests for critical flows
5. Run tests and fix failures until all pass
EOF
```

**Ralph Mode** monitors continuously and self-improves:
```
CronCreate: */15 * * * *
Prompt: cd /path/to/project && pnpm build && pnpm test && pnpm lint
  If any fail, launch Codex to fix. Commit when green.
  Self-assess: "Is this the best I could have done?"
```

### Phase 9: Deployment

Automated deployment pipeline:

1. **GitHub** — `gh repo create org/project --private --source=. --push`
2. **Vercel** — `vercel link --yes && vercel --prod --yes`
3. **Env vars** — Pipe `.env.local` to `vercel env add` for production
4. **Supabase migrations** — `supabase db push`
5. **Supabase auth URLs** — **CRITICAL: Update Site URL + Redirect URLs to production domain** (not localhost!)
6. **DNS** — Point custom domain via Vercel
7. **Stripe** — Create products/prices matching PLAN_LIMITS, configure webhook URL to production
8. **SMS/Email** — Configure Twilio/Resend with real credentials
9. **Monitoring** — Vercel Analytics, Sentry error tracking

**Deployment checklist (MUST verify before calling it "deployed"):**
```
[ ] curl production URL returns 200
[ ] Signup flow works (not redirecting to localhost)
[ ] Magic link email arrives and redirects to production URL
[ ] Supabase Site URL points to production (not localhost:3000)
[ ] Supabase Redirect URLs include production /api/auth/callback
[ ] NEXT_PUBLIC_APP_URL env var set to production URL on Vercel
[ ] Landing page has no placeholder content ("App Preview" boxes, lorem ipsum)
[ ] All marketing pages render with real content (no broken images)
[ ] Auth callback handles both GET (OAuth redirect) and POST (code exchange)
[ ] Stripe webhook URL points to production /api/webhooks/stripe
```

**Common deployment bugs (from QuoteFast):**
- Supabase magic link redirects to `localhost:3000` — must update Site URL in Supabase dashboard
- Landing page "App Preview" placeholder — AI builders leave these, must replace with real mockup/screenshot
- Env vars with `localhost` values deployed to production — check NEXT_PUBLIC_APP_URL
- `eslint-config-next` + ESLint 9 flat config incompatibility — use `typescript-eslint` directly
- Unused imports left by AI builders — run lint after build, fix before deploy

### Phase 10: Post-Stage Retrospective

Auto-generate lessons learned at stage boundaries. Without retrospectives, you repeat the same mistakes.

## Key Safety Mechanisms

- **File Protection:** Validate critical docs before every agent call, restore from git
- **Circuit Breaker:** 5 identical errors or 3 no-progress loops → stop
- **5-Pass Design:** Focused iteration (layout → colors → typography → states → polish)
- **Cost Tracking:** Per-sprint, per-agent spend monitoring
- **Dual Stuck Detection:** Check BOTH log staleness AND file modifications before killing agents

## Lessons Learned

1. Prompts must reference files, not embed them (shell limits)
2. Contracts eliminate the #1 integration bug (type mismatches)
3. 5x design iteration catches what 1x doesn't
4. Commercial gates prevent building to silence
5. Separate backend/frontend agents = cleaner code
6. Circuit breakers > infinite retries
7. Study competing repos and cherry-pick their best ideas
8. `claude -p` buffers ALL output until completion — check file mtime not just logs
9. Tests after build, not during — AI builders introduce unused imports that waste test time
10. Deploy immediately after tests pass — a demo nobody can access isn't a product
11. Ralph Mode (continuous self-assessment) catches what single-pass review misses
12. ALWAYS test auth flow end-to-end on production before calling it "deployed" — Supabase Site URL defaults to localhost
13. AI builders leave placeholder content (empty mockups, "App Preview" boxes) — scan every marketing page visually before shipping
14. Supabase auth config must be pushed via `supabase config push` — CLI stores credentials in macOS Keychain (`Supabase CLI` service name)
15. Deployment checklist is non-negotiable: signup must work, magic links must redirect to production, no placeholder content
