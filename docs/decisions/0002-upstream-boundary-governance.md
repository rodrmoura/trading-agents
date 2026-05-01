# 0002: Upstream Boundary Governance

## Status

Accepted

## Context

This repository was cloned from `TauricResearch/TradingAgents`. We expect the upstream owner to continue updating it. At the same time, we plan to add our own reusable gateway, SDK, runtime, prompts, and eventually frontend.

If we mix generic platform code deeply into upstream-derived files, upstream updates will become hard to receive and our platform will inherit finance-specific assumptions.

## Decision

Treat TradingAgents code as upstream-derived and keep our generic platform code in separate folders or packages.

Patch upstream-derived files only when an integration boundary requires it. The first likely boundary is adding a `vscode` LLM provider that delegates to our generic Python SDK.

## Consequences

- Upstream syncs remain easier to reason about.
- Generic packages can serve future apps.
- We may need adapter layers that feel slightly indirect, but they preserve long-term flexibility.
- Any intentional divergence from upstream should be documented.
