# Deploy And Operations

## Current State

There is no deployable platform yet. This repository currently contains upstream TradingAgents plus local governance docs for planned work.

## Local TradingAgents

Use the upstream instructions in [README.md](README.md) for the current TradingAgents CLI and Docker usage.

Typical local install path:

```powershell
pip install .
tradingagents analyze
```

Provider API keys are required for the upstream provider path until the VS Code gateway integration exists.

## Future VS Code Gateway Operations

The future gateway should be operated from VS Code:

```text
Command Palette -> Start VS Code Model Gateway
```

Expected local behavior:

- Starts a local HTTP server bound to `127.0.0.1`.
- Displays host, port, and token handling guidance.
- Lists models available through VS Code.
- Provides a stop command.
- Does not expose the gateway to the LAN by default.

## Future Package Layout

Expected packages:

```text
packages/vscode-llm-gateway/   # VS Code extension
packages/llm-gateway-python/   # Python SDK and LangChain adapter
packages/agent-runtime/        # Generic runtime
apps/tradingagents-adapter/    # Optional adapter app
```

## Validation Runbooks

Documentation-only changes:

Use [docs/runbooks/docs-validation.md](docs/runbooks/docs-validation.md).

Python changes:

```powershell
pytest
```

VS Code extension changes will need package-specific commands after the extension package exists.

## Production Readiness

This project is not production-ready. Before any broader use, define:

- gateway packaging and signing expectations
- token storage and rotation behavior
- telemetry/logging policy
- model access error handling
- tool permission model
- release process
