---
applyTo: "**"
---

# Model Ownership Routing

Canonical contract: `docs/WORKFLOW_HELPERS.md` under `Model Ownership Policy`, `Agent Routing`, `Plan Critic Gate`, and `Codex Implementation Review`.

Summary:

- GPT owns reasoning, planning, architecture, debugging strategy, research, documentation governance, task shaping, and review.
- Codex owns code-writing implementation only after GPT produces a ready `Coding-Agent Task Ledger`.
- PhD Critic owns read-only devil's-advocate review.
- Reasoning route: GPT 5.5. Use high reasoning by default and xhigh reasoning for ambiguous, architecture-heavy, high-risk, cross-repository, security-sensitive, or broad work.
- Coding route: Codex 5.3. Use high reasoning for routine implementation and xhigh reasoning for complex, high-risk, cross-module, security-sensitive, framework-level, or routing-sensitive implementation.
- Critic route: Opus 4.7. Fallback routes, in order, are Opus 4.6 and Sonnet 4.6. Always use maximum reasoning for critic work, inspections, audits, quality gates, and implementation reviews.
- Codex must not receive vague implementation requests.
- PhD Critic findings are recommendations to GPT, not direct Codex instructions.
- If the required route is unavailable, stop and ask instead of silently falling back.

This instruction does not hot-swap the model of an already-running top-level chat.
