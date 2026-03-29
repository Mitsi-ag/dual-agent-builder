# Voice Agent Testing

**TEMPO Score: 21/25** (T:5 E:4 M:5 P:3 O:4)

## The Signal
Vapi has 500K devs and 300M+ calls but NO testing framework. You can't write a Playwright test for a phone call. Manual QA only. Every voice agent company is flying blind.

## The Gap
- No "Playwright for voice agents" exists at all
- Vapi has basic analytics, no regression testing
- Debugging voice agents means listening to recordings manually
- No CI integration for voice agent quality gates

## The Product
Define test scenarios (caller persona + expected outcome). Platform calls your voice agent, transcribes, scores against criteria. Run in CI before deploy.

### V1 Features
- Test scenario builder: define caller persona, script, expected outcomes
- Automated test calls via Twilio/Vapi API
- Whisper transcription + LLM scoring against criteria
- CI integration (GitHub Actions, etc.)
- Regression suite: run all tests before deploy
- Dashboard: pass/fail trends, latency, transcript viewer

## The Buyer
- Companies deploying voice agents (healthcare, insurance, customer service)
- Vapi/Bland/Retell customers
- QA teams responsible for voice AI quality

## Pricing
| Tier | Price |
|------|-------|
| Starter | $99/mo, 100 test calls |
| Pro | $299/mo, 1K test calls, regression suite |
| Enterprise | $999/mo, 10K calls, custom personas, SLA |
