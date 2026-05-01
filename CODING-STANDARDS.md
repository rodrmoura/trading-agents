# Coding Standards

## Core Rules

- Keep changes minimal, focused, and consistent with the existing codebase.
- Fix root causes instead of layering surface patches.
- Do not rewrite upstream-derived TradingAgents files unless the integration requires it.
- Document every intentional upstream-derived patch.
- Keep generic packages free of finance-specific assumptions.
- Never commit secrets, `.env` values, local gateway tokens, provider API keys, generated caches, or build artifacts.

## Upstream-Derived Code

`tradingagents/` and `cli/` are upstream-derived. Patches should be narrow and adapter-oriented.

Preferred first patch pattern:

```text
TradingAgents LLM factory
  -> provider = "vscode"
  -> generic Python SDK or LangChain adapter
  -> VS Code model gateway
```

Avoid scattering gateway logic across analyst, researcher, trader, and manager agents.

## Generic Packages

Future generic packages should live under `packages/` and should not import TradingAgents internals.

Expected packages:

- `packages/vscode-llm-gateway/`
- `packages/llm-gateway-python/`
- `packages/agent-runtime/`
- `packages/agent-schemas/`

## Python Standards

- Follow the style already present in TradingAgents for upstream-derived patches.
- Prefer typed function signatures when adding new generic code.
- Keep provider adapters small and testable.
- Add focused tests for model selection, structured output, tool-call conversion, and error handling.
- Use environment variables only for configuration; never hardcode credentials.

## VS Code Extension Standards

- Use TypeScript for extension code.
- Keep the extension responsible for VS Code API access, consent-aware model calls, and local gateway lifecycle.
- Keep app-specific business logic outside the extension.
- Bind the gateway to `127.0.0.1` by default.
- Require a generated token for local requests.
- Surface model errors clearly: no permission, model not found, blocked/quota, cancellation, and unknown failures.

## Agent Runtime Standards

- Agents must have explicit roles, allowed tools, input contracts, output contracts, memory scope, and stopping conditions.
- Workflows should be graph-defined, not ad hoc chat chains.
- Prefer structured outputs for manager/decision agents.
- Preserve event logs so a future frontend can replay what happened.

## Validation

Choose validation based on changed files and risk.

For documentation-only changes:

- `git diff --check`
- markdown diagnostics when available
- non-ASCII scan when the touched docs are expected to remain ASCII

For Python changes:

- targeted `pytest` for touched behavior
- full tests when shared behavior changes
- import smoke checks for new modules

For VS Code extension changes:

- TypeScript compile/check
- extension tests when available
- manual gateway smoke for model listing, auth, streaming, cancellation, and errors
