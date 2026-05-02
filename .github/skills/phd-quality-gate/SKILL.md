---
name: phd-quality-gate
description: "Use when: full readiness review before commit, deploy, release, major refactor, compaction, sanity-check everything, or make current work better."
argument-hint: "pre-commit | full-review | quality-gate"
user-invocable: true
disable-model-invocation: false
---

# PhD Quality Gate

Canonical contract: `docs/WORKFLOW_HELPERS.md` under `PhD Quality Gate`.

Critic route: Opus 4.7. Fallback routes, in order, are Opus 4.6 and Sonnet 4.6. Always use maximum reasoning for critic work, inspections, audits, quality gates, and implementation reviews.

## Procedure

1. Start with PhD Critic read-only review.
2. Convert accepted findings into GPT-owned plans or Codex ledgers.
3. Run relevant tests/checks where tools allow.
4. Close or explicitly defer findings.
5. Finish with `/state-sync` or `/session-wrap` when current truth changed.

## Validation Strength Labels

- `V0 read`: read-only review
- `V1 static`: static checks, grep, metadata validation, syntax checks
- `V2 targeted`: focused tests or smoke checks
- `V3 integration`: broader integration tests
- `V4 runtime`: real runtime validation
- `V5 production`: production or release-environment validation
