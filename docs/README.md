# Project Documentation

This folder captures the working decisions, architecture guidance, and operating rules for our TradingAgents-based agent platform work.

The project has two tracks:

1. Put TauricResearch/TradingAgents to work with the VS Code LLM gateway/extension.
2. Create a generalized agent collaboration platform for future multi-agent applications.

## Start Here

- [Project Guide](../PROJECT-GUIDE.md)
- [TODO](../TODO.md)
- [Documentation Governance](../DOCS-GOVERNANCE.md)
- [Project Vision](architecture/project-vision.md)
- [Code Governance](architecture/code-governance.md)
- [Repository Layout](architecture/repository-layout.md)
- [Repository Strategy](architecture/repository-strategy.md)
- [Roadmap](architecture/roadmap.md)
- [Copilot and Skills Guidance](guidance/copilot-and-skills.md)
- [Session Lifecycle Skills](../.github/skills/README.md)

## Architecture Decision Records

- [0001: Two-Project Roadmap](decisions/0001-two-project-roadmap.md)
- [0002: Upstream Boundary Governance](decisions/0002-upstream-boundary-governance.md)
- [0003: VS Code Model Gateway](decisions/0003-vscode-model-gateway.md)
- [0004: Two-Repository Strategy](decisions/0004-two-repository-strategy.md)
- [ADR Template](decisions/ADR-TEMPLATE.md)

## Reference Drafts

- [Gateway API Draft](reference/gateway-api-draft.md)
- [Agent Manifest Draft](reference/agent-manifest-draft.md)

## Runbooks

- [Documentation Validation](runbooks/docs-validation.md)
- [Upstream Sync](runbooks/upstream-sync.md)

## Documentation Rules

- Record durable decisions in `docs/decisions/`.
- Record working guidance in `docs/guidance/`.
- Record operational procedures in `docs/runbooks/`.
- Record stable contracts and inventories in `docs/reference/`.
- Use [Project Guide](../PROJECT-GUIDE.md) as the source of truth for product and architecture direction.
- Use [Documentation Governance](../DOCS-GOVERNANCE.md) to decide which files to update.
- Keep upstream-derived TradingAgents changes documented in [Code Governance](architecture/code-governance.md) until we add a dedicated patch log.
- Prefer small, explicit docs over broad speculative design documents.
