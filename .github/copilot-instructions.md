# Copilot Instructions

This repository is an upstream-derived TradingAgents workspace that we are using as the first proving ground for a broader reusable agent platform. Treat it as two projects in one: the Tauric VS Code LLM integration and the generalized agent collaboration platform.

## Project Direction

- Project 1: put TauricResearch/TradingAgents to work with the VS Code LLM gateway/extension.
- Project 2: create a generalized agent collaboration platform for future multi-agent applications.
- TradingAgents is the first integrated ecosystem, not the foundation of every future abstraction.
- Always preserve the distinction between TradingAgents-specific integration work and reusable platform work.

## Code Boundaries

- Treat `tradingagents/` and `cli/` as upstream-derived code.
- Keep patches to upstream-derived code narrow and integration-focused.
- Prefer new generic code in `packages/`, `apps/`, `prompts/`, and `docs/`.
- Generic packages must not import TradingAgents internals.
- Adapter code may depend on both generic packages and TradingAgents.

## Documentation

- Treat `PROJECT-GUIDE.md` as the product and architecture source of truth.
- Treat `TODO.md` as the active backlog.
- Use `DOCS-GOVERNANCE.md` to decide which docs to update.
- Record durable architecture choices as ADRs in `docs/decisions/`.
- Update `docs/architecture/code-governance.md` when code ownership boundaries change.
- Update `docs/guidance/copilot-and-skills.md` before importing or adapting instructions from other repositories.

## Upstream Governance

- Keep upstream syncs separate from feature work.
- Do not casually rewrite upstream-derived files.
- If an upstream-derived file is patched, document why.

## Agent Platform Guidance

- Agents should have explicit roles, inputs, outputs, tools, memory scope, and stopping conditions.
- Avoid finance assumptions in generic runtime, gateway, SDK, and schema code.
- Prefer manifest-driven workflow design over hardcoded agent teams when building generic features.

## Security And Secrets

- Never commit API keys, local gateway tokens, generated caches, or credential files.
- VS Code gateway work should default to localhost-only access and explicit user consent.
