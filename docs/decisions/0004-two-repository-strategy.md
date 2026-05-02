# 0004: Two-Repository Strategy

## Status

Accepted

## Context

We are doing two related projects in one workspace:

1. Put TauricResearch/TradingAgents to work with the VS Code LLM gateway/extension.
2. Create a generalized agent collaboration platform for future multi-agent applications.

The first project needs to stay close to the upstream TradingAgents repository. The second project needs to remain reusable and free of TradingAgents-specific finance assumptions.

## Options Considered

- Keep everything in one fork or mirror of TradingAgents.
- Create one parent monorepo with TradingAgents and the platform inside it.
- Use two repositories: one TradingAgents integration repo and one generalized platform repo.

## Decision

Use two repositories.

The first repository will track TauricResearch/TradingAgents and hold our integration work. The second repository will be created after the TradingAgents gateway vertical slice works here and reusable code is ready to extract or start cleanly.

The planned name for the second repository is `agent-collaboration-platform`.

## Consequences

- Upstream TradingAgents updates stay easier to receive and review.
- Generic platform code can evolve without depending on TradingAgents internals.
- We need clear rules for moving reusable code from the integration repo into the platform repo.
- We need to avoid pushing local governance or integration changes to the upstream TauricResearch repository.

## Revisit Triggers

- The integration repo becomes mostly platform code.
- The platform repo needs TradingAgents test fixtures or examples.
- A parent monorepo becomes simpler than two repositories.
- Licensing or provenance concerns require a different split.
