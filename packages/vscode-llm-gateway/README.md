# VS Code LLM Gateway

Placeholder for the VS Code extension and local gateway that exposes models available inside VS Code to local apps.

Expected future responsibilities:

- start and stop a localhost-only gateway from VS Code
- list available VS Code language models
- invoke selected models with streaming and cancellation
- expose useful errors for missing consent, unavailable models, quota, and policy limits
- protect local requests with generated token authentication

This package should not import TradingAgents.
