# 0001: Two-Project Roadmap

## Status

Accepted

## Context

We want TradingAgents to run using models available inside VS Code. We also want to build, later, a generic agent ecosystem where specialized agents collaborate toward shared goals.

These goals are related but should not be collapsed into one large upfront rewrite.

## Decision

Split the work into two related projects:

1. Put TauricResearch/TradingAgents to work with the VS Code LLM gateway/extension.
2. Build a generalized, manifest-driven agent collaboration platform using TradingAgents as the first workflow template.

## Consequences

- The VS Code gateway can be reused by future apps.
- TradingAgents remains the first vertical slice, not the whole platform.
- We delay broad framework abstractions until one real workflow works through the gateway.
- We need clear code boundaries so generic platform code does not become finance-specific.
