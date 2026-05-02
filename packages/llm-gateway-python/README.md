# LLM Gateway Python SDK

Generic Python SDK for the native VS Code LLM gateway.

Current P2.4 scope:

- package-local `pyproject.toml` for the `llm-gateway` distribution
- importable `llm_gateway` source package
- shallow native gateway data types for health, models, chat, and stream events
- redacting client configuration
- blocking standard-library HTTP calls for `/health`, `/v1/models`, `/v1/chat/completions`, and `/v1/chat/completions/stream`
- synchronous native SSE streaming through `GatewayClient.stream_chat()`
- typed native gateway errors, malformed-response errors, and transport errors
- optional LangChain Core adapter through `llm_gateway.langchain_adapter.GatewayChatModel`
- package-local tests for metadata, imports, boundaries, redaction, HTTP behavior, native error mapping, SSE parsing, stream cleanup, and LangChain adapter behavior

This package should remain generic and avoid finance assumptions.

It must not import from TradingAgents or the repo CLI. The base `llm_gateway` import remains lightweight and does not import LangChain Core.

## Install From Repository Root

```powershell
& "c:/VSCode/Tauric/TradingAgents/.venv/Scripts/python.exe" -m pip install -e packages/llm-gateway-python
```

Install the optional LangChain adapter extra when using `GatewayChatModel`:

```powershell
& "c:/VSCode/Tauric/TradingAgents/.venv/Scripts/python.exe" -m pip install -e "packages/llm-gateway-python[langchain]"
```

## Test From Repository Root

```powershell
& "c:/VSCode/Tauric/TradingAgents/.venv/Scripts/python.exe" -m pytest packages/llm-gateway-python/tests -q
& "c:/VSCode/Tauric/TradingAgents/.venv/Scripts/python.exe" -c "import llm_gateway; print(llm_gateway.__version__)"
& "c:/VSCode/Tauric/TradingAgents/.venv/Scripts/python.exe" -c "from llm_gateway.langchain_adapter import GatewayChatModel; print(GatewayChatModel.__name__)"
```

## Package-Local Commands

From `packages/llm-gateway-python/`:

```powershell
& "c:/VSCode/Tauric/TradingAgents/.venv/Scripts/python.exe" -m pip install -e .
& "c:/VSCode/Tauric/TradingAgents/.venv/Scripts/python.exe" -m pytest tests -q
```

## Import Smoke

```python
from llm_gateway import ChatMessage, ChatRequest, GatewayClient, GatewayClientConfig, StreamChunkEvent

config = GatewayClientConfig(
    base_url="http://127.0.0.1:<port>",
    token="<gateway-token>",
)
client = GatewayClient(config)

repr(config)  # token value is redacted

health = client.health()
models = client.list_models()
response = client.chat(
    ChatRequest(
        model=models[0].id,
        messages=[ChatMessage(role="user", content="Hello")],
    )
)

for event in client.stream_chat(
    ChatRequest(
        model=models[0].id,
        messages=[ChatMessage(role="user", content="Stream hello")],
    )
):
    if isinstance(event, StreamChunkEvent):
        print(event.text)
```

## LangChain Core Adapter

The adapter is optional and package-local:

```python
from llm_gateway import GatewayClient, GatewayClientConfig
from llm_gateway.langchain_adapter import GatewayChatModel

client = GatewayClient(
    GatewayClientConfig(
        base_url="http://127.0.0.1:<port>",
        token="<gateway-token>",
    )
)

chat_model = GatewayChatModel(client=client, model="<model-id>")
message = chat_model.invoke("Hello")
print(message.content)

for chunk in chat_model.stream("Stream hello"):
    if chunk.content:
        print(chunk.content, end="")
```

`GatewayChatModel` converts LangChain system, human/user, and assistant messages to native gateway `ChatMessage` values, then calls `GatewayClient.chat()` or `GatewayClient.stream_chat()` with a native `ChatRequest`. String content is passed through unchanged. LangChain text blocks are normalized into plain text, and unsupported roles or content shapes fail before sending a request.

Non-empty stop sequences and unsupported generation options fail explicitly because the native gateway contract does not expose those request fields. Adapter string representations and identifying parameters do not expose bearer tokens.

Structured output is not supported by the native gateway contract yet. `with_structured_output(...)` raises `NotImplementedError`; callers should catch it and fall back to free-text `invoke()` until a native structured-output contract exists.

Native gateway tool calling is deferred. `bind_tools(...)` raises `NotImplementedError` so callers do not receive misleading empty tool results.

## Client Behavior

- `health()` performs public `GET /health` and does not send an authorization header.
- `list_models()` performs protected `GET /v1/models` with `Authorization: Bearer <gateway-token>`.
- `chat()` performs protected `POST /v1/chat/completions` with native UTF-8 JSON.
- `stream_chat()` validates that a non-empty token is configured, then returns a blocking synchronous iterator over native SSE events from protected `POST /v1/chat/completions/stream`.
- Protected methods require a non-empty token before network I/O.
- Native error envelopes are raised as `GatewayRequestError` with status, code, request ID, and metadata preserved.
- Malformed gateway payloads raise `GatewayResponseError`; local HTTP failures raise `GatewayTransportError`.

## Streaming Events

`stream_chat()` yields native stream event dataclasses:

- `StreamChunkEvent(text)` for each `event: chunk` payload.
- `StreamDoneEvent(id, model, finish_reason, metadata)` for the terminal successful `event: done` payload. The native gateway currently accepts only `finishReason: "stop"`.
- `StreamErrorEvent(error)` for a terminal in-stream `event: error` payload. The contained `GatewayErrorPayload` uses the same native error envelope and token redaction as non-streaming errors.

The iterator closes the underlying HTTP response when a stream completes, when an in-stream error event is received, when malformed SSE raises an exception, or when callers explicitly stop early with `iterator.close()`.

Pre-stream non-2xx HTTP responses still raise `GatewayRequestError`. Transport failures raise `GatewayTransportError`. Malformed SSE, unknown event names, missing terminal events, and malformed native event payloads raise `GatewayResponseError`.

Use placeholder tokens in examples and local configuration only:

```python
config = GatewayClientConfig(
    base_url="http://127.0.0.1:<port>",
    token="<gateway-token>",
)
```
