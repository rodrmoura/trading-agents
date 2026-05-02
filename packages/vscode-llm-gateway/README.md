# VS Code LLM Gateway

P1.5 implements local gateway lifecycle, authenticated model listing, authenticated native non-stream chat invocation, and authenticated native SSE chat streaming for Phase 1.

Current behavior in P1.5:

- start/stop/status/copy-token command wiring
- local HTTP server bound to `127.0.0.1` on an ephemeral port
- memory-only bearer token generated after successful server bind
- explicit gateway lifecycle states: `stopped`, `starting`, `running`, `stopping`, `failed`
- public `GET /health` endpoint without token disclosure
- authenticated `POST /shutdown` endpoint that sends a complete success response before stop
- authenticated `GET /v1/models` endpoint returning mapped VS Code model metadata
- authenticated `POST /v1/chat/completions` endpoint with strict native JSON validation and non-stream plain-text responses
- authenticated `POST /v1/chat/completions/stream` endpoint with native Server-Sent Events (`chunk`, `done`, `error`)
- sanitized native JSON errors with no stack or secret disclosure

This package should not import TradingAgents.

## Setup

Run from `packages/vscode-llm-gateway/`:

```powershell
npm install
npm run check
npm run compile
npm test
```

## Command IDs

- `tradingAgentsGateway.start`
- `tradingAgentsGateway.stop`
- `tradingAgentsGateway.status`
- `tradingAgentsGateway.copyToken`

## Placeholder command behavior

- `start`: starts the gateway once and reports host/port. If already running, returns existing status without rotating token.
- `stop`: stops the gateway, closes the HTTP server on best effort, and invalidates the token.
- `status`: shows current state without displaying token.
- `copyToken`: copies token only when running; when stopped it fails gracefully and does not start the gateway.

Start/status notifications include a `Copy Token` action as the explicit user-driven token disclosure path.

## HTTP endpoints

- `GET /health` (public): returns status metadata (`status`, `version`, `host`, `port`, `startedAt`, `auth`) and never includes token.
- `POST /shutdown` (bearer-auth required): accepts no request body, returns JSON success, then triggers shared stop path.
- `GET /v1/models` (bearer-auth required): returns `200` with JSON shape `{ "models": [...] }`.
- `POST /v1/chat/completions` (bearer-auth required): non-stream native chat request/response.
- `POST /v1/chat/completions/stream` (bearer-auth required): native SSE streaming chat request/response.

Native non-stream chat request (strict top-level/message field allowlist):

```json
{
  "model": "opaque-vscode-model-id",
  "messages": [
    { "role": "system", "content": "Optional system instruction" },
    { "role": "user", "content": "Hello" }
  ],
  "requestId": "optional-client-id",
  "metadata": {}
}
```

Native non-stream chat response:

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

Native streaming chat request uses the same strict request shape as non-stream chat.

Native streaming response events (SSE):

```text
event: chunk
data: {"text":"partial text"}

event: done
data: {"id":"gwchat_opaque-id","model":"opaque-vscode-model-id","finishReason":"stop","metadata":{}}

event: error
data: {"error":{"code":"unknown_model_error","message":"The model request failed.","requestId":"gwreq_opaque-id","metadata":{}}}

```

Streaming behavior highlights:

- JSON validation and startup/model errors are returned as normal JSON native errors before SSE headers are committed.
- After SSE headers are committed, failures emit one `event: error` payload and then close.
- Successful streams emit zero or more `chunk` events followed by exactly one `done` event.
- Empty chunks (`""`) are skipped; whitespace chunks are preserved.
- The stream never emits an OpenAI `[DONE]` sentinel.

Validation highlights:

- requires `Content-Type: application/json` (including case/charset variants)
- rejects missing/non-JSON media type with `415 unsupported_media_type`
- rejects malformed or empty JSON with `400 invalid_json`
- rejects request bodies over 1 MiB with `400 validation_error`
- rejects unknown top-level or message fields with `400 validation_error`
- accepts message roles `system`, `user`, `assistant`; system messages are converted to provider user messages with `System instructions:\n` prefix

Model object shape:

```json
{
  "id": "opaque-vscode-model-id",
  "name": "Display Name",
  "vendor": "provider-name",
  "family": "optional-family",
  "version": "optional-version",
  "capabilities": {
    "streaming": true,
    "toolCalling": false,
    "structuredOutput": false
  }
}
```

Mapping behavior:

- `id` is returned exactly as provided by VS Code.
- `name` falls back to `id` when blank.
- `vendor`, `family`, and `version` become `null` when blank.
- capability flags are conservative defaults in P1.3.
- `capabilities.streaming` is `true` for models available via this gateway stream path.

Known endpoint wrong methods return `405 method_not_allowed` after auth checks for protected routes.

## Authentication rules

- Accepts tokens only from `Authorization: Bearer <gateway-token>`.
- Rejects token transport through query string, cookies, request body, and alternate headers (including `x-gateway-token` and `x-api-key`).
- Missing, malformed, or wrong token returns `401 unauthorized`.

## Manual smoke command

After starting the gateway and copying the token:

```powershell
$body = @{
  model = "<model-id-from-models>"
  messages = @(@{ role = "user"; content = "Reply with one short sentence." })
} | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:<port>/v1/chat/completions -Headers @{ Authorization = "Bearer <copied-token>" } -ContentType "application/json" -Body $body
```

Streaming smoke (SSE response body):

```powershell
$body = @{
  model = "<model-id-from-models>"
  messages = @(@{ role = "user"; content = "Count from one to five slowly." })
} | ConvertTo-Json -Depth 5
Invoke-WebRequest -Method Post -Uri http://127.0.0.1:<port>/v1/chat/completions/stream -Headers @{ Authorization = "Bearer <copied-token>" } -ContentType "application/json" -Body $body
```

Manual cancellation check:

- Start a streaming request and interrupt/close the client request before completion.
- Confirm the gateway remains responsive and subsequent authenticated requests still succeed.

## Tests

Tests use Node built-in `node:test` + `assert` and import compiled `dist` modules.

Coverage includes:

- start/stop idempotency and lifecycle state behavior
- token generation and token clearing on stop/shutdown/deactivate path
- local bind host and health payload shape
- protected endpoint auth gating and method handling
- strict bearer token transport enforcement
- shutdown auth/body validation and response-before-close behavior
- copy-token before start helper behavior
- command message token non-disclosure
- strict native chat request/content-type/body-size/schema validation
- non-stream native chat model invocation and response assembly
- native SSE stream framing (`chunk`, `done`, `error`) and sanitized post-header error handling
- stream best-effort cancellation on client disconnect and gateway stop/shutdown/deactivate paths
- chat model error mapping and cancellation best-effort behavior

Activation is command-scoped only and does not start a gateway.
