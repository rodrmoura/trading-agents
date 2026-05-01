# Documentation Governance

Documentation is part of the engineering system for this project. It preserves decisions, keeps upstream-derived TradingAgents work separate from our generic platform work, and makes future sessions resumable from the repository itself.

## Source Of Truth Order

When documents conflict, resolve them in this order:

1. [PROJECT-GUIDE.md](PROJECT-GUIDE.md) - product scope, end goal, project boundaries, architecture direction, and launch constraints.
2. [TODO.md](TODO.md) - active implementation backlog and honest done/partial/not-done state.
3. [DOCS-GOVERNANCE.md](DOCS-GOVERNANCE.md) - documentation ownership, routing, update triggers, and drift control.
4. [docs/decisions](docs/decisions) - durable architecture and product decisions.
5. [CODING-STANDARDS.md](CODING-STANDARDS.md) - code, testing, integration, and boundary rules.
6. [SECURITY.md](SECURITY.md) - secrets, gateway access, model access, and data-handling rules.
7. [DEPLOY.md](DEPLOY.md) - local setup, gateway operation, package, and release runbooks.
8. [docs/architecture](docs/architecture) and [docs/guidance](docs/guidance) - supporting architecture and working guidance.
9. [.github/copilot-instructions.md](.github/copilot-instructions.md) and [.github/skills](.github/skills) - agent guidance and lifecycle commands.
10. [README.md](README.md) - upstream TradingAgents summary and user-facing quick start.
11. [PROJECT-CHANGELOG.md](PROJECT-CHANGELOG.md) - notable repository-visible changes for our local platform work.

The project guide wins on product and architecture. This file wins on documentation routing and maintenance rules.

## Document Classes

| Class | Files | Purpose |
| --- | --- | --- |
| Product truth | `PROJECT-GUIDE.md` | Defines what we are building and why |
| Planning | `TODO.md` | Tracks active work, done, partial, blocked, and next |
| Governance | `DOCS-GOVERNANCE.md`, `CONTRIBUTING.md`, `.github/copilot-instructions.md`, `.github/skills/**` | Controls how work and agents stay aligned |
| Engineering rules | `CODING-STANDARDS.md`, `SECURITY.md` | Defines safe implementation patterns |
| Operations | `README.md`, `DEPLOY.md`, `.env.example` | Helps run, test, package, and operate the app/gateway |
| Decisions | `docs/decisions/*.md` | Records durable choices, tradeoffs, consequences, and revisit triggers |
| Architecture notes | `docs/architecture/*.md` | Explains active architecture and project structure |
| Guidance | `docs/guidance/*.md` | Captures working practices such as Copilot and skill usage |
| History | `PROJECT-CHANGELOG.md` | Tracks notable local platform changes |

## Update Triggers

Update documentation in the same change when work affects any of these areas:

- Product scope, project boundaries, platform goals, frontend vision, or launch criteria: update `PROJECT-GUIDE.md` and `TODO.md`.
- Upstream boundary, fork/subtree strategy, folder ownership, or dependency direction: update `PROJECT-GUIDE.md`, `DOCS-GOVERNANCE.md`, and `docs/architecture/code-governance.md`.
- VS Code gateway API, auth token model, model selection, streaming, tool calling, or structured output: update `PROJECT-GUIDE.md`, `TODO.md`, `SECURITY.md`, `DEPLOY.md`, and an ADR when the decision is durable.
- Generic agent runtime, manifest schema, tool registry, memory, checkpoints, or workflow graph model: update `PROJECT-GUIDE.md`, `TODO.md`, `CODING-STANDARDS.md`, and an ADR.
- Local setup, extension packaging, Python SDK installation, environment variables, service URLs, or developer commands: update `README.md`, `DEPLOY.md`, `.env.example` if relevant, and `TODO.md`.
- Agent workflow, slash command, skill, or Copilot behavior: update `.github/copilot-instructions.md`, `.github/skills/README.md`, the relevant skill, `docs/guidance/copilot-and-skills.md`, `TODO.md`, and `PROJECT-CHANGELOG.md`.
- Repository-visible changes future sessions should remember: update `PROJECT-CHANGELOG.md` under `[Unreleased]`.

## Writing Rules

- Prefer one canonical source over duplicated prose. Link or summarize from lower-priority docs.
- Mark status honestly: done only after verification, partial when implementation exists but readiness is incomplete, blocked when a decision or dependency is missing.
- Keep docs concise. Do not paste chat transcripts or noisy command output.
- Do not store secrets, `.env` values, gateway tokens, provider keys, credentials, customer data, or generated local caches in markdown.
- Keep upstream TradingAgents release notes separate from our local platform history.
- Use ADRs for durable choices with meaningful alternatives.

## Lifecycle Commands

Use the workspace skills as the documentation maintenance workflow:

- `/session-resume`: read docs, fetch/pull safely, and present next steps. It should not edit docs.
- `/state-sync`: lightweight in-progress checkpoint. It may update `TODO.md`, `PROJECT-CHANGELOG.md`, and related docs, but must not pull or commit.
- `/session-wrap`: final session closure. It must perform final markdown sync, validate, review staged paths, and commit when appropriate.

See [.github/skills/README.md](.github/skills/README.md) for the lifecycle matrix.

## Review Checklist

Before finishing a documentation-impacting change:

- Did `PROJECT-GUIDE.md` remain the source of truth for product and architecture?
- Did `TODO.md` reflect actual done, partial, blocked, and next work?
- Did `PROJECT-CHANGELOG.md` capture notable local platform changes without noise?
- Did setup or operations changes update `README.md`, `DEPLOY.md`, and `.env.example` as needed?
- Did security or gateway-access changes update `SECURITY.md` or `CODING-STANDARDS.md`?
- Did durable decisions get an ADR?
- Did touched markdown pass diagnostics and `git diff --check`?
