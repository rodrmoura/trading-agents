# Gateway API Draft

This is a draft contract for the VS Code LLM gateway. It is not yet implemented.

## Goals

- Let local apps call models available inside VS Code.
- Keep the gateway local-only by default.
- Support streaming, cancellation, structured output compatibility, and clear errors.
- Keep the API reusable outside TradingAgents.

## Authentication

Every request should include a generated gateway token.

```text
Authorization: Bearer <gateway-token>
```

The extension should generate the token when the gateway starts and should not commit or print it in logs.

## Draft Endpoints

```text
GET  /health
GET  /v1/models
POST /v1/chat/completions
POST /v1/chat/completions/stream
POST /shutdown
```

The `/v1/chat/completions` shape may become OpenAI-compatible, native, or both. This is still an open decision.

Current direction: implement a native minimal API first, then add an OpenAI-compatible facade later if the native path proves useful.

## Model Listing Response

```json
{
  "models": [
    {
      "id": "vscode-model-id",
      "name": "Display Name",
      "vendor": "provider-or-family",
      "family": "optional-family",
      "capabilities": {
        "streaming": true,
        "toolCalling": false,
        "structuredOutput": false
      }
    }
  ]
}
```

## Error Categories

- `unauthorized`: missing or invalid gateway token.
- `model_not_found`: requested VS Code model is unavailable.
- `model_access_denied`: user consent or entitlement is missing.
- `quota_or_rate_limited`: model provider rejected due to quota/rate limits.
- `cancelled`: caller cancelled the request.
- `gateway_not_ready`: extension/gateway is not fully initialized.
- `unknown_model_error`: raw model call failed in an unexpected way.

## Open Decisions

- Should streaming use Server-Sent Events, newline-delimited JSON, or WebSocket?
- Should structured output be gateway-native or adapter-level only at first?
- How should tool calls be represented when VS Code model support varies by model?
