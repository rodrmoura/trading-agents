# Apps

App-level integration shells live here.

This directory is for code that composes reusable packages into a runnable workflow or user-facing surface. It may contain TradingAgents-specific adapters and future UI prototypes.

## Current Structure

- `tradingagents-adapter/`: TradingAgents-specific integration shell.
- `control-room/`: future frontend prototype for observing and steering agent collaboration.

## Boundary

Reusable runtime, gateway, SDK, schema, memory, and tool abstractions should move into `packages/`. TradingAgents-specific orchestration belongs in `apps/tradingagents-adapter/` or narrow upstream-derived patches.
