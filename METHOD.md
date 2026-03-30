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

1. **Supabase** — Apply all migrations, verify RLS policies
2. **Vercel** — Connect repo, set env vars, deploy
3. **DNS** — Point custom domain
4. **Stripe** — Create products/prices matching PLAN_LIMITS, configure webhook URL
5. **SMS/Email** — Configure Twilio/Resend with real credentials
6. **Monitoring** — Vercel Analytics, Sentry error tracking

```bash
# Deploy via Codex
codex exec --full-auto --ephemeral - <<'EOF'
Deploy the project:
1. Run `vercel --prod` (or `vercel link` first if needed)
2. Set all env vars from .env.local via `vercel env add`
3. Apply Supabase migrations: `supabase db push`
4. Verify deployment: curl the production URL
5. Run E2E tests against production
EOF
```

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
