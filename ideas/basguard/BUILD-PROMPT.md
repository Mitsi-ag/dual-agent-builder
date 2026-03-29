# BasGuard — Agent Regression Preventer

> Paste this into Claude Code to generate planning docs and build the product.
> Then run: `python3 .buildrunner/run.py unattended`

---

## Product Vision

BasGuard is an MCP server that prevents AI coding agents from repeating known mistakes. It watches your git history, test failures, and code review comments, builds a structured anti-pattern registry, and injects warnings when an agent is about to make a known-bad change.

**Tagline:** "Your codebase remembers. Your agents learn."

## Tech Stack
Next.js 15, TypeScript, Tailwind v4, Supabase, Vercel, Stripe

## 14 Sprints / 7 Stages

### Stage 0 (Sprint 0): Validation
- Find 8 dev leads using Claude Code/Cursor who've seen repeated AI mistakes

### Stage 1 (Sprints 1-2): Foundation
- Sprint 1: Next.js scaffold, Supabase auth, repos table, dashboard shell
- Sprint 2: Git integration — clone/connect repos, parse commit history, store metadata

### Stage 2 (Sprints 3-4): Pattern Engine
- Sprint 3: Anti-pattern extractor — analyze reverted commits, test failures, review comments with AI. Build structured patterns (category, severity, frequency, code snippet, fix)
- Sprint 4: Pattern matching engine — when agent context includes a file, check against patterns for that file/module. Return warnings with confidence scores

### Stage 3 (Sprints 5-6): MCP Server
- Sprint 5: MCP server implementation — `pattern_check` tool that agents call before making changes. Returns relevant warnings. Integrates with Claude Code via CLAUDE.md auto-include
- Sprint 6: Real-time monitoring — websocket feed of agent actions, pattern match hits, warnings delivered, warnings ignored

### Stage 4 (Sprints 7-9): Dashboard
- Sprint 7: Pattern dashboard — browse all patterns, filter by category/severity/file, edit/promote/dismiss
- Sprint 8: Analytics — pattern hit frequency, most costly patterns (time to fix), trend over time, team comparison
- Sprint 9: Cross-repo patterns — patterns that apply across multiple repos, team-wide learning

### Stage 5 (Sprints 10-12): Revenue
- Sprint 10: Team features — invite members, per-repo permissions, pattern sharing controls
- Sprint 11: Stripe billing — free/team/enterprise tiers, usage tracking
- Sprint 12: API + integrations — REST API, GitHub App for auto-connecting repos, webhook events

### Stage 6 (Sprints 13-14): Scale
- Sprint 13: IDE integrations — VS Code extension showing pattern warnings inline, Cursor support
- Sprint 14: Landing page, docs, onboarding wizard, SEO, pricing page

## Key Contract Types

```typescript
export interface Pattern {
  id: string;
  repo_id: string;
  category: 'a11y' | 'security' | 'performance' | 'typescript' | 'testing' | 'architecture' | 'design';
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  bad_pattern: string;      // code snippet of what NOT to do
  good_pattern: string;     // code snippet of the fix
  file_patterns: string[];  // glob patterns of affected files
  occurrence_count: number;
  first_seen_commit: string;
  last_seen_commit: string;
  is_promoted: boolean;     // promoted to hard rule
  created_at: string;
}

export interface PatternMatch {
  id: string;
  pattern_id: string;
  agent_session_id: string;
  file_path: string;
  confidence: number;       // 0-100
  warning_delivered: boolean;
  warning_heeded: boolean;  // did the agent change behavior?
  created_at: string;
}

export interface Repo {
  id: string;
  org_id: string;
  name: string;
  github_url: string;
  last_analyzed_commit: string | null;
  pattern_count: number;
  is_active: boolean;
}
```

## Design Direction
- **Dark mode default**, code-editor aesthetic (feels like part of the dev toolchain)
- **Primary:** #1E293B (slate-800), **Accent:** #F59E0B (amber) for warnings, #10B981 (emerald) for safe
- **Font:** JetBrains Mono for code/patterns, Inter for body
- **Key component:** Pattern card with bad→good code diff, severity badge, occurrence count

## Golden Jobs

### Job A — Detect Repeated TypeScript Error
> "My team keeps using `any` type in API response handlers. The reviewer catches it every sprint. BasGuard should warn the agent before it writes `any`."

### Job B — Cross-Repo Security Pattern
> "We had an SQL injection in repo A last month. Warn all agents across our 5 repos when they write raw SQL without parameterization."

### Job C — Architecture Violation
> "Agents keep importing from `src/lib/` directly in components instead of using the hook layer. Warn when this import pattern appears."

### Job D — Test Regression
> "A test for the payment flow broke 3 sprints in a row because agents modify the mock data format. Warn when touching payment test fixtures."

## Run

```bash
# Copy orchestrator, edit config.py, write planning docs
cp -r /path/to/dual-agent-builder/.buildrunner/ .buildrunner/
# Edit config.py with sprints/contracts above

# Terminal 1: Build
nohup python3 -u .buildrunner/run.py unattended > .buildrunner/logs/run.log 2>&1 &
echo $! > .buildrunner/.runner-pid

# Terminal 2: Watch live
tail -f .buildrunner/logs/codex-live.log .buildrunner/logs/claude-live.log

# Terminal 3: Monitor
watch -n 300 python3 .buildrunner/monitor.py
```
