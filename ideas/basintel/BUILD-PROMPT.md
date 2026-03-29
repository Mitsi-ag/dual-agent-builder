# BasIntel — Vertical Intelligence Dashboard

> Paste this into Claude Code to generate planning docs and build the product.
> Then run: `python3 .buildrunner/run.py unattended`

---

## Product Vision

BasIntel is a vertical-specific real-time intelligence dashboard. Start with ONE vertical (AI/ML industry), templatize, then expand. News aggregation + AI synthesis + actionable alerts.

**Tagline:** "Know what matters. Before everyone else."

**Starting vertical:** AI/ML — model releases, company pivots, funding rounds, open source trends, regulatory moves.

## Tech Stack
Next.js 15, TypeScript, Tailwind v4, Supabase, Vercel, Stripe, RSS/API ingestion, Claude for synthesis

## 14 Sprints / 7 Stages

### Stage 0 (Sprint 0): Validation
- Find 8 analysts/VPs who track AI industry manually (newsletters, Twitter, HN)
- Ask: what do you miss? How long does your daily scan take?

### Stage 1 (Sprints 1-2): Foundation
- Sprint 1: Next.js scaffold, Supabase auth, sources + articles tables, dashboard shell
- Sprint 2: Source ingestion pipeline — RSS reader, HN API, GitHub Trending API, Product Hunt API. Store raw articles with metadata

### Stage 2 (Sprints 3-4): AI Synthesis
- Sprint 3: AI processing pipeline — Claude summarizes articles, extracts entities (companies, models, people), assigns categories and sentiment, detects trends
- Sprint 4: Daily brief generator — AI synthesizes top 10 signals into a structured morning brief. Email delivery via Resend

### Stage 3 (Sprints 5-6): Alerts & Search
- Sprint 5: Alert system — custom rules (keyword triggers, entity mentions, sentiment shifts, anomaly detection). Slack, email, webhook delivery
- Sprint 6: Search & filters — full-text search across articles, filter by source/category/entity/date, saved searches

### Stage 4 (Sprints 7-9): Dashboard
- Sprint 7: Main dashboard — real-time feed (filterable), trend charts, entity graph (who's connected to what)
- Sprint 8: Analytics — signal frequency by category, emerging topics (mentioned <3 times but accelerating), source reliability scoring
- Sprint 9: Team features — shared dashboards, annotations, discussion threads on signals, @mentions

### Stage 5 (Sprints 10-12): Revenue
- Sprint 10: Custom sources — users add their own RSS feeds, Twitter lists, Discord channels, Slack channels
- Sprint 11: Stripe billing — individual/team/enterprise tiers, API access for enterprise
- Sprint 12: API + export — REST API for programmatic access, CSV/JSON export, webhook events for new signals

### Stage 6 (Sprints 13-14): Scale
- Sprint 13: Second vertical template (supply chain OR crypto), vertical switcher in dashboard
- Sprint 14: Landing page, docs, pricing page, onboarding (pick vertical + configure sources)

## Key Contract Types

```typescript
export interface Signal {
  id: string;
  source_id: string;
  title: string;
  url: string;
  content_summary: string;
  ai_analysis: SignalAnalysis;
  category: 'model_release' | 'funding' | 'acquisition' | 'open_source' | 'regulatory' | 'research' | 'product_launch' | 'partnership';
  sentiment: 'positive' | 'neutral' | 'negative' | 'mixed';
  importance_score: number;  // 0-100
  entities: Entity[];
  published_at: string;
  processed_at: string;
}

export interface SignalAnalysis {
  summary: string;
  key_facts: string[];
  implications: string[];
  related_signals: string[];
  trend_category: string | null;
}

export interface Entity {
  name: string;
  type: 'company' | 'person' | 'model' | 'technology' | 'regulation';
  sentiment: 'positive' | 'neutral' | 'negative';
}

export interface Source {
  id: string;
  name: string;
  type: 'rss' | 'api' | 'scraper';
  url: string;
  reliability_score: number;  // 0-100
  refresh_interval_minutes: number;
  is_active: boolean;
}

export interface AlertRule {
  id: string;
  user_id: string;
  name: string;
  conditions: Array<{
    field: 'keyword' | 'entity' | 'category' | 'sentiment' | 'importance';
    operator: 'contains' | 'equals' | 'greater_than' | 'less_than';
    value: string;
  }>;
  channels: ('slack' | 'email' | 'webhook')[];
  is_active: boolean;
}

export interface DailyBrief {
  id: string;
  date: string;
  top_signals: Signal[];
  emerging_trends: string[];
  notable_entities: Array<{ name: string; mention_count: number; sentiment_trend: string }>;
  generated_at: string;
}
```

## Design Direction
- **Bloomberg meets Notion** — data-dense but beautiful, dark mode default
- **Primary:** #0A0A0A, **Accent:** #6366F1 (indigo for signals), #F97316 (orange for alerts)
- **Font:** Inter for body, Berkeley Mono for data
- **Key component:** Signal card with importance badge, entity tags, sentiment indicator, source attribution

## 50+ Pre-Seeded Sources (AI/ML Vertical)

### Tier 1 (High reliability, daily check)
- HN front page (API), arXiv CS papers (RSS), GitHub Trending (scraper)
- OpenAI blog, Anthropic blog, Google AI blog, Meta AI blog (RSS)
- TechCrunch AI section, The Verge AI (RSS)

### Tier 2 (Good signal, 2x daily)
- Product Hunt AI category, r/MachineLearning, r/LocalLLaMA (API)
- Hugging Face papers daily, Papers With Code trending (RSS)
- YC blog, a16z AI blog, Sequoia AI blog (RSS)

### Tier 3 (Emerging, 1x daily)
- AI Twitter lists (top 50 accounts), AI Discord summaries
- Changelog Nightly, TLDR AI newsletter (RSS)
- GitHub star-history for tracked repos

## Golden Jobs

### Job A — Morning Brief
> "It's 7am Monday. I want to know the 5 most important AI things that happened since Friday. Don't make me read 50 articles."

### Job B — Alert on Competitor Move
> "Alert me instantly (Slack) if OpenAI, Anthropic, or Google announces a new model, pricing change, or acquisition."

### Job C — Trend Detection
> "Show me topics that were mentioned <3 times last week but >10 times this week. Those are emerging trends."

### Job D — Team Intelligence
> "My VP of Product needs a weekly AI industry summary. Auto-generate and email it every Monday at 8am."
