# Copilot And Skills Guidance

This document is a lightweight index for repository-local assistant customization. It does not own the long workflow rules.

## Canonical Sources

- `docs/WORKFLOW_HELPERS.md`: model ownership, task triage, Coding-Agent Task Ledger, Plan Critic Gate, Codex implementation review, lifecycle commands, and PhD Critic contract.
- `.github/copilot-instructions.md`: always-on repository behavior summary.
- `.github/agents/README.md`: callable agent inventory.
- `.github/skills/README.md`: slash-command skill inventory.
- `.github/prompts/*.prompt.md`: thin prompt wrappers.
- `.github/instructions/*.instructions.md`: scoped instruction files.

## Active Customizations

| Surface | Purpose |
| --- | --- |
| `.github/agents/reasoning-engineer.agent.md` | GPT-owned reasoning, planning, documentation governance, ledgers, and review coordination |
| `.github/agents/codex-coding-engineer.agent.md` | Codex-owned implementation from one ready ledger |
| `.github/agents/phd-critic.agent.md` | Read-only devil's-advocate review |
| `.github/skills/session-resume/SKILL.md` | Start-of-session current-truth restore |
| `.github/skills/state-sync/SKILL.md` | Minimal current-truth checkpoint |
| `.github/skills/session-wrap/SKILL.md` | Durable session handoff |
| `.github/skills/phd-critic/SKILL.md` | Read-only critic slash command |
| `.github/skills/phd-quality-gate/SKILL.md` | Full readiness workflow |

## Discovery Rule

Open VS Code at the repository root when using this project's custom agents, prompts, or slash commands. Do not duplicate repo-local skills into a parent workspace unless explicitly approved.

## Model Routes

- Reasoning Engineer uses GPT 5.5, with high or xhigh reasoning depending on complexity.
- Codex Coding Engineer uses Codex 5.3, with high or xhigh reasoning depending on complexity.
- PhD Critic uses Opus 4.7, with Opus 4.6 and Sonnet 4.6 as fallback routes.
- Always use maximum reasoning for critic work, inspections, audits, quality gates, and implementation reviews.
