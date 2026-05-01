# TradingAgents Adapter

This app layer is for TradingAgents-specific wiring that should not live inside reusable packages.

Expected responsibilities:

- connect TradingAgents provider selection to the VS Code LLM gateway SDK
- hold integration smoke checks that exercise TradingAgents through the gateway
- keep finance/workflow-specific adapter code outside generic packages
- document any unavoidable upstream-derived patches

Do not build generic runtime abstractions here. Move reusable pieces into `packages/` and eventually into the generalized agent collaboration platform repo.
