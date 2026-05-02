# Documentation Governance

Documentation is part of the engineering system. It preserves current truth, durable decisions, validation evidence, and handoff context without creating duplicate sources of truth.

## Canonical Governance Files

| File | Owns |
| --- | --- |
| `docs/WORKFLOW_HELPERS.md` | AI-agent workflow, model ownership, ledgers, review gates, lifecycle commands, and task triage |
| `.github/copilot-instructions.md` | Always-on repository behavior summary that points to canonical governance |
| `.github/instructions/documentation-system.instructions.md` | File-scoped documentation rules for `docs/**/*.md` |
| `.github/instructions/model-routing.instructions.md` | Always-on model ownership routing summary |
| `.github/agents/*.agent.md` | Callable role agents |
| `.github/prompts/*.prompt.md` | Thin slash-command prompt wrappers |
| `.github/skills/*/SKILL.md` | Slash-command workflow wrappers |

## Current Truth And History

| File | Owns | Default Resume Input |
| --- | --- | --- |
| `docs/repo_state/ACTIVE_STATE.md` | Current focus, mode, blockers, evidence snapshot, next actions, resume pointers | Yes |
| `docs/repo_state/PROVEN_KNOWLEDGE.md` | Durable current priors, stable facts, reopen rules, contested knowledge | Yes |
| `docs/DECISIONS.md` | Final governance and workflow decisions with rollback criteria | When decisions matter |
| `docs/EXPERIMENT_LOG.md` | Validation, benchmark, experiment, and readiness evidence | When evidence matters |
| `docs/CHANGELOG.md` | Historical session timeline between wraps | No |
| `docs/session_capsules/*.md` | Dense long-form handoff for complex sessions | Only when ACTIVE_STATE points to one |
| `docs/ROADMAP.md` | Medium-term priorities and parked work | Only when priority is unclear |

## Existing Project Docs

Existing project-specific docs remain valid when they own project scope, architecture, operations, or implementation plans. They should point to the canonical governance files instead of duplicating workflow rules.

Examples:

- `PROJECT-GUIDE.md`: project and architecture source of truth.
- `TODO.md`: active backlog.
- `CODING-STANDARDS.md`: implementation conventions.
- `SECURITY.md`: security rules.
- `DEPLOY.md`: setup and operation notes.
- `docs/architecture/**`: project architecture notes.
- `docs/planning/**`: project execution plans and task packets.
- `docs/decisions/**`: architecture decision records.

## Rules

- One fact gets one home.
- Use pointers instead of duplicating long rules.
- Resolve current truth first in `ACTIVE_STATE` and `PROVEN_KNOWLEDGE` when docs disagree.
- Do not store secrets, tokens, credentials, `.env` values, generated caches, or private local data in docs.
- Do not update historical docs from `/state-sync`; use `/session-wrap` for durable historical handoff.
- Do not read `docs/CHANGELOG.md` by default during resume.

## Update Triggers

- Workflow, agent, prompt, skill, routing, review, or ledger behavior changed: update `docs/WORKFLOW_HELPERS.md` and the relevant `.github/**` wrapper.
- Current focus, blockers, evidence, or next actions changed: update `docs/repo_state/ACTIVE_STATE.md`.
- Durable current priors changed: update `docs/repo_state/PROVEN_KNOWLEDGE.md`.
- Final governance/workflow decision changed: update `docs/DECISIONS.md`.
- Validation or experiment evidence changed materially: update `docs/EXPERIMENT_LOG.md`.
- Historical session handoff is needed: update `docs/CHANGELOG.md` and, for complex sessions, `docs/session_capsules/`.
- Product or project architecture changed: update the existing project-specific source of truth and add pointers here only when governance ownership changes.
