# BasVoice — Voice Agent Testing Platform

> Paste this into Claude Code to generate planning docs and build the product.
> Then run: `python3 .buildrunner/run.py unattended`

---

## Product Vision

BasVoice is "Playwright for voice agents." Define test scenarios, BasVoice calls your voice agent, transcribes the conversation, and scores against your criteria. Run in CI before every deploy.

**Tagline:** "Test your voice agents before your customers do."

## Tech Stack
Next.js 15, TypeScript, Tailwind v4, Supabase, Vercel, Stripe, Twilio (for test calls), Groq Whisper (transcription)

## 14 Sprints / 7 Stages

### Stage 0 (Sprint 0): Validation
- Find 8 companies deploying voice agents (Vapi, Bland, Retell customers)
- Ask: how do you test? (Answer: they don't, or they call themselves)

### Stage 1 (Sprints 1-2): Foundation
- Sprint 1: Next.js scaffold, Supabase auth, test_suites + test_scenarios tables, dashboard shell
- Sprint 2: Scenario builder — define caller persona, conversation script, expected outcomes, scoring rubric

### Stage 2 (Sprints 3-4): Core Testing
- Sprint 3: Test executor — Twilio calls the target voice agent number, streams audio to/from an AI caller persona (Claude), records full conversation
- Sprint 4: Scoring engine — Whisper transcribes conversation, Claude scores against rubric (task completion, tone, accuracy, handling edge cases), generates pass/fail report

### Stage 3 (Sprints 5-6): Automation
- Sprint 5: Test suite runner — run multiple scenarios sequentially, aggregate results, generate suite report
- Sprint 6: CI integration — GitHub Actions workflow, webhooks for test triggers, status badges, PR comments with results

### Stage 4 (Sprints 7-9): Dashboard
- Sprint 7: Results dashboard — test history, pass/fail trends, conversation transcript viewer with annotations
- Sprint 8: Analytics — latency analysis, response quality trends, regression detection (score drops between versions)
- Sprint 9: Persona library — pre-built caller personas (angry customer, confused elderly, non-native speaker, impatient exec)

### Stage 5 (Sprints 10-12): Revenue
- Sprint 10: Team features — shared test suites, per-team results, comparison between voice agent versions
- Sprint 11: Stripe billing — per-test-call pricing, monthly plans, usage dashboard
- Sprint 12: API — REST API for triggering tests programmatically, webhook events, Slack integration

### Stage 6 (Sprints 13-14): Scale
- Sprint 13: Multi-provider support (Vapi, Bland, Retell, Twilio, custom SIP), parallel test execution
- Sprint 14: Landing page, docs, CI setup guide, pricing page, onboarding wizard

## Key Contract Types

```typescript
export interface TestScenario {
  id: string;
  suite_id: string;
  name: string;
  persona: CallerPersona;
  script: ConversationScript;
  scoring_rubric: ScoringRubric;
  target_phone_number: string;
  max_duration_seconds: number;
  created_at: string;
}

export interface CallerPersona {
  name: string;
  age_range: string;
  personality: string;  // "impatient", "confused", "friendly"
  accent: string | null;
  background_noise: string | null;
  speaking_style: string;
}

export interface ConversationScript {
  opening: string;
  objectives: string[];
  edge_cases: string[];
  exit_condition: string;
}

export interface ScoringRubric {
  criteria: Array<{
    name: string;
    description: string;
    weight: number;
    pass_threshold: number;
  }>;
}

export interface TestResult {
  id: string;
  scenario_id: string;
  status: 'running' | 'completed' | 'failed' | 'timeout';
  transcript: TranscriptEntry[];
  scores: Array<{ criterion: string; score: number; pass: boolean; explanation: string }>;
  overall_score: number;
  overall_pass: boolean;
  duration_seconds: number;
  recording_url: string | null;
  created_at: string;
}

export interface TranscriptEntry {
  speaker: 'agent' | 'caller';
  text: string;
  timestamp_ms: number;
  sentiment: 'positive' | 'neutral' | 'negative' | null;
}
```

## Design Direction
- **Clean, QA-tool aesthetic** — like Playwright's test report viewer
- **Primary:** #1A1A2E, **Accent:** #16A34A (green for pass), #DC2626 (red for fail)
- **Font:** Inter for body, JetBrains Mono for transcripts
- **Key component:** Conversation timeline with speaker bubbles, score badges, waveform visualization

## Golden Jobs

### Job A — Test an Appointment Booking Agent
> "My voice agent books dental appointments. Test: caller wants Thursday 2pm, agent should check availability, offer alternatives if full, confirm booking."

### Job B — Regression Test After Prompt Change
> "I updated my agent's system prompt. Run last week's test suite to make sure nothing broke."

### Job C — Edge Case: Angry Customer
> "Test my support agent with an angry caller who demands a refund. Agent should de-escalate, not promise anything unauthorized."

### Job D — CI Gate
> "Block my deploy if any test scenario scores below 70%. Add a GitHub Actions step."
