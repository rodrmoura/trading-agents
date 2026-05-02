# Copilot Instructions

Use `docs/WORKFLOW_HELPERS.md` as the canonical AI-agent governance contract for this repository.

## Model Ownership

- GPT owns reasoning, planning, architecture, debugging strategy, research, documentation governance, task shaping, and review.
- Codex owns code-writing implementation only after GPT produces a ready `Coding-Agent Task Ledger`.
- PhD Critic owns read-only devil's-advocate review.
- Reasoning route: GPT 5.5. Use high reasoning by default and xhigh reasoning for ambiguous, architecture-heavy, high-risk, cross-repository, security-sensitive, or broad work.
- Coding route: Codex 5.3. Use high reasoning for routine implementation and xhigh reasoning for complex, high-risk, cross-module, security-sensitive, framework-level, or routing-sensitive implementation.
- Critic route: Opus 4.7. Fallback routes, in order, are Opus 4.6 and Sonnet 4.6. Always use maximum reasoning for critic work, inspections, audits, quality gates, and implementation reviews.
- If the required GPT, Codex, or critic route is unavailable, stop and ask instead of silently falling back.

## General Task Triage

A request is gated if it:

- may edit more than one file
- creates, deletes, renames, or moves files
- touches runtime behavior, tests, CI, build, config, schema, docs-current-truth, workflows, commands, deployment, review, audit, or failed-test behavior
- asks for planning, architecture, strategy, review, audit, optimization, bug check, or "make this better"
- follows a failed attempt or user correction
- is ambiguous

Fast path is allowed only when all are true:

- one file
- mechanically obvious change
- no runtime/config/schema/test/workflow/current-truth surface
- no behavior change
- no ambiguity

For gated work:

1. GPT reasons and creates a plan/ledger.
2. PhD Critic reviews substantive plans before implementation.
3. Codex implements exactly one ready ledger.
4. PhD Critic reviews Codex implementation.
5. GPT accepts the result or creates the next patch ledger.
6. Persist with `/state-sync` or `/session-wrap` if needed.

## Repository-Specific Boundaries

- Treat upstream-derived source folders as externally owned unless a ready ledger explicitly permits a narrow integration patch.
- Keep reusable package work independent from app-specific internals.
- Prefer small reversible changes and current project style.
- Do not commit secrets, local tokens, credentials, generated caches, or environment values.
- Do not commit, branch, push, reset, revert, merge, rebase, or stash unless explicitly asked.

## Documentation

- `docs/repo_state/ACTIVE_STATE.md` and `docs/repo_state/PROVEN_KNOWLEDGE.md` are the first resume sources.
- `docs/WORKFLOW_HELPERS.md` owns governance workflow and ledger rules.
- `docs/DECISIONS.md`, `docs/EXPERIMENT_LOG.md`, `docs/CHANGELOG.md`, and `docs/ROADMAP.md` own the roles defined in `docs/WORKFLOW_HELPERS.md`.
- Keep one fact in one home; use pointers instead of duplicated long prose.
