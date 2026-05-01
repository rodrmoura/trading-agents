# 0003: VS Code Model Gateway

## Status

Proposed

## Context

VS Code exposes available chat models through the extension API, not through a normal Python package. Local Python apps cannot directly call `vscode.lm.selectChatModels()` or `LanguageModelChat.sendRequest(...)`.

TradingAgents is Python-based and currently uses LangChain model clients. Future apps may be Python, Node, or another stack.

## Decision

Build a reusable VS Code extension that exposes a localhost-only model gateway. Local apps call the gateway through a small SDK or OpenAI-compatible endpoint. The extension calls the VS Code Language Model API.

Initial target shape:

```text
local app
  -> localhost gateway API
  -> VS Code extension
  -> VS Code Language Model API
```

## Requirements

- Start only through explicit user action in VS Code.
- Bind to `127.0.0.1` by default.
- Use a generated token for local requests.
- List available models.
- Send chat requests and stream text responses.
- Surface model permission, quota, and availability errors clearly.
- Add structured output and tool calling after the basic invocation path works.

## Open Questions

- Should the first public API be OpenAI-compatible, native gateway-specific, or both?
- Should app-specific tools execute in the app process, the extension process, or both?
- How should model selection be represented when VS Code model identifiers change over time?
- Should the extension include a frontend control room, or should the control room be a separate app?
