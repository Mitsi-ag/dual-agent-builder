# Agent Regression Preventer

**TEMPO Score: 22/25** (T:5 E:4 M:4 P:5 O:4)

## The Signal
Every team using AI coding tools (Claude Code, Cursor, Codex) hits the same problem: the AI makes the same mistakes across sessions. CLAUDE.md and PATTERNS.md are manual solutions. This automates them.

## The Gap
- superpowers/CLAUDE.md: manual pattern files, no enforcement
- Pre-commit hooks: catch syntax, not semantic patterns
- Code review: catches issues after the fact, not before
- No tool watches git history + test failures and injects warnings into agent context

## The Product
MCP server that builds a knowledge graph of your repo's anti-patterns. When an AI agent is about to make a change that matches a known-bad pattern, it injects a warning into the agent's context.

### V1 Features
- MCP server that connects to Claude Code / Cursor / Codex
- Parses git history: reverted commits, repeated test failures, review comments
- Builds structured anti-pattern registry (like PATTERNS.md but automatic)
- Real-time warning injection when agent approaches known-bad code patterns
- Dashboard: pattern frequency, most costly patterns, trend over time
- Team features: cross-repo pattern sharing

## The Buyer
- Engineering teams with 10+ devs using AI coding tools
- Platform engineering teams standardizing AI tool usage
- Enterprises worried about AI code quality and consistency

## Pricing
| Tier | Price |
|------|-------|
| Free | 1 repo, personal use |
| Team | $29/dev/mo, 10 repos |
| Enterprise | $99/dev/mo, unlimited, analytics, SSO |

## The Moat
- Accumulated knowledge per repo (deeper over time, can't replicate)
- Cross-repo pattern learning (network effects)
- Integration with every major AI coding tool
