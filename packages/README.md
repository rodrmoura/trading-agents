# Packages

Reusable packages incubate here while this integration repo proves the first vertical slice.

Long term, reusable packages should move to the generalized agent collaboration platform repository.

## Current Structure

- `vscode-llm-gateway/`: VS Code extension and local model gateway.
- `llm-gateway-python/`: Python SDK and LangChain-compatible adapter.
- `agent-schemas/`: shared contracts for agents, tools, workflows, events, artifacts, and memory.
- `agent-runtime/`: generalized workflow runtime built on the shared contracts.

## Boundary

Packages must not import `tradingagents/` or `cli/`. If a package needs TradingAgents-specific behavior, put that behavior in `apps/tradingagents-adapter/`.
