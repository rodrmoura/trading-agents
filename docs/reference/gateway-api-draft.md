# Gateway API Draft

This is the draft/native contract for the VS Code LLM gateway. Phase 1 text chat and P3.3b non-streaming native tool-call roundtrip are implemented; later structured-output and OpenAI-compatible facade work remains separate.

## Goals

- Let local apps call models available inside VS Code.
- Keep the gateway local-only by default.
- Support streaming, cancellation, structured output compatibility, and clear errors.
- Keep the API reusable outside TradingAgents.

## Authentication

Every protected request uses a generated gateway token.

```text
Authorization: Bearer <gateway-token>
```

The extension generates the token when the gateway starts. It must not commit, persist, print, log, or return the token from HTTP endpoints.

Phase 1 accepts tokens only in the `Authorization: Bearer <gateway-token>` header. Do not accept gateway tokens in query strings, request bodies, cookies, alternate headers, or path segments. Missing, malformed, or wrong tokens return `401 unauthorized` with the native error envelope. Never log raw `Authorization` header values.

## Draft Endpoints

```text
GET  /health
GET  /v1/models
POST /v1/chat/completions
POST /v1/chat/completions/stream
POST /shutdown
```

Current direction: implement a native minimal API first, then add an OpenAI-compatible facade later if the native path proves useful.

## Native Locked Contract

The gateway uses a native minimal API only. Do not implement an OpenAI-compatible facade, structured-output enforcement, WebSockets, newline-delimited JSON streaming, or permissive CORS in the native gateway path.

The `/v1/chat/completions` path name does not imply OpenAI API compatibility. Do not return OpenAI-style response wrappers, streaming sentinels, or OpenAI tool field names. The native non-streaming response keeps the locked `usage: null` field and uses native `message.toolCalls` only when the model returns tool calls.

Endpoint semantics:

- `GET /health` is public and returns only non-sensitive gateway status.
- `GET /v1/models` requires `Authorization: Bearer <gateway-token>`.
- `POST /v1/chat/completions` requires bearer auth and is non-streaming only. It supports native tool-call request/response roundtrips.
- `POST /v1/chat/completions/stream` requires bearer auth and is text-only in P3.3b.
- `POST /shutdown` requires bearer auth. The VS Code stop command is still the primary shutdown path.
- `POST /v1/chat/completions` rejects `stream` and other unknown top-level fields with `validation_error`.
- `POST /v1/chat/completions/stream` rejects top-level `tools`, assistant `toolCalls`, and `role: "tool"` messages with `validation_error` before model invocation.
- Wrong methods for known endpoints return `405 method_not_allowed` through the native error envelope.
- In P1.2, known future protected paths may return `501 not_implemented`, but only after bearer auth succeeds.

Token lifecycle:

- The extension generates a random memory-only token each time the gateway starts.
- Token generation happens only after the HTTP server successfully binds.
- The token is never persisted, never logged, and never returned by HTTP endpoints.
- The token invalidates on stop, authenticated shutdown, and extension deactivation.
- Restarting the gateway rotates the token.
- Starting while already running is idempotent and does not rotate the token.
- `copyToken` fails gracefully when no running gateway token exists and must not start the gateway implicitly.
- The token may be copied only through an explicit VS Code user command or explicit button action in a VS Code notification/status flow.

Gateway states:

- `stopped`: no server, no token, no selected port.
- `starting`: start command is binding the server; no token is exposed until bind succeeds.
- `running`: server has host, port, token, and started timestamp.
- `stopping`: stop or shutdown is closing the server and cancelling active requests on a best-effort basis.
- `failed`: start failed; no token is exposed and state returns to `stopped` after reporting the sanitized failure.

Lifecycle rules:

- Extension activation registers commands only; it must not start networking or call VS Code language model APIs.
- Start command creates the server and token only; it must not call language model APIs.
- Model listing may call `vscode.lm.selectChatModels({})` when an authenticated `/v1/models` request arrives.
- Chat endpoints may call `LanguageModelChat.sendRequest` when an authenticated HTTP chat request arrives.
- Deactivation stops the server and invalidates the token. Stop and shutdown cancel in-flight requests on a best-effort basis.
- Starting while already running is idempotent and reports the existing host and port without rotating the token.
- `POST /shutdown` is authenticated, accepts no request body, sends its success response completely, then begins the same stop path used by the VS Code stop command.
- `POST /shutdown` while already stopping should return a sanitized success or gateway-not-ready response; it must not hang the socket.

## Health Response

```json
{
  "status": "ok",
  "version": "0.0.1",
  "host": "127.0.0.1",
  "port": 49152,
  "startedAt": "2026-05-01T00:00:00.000Z",
  "auth": "bearer"
}
```

`/health` must not include the gateway token, prompt text, response text, model request contents, or local environment values.

## Model Listing Response

```json
{
  "models": [
    {
      "id": "vscode-model-id",
      "name": "Display Name",
      "vendor": "provider-or-family",
      "family": "optional-family",
      "version": null,
      "capabilities": {
        "streaming": true,
        "toolCalling": false,
        "structuredOutput": false
      }
    }
  ]
}
```

Model object rules:

- `id` is the opaque VS Code model identifier used by chat requests.
- `name` falls back to `id` when no display name is available.
- `vendor`, `family`, `version`, and token-limit fields are optional or nullable when VS Code does not expose them through the stable API.
- The gateway accepts chat requests only for model IDs returned by the current `/v1/models` result.
- Capability flags default conservatively. `structuredOutput` remains `false`. `/v1/models` may continue reporting `toolCalling: false` until reliable VS Code model capability detection exists, even though the native non-streaming transport can carry tool calls. `streaming` is `true` for models that can use the gateway stream path.

## Native Chat Request

```json
{
  "model": "opaque-vscode-model-id",
  "messages": [
    { "role": "system", "content": "Optional system instruction" },
    { "role": "user", "content": "Hello" },
    {
      "role": "assistant",
      "content": "",
      "toolCalls": [
        { "id": "call_1", "name": "get_stock_data", "input": { "ticker": "MSFT" } }
      ]
    },
    { "role": "tool", "toolCallId": "call_1", "content": "tool output text" }
  ],
  "tools": [
    {
      "name": "get_stock_data",
      "description": "Fetch stock data.",
      "inputSchema": { "type": "object", "properties": { "ticker": { "type": "string" } } }
    }
  ],
  "requestId": "optional-client-request-id",
  "metadata": {}
}
```

Validation rules:

- `Content-Type` for chat POST endpoints must be `application/json` or an `application/json` variant.
- Request bodies larger than 1 MiB are rejected.
- Top-level keys are exactly `model`, `messages`, optional `requestId`, optional `metadata`, and optional `tools`.
- `model` is required and must be a non-empty string.
- `messages` is required and must contain at least one item.
- Text message `role` must be `system`, `user`, or `assistant`, and `content` must be a non-empty string.
- Assistant messages may include native `toolCalls`; when present, `toolCalls` must be a non-empty array and assistant `content` may be an empty string.
- Each native tool call is `{ "id": "call_1", "name": "get_stock_data", "input": { ... } }`; `id` and `name` must be nonblank strings, and `input` must be an object.
- Tool result messages are `{ "role": "tool", "toolCallId": "call_1", "content": "tool output text" }`; `toolCallId` must be nonblank and `content` must be a string.
- `tools`, when present, must be a non-empty array of native tool objects. Each tool must have nonblank string `name`, string `description`, and optional object `inputSchema`.
- Native tool objects reject sibling `type`, `function`, and `parameters` keys. JSON Schema keywords such as `inputSchema.type` are valid inside `inputSchema`.
- OpenAI-style message fields `tool_calls`, `tool_call_id`, `function`, and `arguments` are invalid.
- `metadata`, when present, must be a JSON object.
- `requestId`, when present, must be a non-empty string.
- Empty POST bodies are invalid for chat endpoints. Malformed JSON returns `invalid_json`. Oversized bodies return `validation_error` unless the implementation adds a more specific sanitized error code later.

## Native Chat Response

```json
{
  "id": "gwchat_opaque-id",
  "model": "opaque-vscode-model-id",
  "created": "2026-05-01T00:00:00.000Z",
  "message": {
    "role": "assistant",
    "content": "Model response text"
  },
  "finishReason": "stop",
  "usage": null,
  "metadata": {}
}
```

Native non-streaming tool-call response:

```json
{
  "id": "gwchat_opaque-id",
  "model": "opaque-vscode-model-id",
  "created": "2026-05-01T00:00:00.000Z",
  "message": {
    "role": "assistant",
    "content": "",
    "toolCalls": [
      { "id": "call_1", "name": "get_stock_data", "input": { "ticker": "MSFT" } }
    ]
  },
  "finishReason": "toolCalls",
  "usage": null,
  "metadata": {}
}
```

`finishReason` is exactly `"toolCalls"` when `message.toolCalls` is non-empty; otherwise it is exactly `"stop"`. The gateway does not execute returned tool calls. Local clients execute tools and include prior assistant `toolCalls` plus `role: "tool"` results on the next model turn. Structured output normalization belongs in a later adapter or contract packet.

## Streaming Response

P3.3b streaming uses text-only Server-Sent Events from `POST /v1/chat/completions/stream`. Tool-enabled streaming is not supported yet; the endpoint rejects top-level `tools`, assistant `toolCalls`, and `role: "tool"` messages with `validation_error` before model invocation.

Required response headers:

```text
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

Chunk event:

```text
event: chunk
data: {"text":"partial text"}

```

Done event:

```text
event: done
data: {"id":"gwchat_opaque-id","model":"opaque-vscode-model-id","finishReason":"stop","metadata":{}}

```

Error event:

```text
event: error
data: {"error":{"code":"unknown_model_error","message":"The model request failed.","requestId":"gwreq_opaque-id","metadata":{}}}

```

Do not emit an OpenAI-style `[DONE]` sentinel in Phase 1. Close the response after `done` or `error`. Client disconnect must cancel the VS Code request with a cancellation token on a best-effort basis.

SSE error rules:

- Failures before SSE headers are sent use the normal JSON native error envelope and HTTP status code.
- Failures after the first SSE byte is sent use exactly one `event: error` with the native error payload, then close the response.
- Successful streams emit zero or more `chunk` events and exactly one `done` event, then close the response.
- Cancellation after headers are sent emits `event: error` with `cancelled` when the server can still write; otherwise cancellation just closes the response.

## Error Envelope

All JSON error responses use this native envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "requestId": "gwreq_opaque-id",
    "metadata": {}
  }
}
```

Messages must be sanitized. Do not return raw prompt text, response text, tokens, stack traces, environment values, or unreviewed provider payloads.

Status-code mapping:

| HTTP Status | Error Code | Use When |
| --- | --- | --- |
| 400 | `invalid_json` | JSON parsing fails. |
| 400 | `validation_error` | Request shape is invalid. |
| 401 | `unauthorized` | Bearer token is missing or invalid. |
| 403 | `model_access_denied` | VS Code reports missing user consent or entitlement. |
| 404 | `not_found` | Endpoint path is unknown. |
| 404 | `model_not_found` | Requested model ID is not currently available. |
| 405 | `method_not_allowed` | Endpoint path exists but method is wrong. |
| 415 | `unsupported_media_type` | POST content type is not JSON. |
| 429 | `quota_or_rate_limited` | VS Code reports blocked, quota, or rate-limit state. |
| 499 | `cancelled` | Caller cancellation is detected before a normal response is produced. |
| 500 | `internal_error` | Gateway code fails unexpectedly. |
| 501 | `not_implemented` | Protected endpoint is reserved but not implemented in the current phase. |
| 502 | `unknown_model_error` | Model call fails without a known category. |
| 503 | `gateway_not_ready` | Gateway is not ready to handle the request. |

## Error Categories

- `unauthorized`: missing or invalid gateway token.
- `model_not_found`: requested VS Code model is unavailable.
- `model_access_denied`: user consent or entitlement is missing.
- `quota_or_rate_limited`: model provider rejected due to quota or rate limits.
- `cancelled`: caller cancelled the request.
- `gateway_not_ready`: extension or gateway is not fully initialized.
- `unknown_model_error`: raw model call failed in an unexpected way.

## Open Decisions

- Whether to add an OpenAI-compatible facade after the native Phase 1 path works.
- Whether structured output should become gateway-native or remain adapter-level after Phase 1.
- How to detect and advertise reliable per-model tool-calling capability through `/v1/models`.
- How to support tool-enabled streaming without weakening the native non-streaming contract.
