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

### Phase 8: Post-Stage Retrospective

Auto-generate lessons learned at stage boundaries. Without retrospectives, you repeat the same mistakes.

## Key Safety Mechanisms

- **File Protection:** Validate critical docs before every agent call, restore from git
- **Circuit Breaker:** 5 identical errors or 3 no-progress loops → stop
- **20-Pass Design:** Score-based exit with stagnation detection
- **Cost Tracking:** Per-sprint, per-agent spend monitoring

## Lessons Learned

1. Prompts must reference files, not embed them (shell limits)
2. Contracts eliminate the #1 integration bug (type mismatches)
3. 5x design iteration catches what 1x doesn't
4. Commercial gates prevent building to silence
5. Separate backend/frontend agents = cleaner code
6. Circuit breakers > infinite retries
7. Study competing repos and cherry-pick their best ideas
