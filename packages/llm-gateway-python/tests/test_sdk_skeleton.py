from __future__ import annotations

import ast
import json
from importlib import metadata
from io import BytesIO
from pathlib import Path
import urllib.error as urllib_error

import pytest

import llm_gateway
from llm_gateway import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    GatewayClient,
    GatewayClientConfig,
    GatewayConfigurationError,
    GatewayErrorPayload,
    GatewayHealth,
    GatewayModel,
    GatewayModelCapabilities,
    GatewayRequestError,
    GatewayResponseError,
    GatewayTransportError,
    StreamChunkEvent,
    StreamDoneEvent,
    StreamErrorEvent,
)

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PACKAGE_ROOT / "src" / "llm_gateway"
README = PACKAGE_ROOT / "README.md"


class StubResponse:
    def __init__(self, payload: object, status_code: int = 200) -> None:
        self._body = json.dumps(payload).encode("utf-8")
        self._status_code = status_code

    def __enter__(self) -> "StubResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def getcode(self) -> int:
        return self._status_code

    def read(self) -> bytes:
        return self._body


class StubStreamResponse:
    def __init__(
        self,
        body: bytes | str,
        status_code: int = 200,
        readline_error: BaseException | None = None,
    ) -> None:
        if isinstance(body, str):
            body = body.encode("utf-8")
        self._body = BytesIO(body)
        self._status_code = status_code
        self._readline_error = readline_error
        self.closed = False

    def getcode(self) -> int:
        return self._status_code

    def read(self) -> bytes:
        return self._body.read()

    def readline(self) -> bytes:
        if self._readline_error is not None:
            raise self._readline_error
        return self._body.readline()

    def close(self) -> None:
        self.closed = True


def request_headers(request: object) -> dict[str, str]:
    return {name.lower(): value for name, value in request.header_items()}


def http_error(url: str, status_code: int, payload: object) -> urllib_error.HTTPError:
    return urllib_error.HTTPError(
        url,
        status_code,
        "native gateway error",
        hdrs={},
        fp=BytesIO(json.dumps(payload).encode("utf-8")),
    )


def sse_event(name: str, payload: object) -> bytes:
    data = json.dumps(payload, separators=(",", ":"))
    return f"event: {name}\ndata: {data}\n\n".encode("utf-8")


def test_package_imports_and_metadata() -> None:
    assert llm_gateway.__version__ == "0.0.1"
    assert metadata.version("llm-gateway") == "0.0.1"
    assert GatewayClient.__name__ == "GatewayClient"


def test_source_does_not_import_forbidden_repo_roots() -> None:
    forbidden_roots = {"trading" + "agents", "c" + "li"}

    for source_file in SOURCE_ROOT.glob("*.py"):
        tree = ast.parse(source_file.read_text(encoding="utf-8"), filename=str(source_file))
        for node in ast.walk(tree):
            imported_root: str | None = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_root = alias.name.split(".", 1)[0]
                    assert imported_root not in forbidden_roots
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imported_root = node.module.split(".", 1)[0]
                assert imported_root not in forbidden_roots


def test_config_and_client_repr_redact_token() -> None:
    token = "test-token-value"
    config = GatewayClientConfig(base_url="http://127.0.0.1:49152", token=token, timeout=3.0)
    client = GatewayClient(config)

    assert token not in repr(config)
    assert token not in str(config)
    assert token not in repr(client)
    assert "<redacted>" in repr(config)
    assert "<redacted>" in repr(client)


def test_config_repr_handles_missing_and_empty_tokens() -> None:
    missing = GatewayClientConfig(base_url="http://127.0.0.1:49152")
    empty = GatewayClientConfig(base_url="http://127.0.0.1:49152", token="")

    assert "token=None" in repr(missing)
    assert "token=''" in repr(empty)


def test_stream_chat_posts_authenticated_native_json_and_yields_events(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token = "synthetic-stream-token"
    seen: dict[str, object] = {"calls": 0}
    response = StubStreamResponse(
        b": ignored comment\r\n"
        b"event: chunk\r\n"
        b"data: {\"text\":\r\n"
        b"data: \"Hel\"}\r\n"
        b"\r\n"
        + sse_event("chunk", {"text": "lo"})
        + sse_event(
            "done",
            {
                "id": "gwchat_opaque-id",
                "model": "vscode-model-id",
                "finishReason": "stop",
                "metadata": {"trace": "ok"},
            },
        )
        + sse_event("chunk", {"text": "ignored"})
    )

    def stub_urlopen(request: object, timeout: float | None = None) -> StubStreamResponse:
        seen["calls"] = seen["calls"] + 1
        seen["url"] = request.full_url
        seen["method"] = request.get_method()
        seen["headers"] = request_headers(request)
        seen["body"] = json.loads(request.data.decode("utf-8"))
        seen["timeout"] = timeout
        return response

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152/prefix/", token=token, timeout=5.0)
    )
    request = ChatRequest(
        model="vscode-model-id",
        messages=[ChatMessage(role="user", content="Hello")],
        request_id="client-request-id",
        metadata={"source": "test"},
    )

    stream = client.stream_chat(request)

    assert seen["calls"] == 0
    assert list(stream) == [
        StreamChunkEvent(text="Hel"),
        StreamChunkEvent(text="lo"),
        StreamDoneEvent(
            id="gwchat_opaque-id",
            model="vscode-model-id",
            finish_reason="stop",
            metadata={"trace": "ok"},
        ),
    ]
    assert response.closed is True
    assert seen["url"] == "http://127.0.0.1:49152/prefix/v1/chat/completions/stream"
    assert seen["method"] == "POST"
    assert seen["headers"] == {
        "accept": "text/event-stream",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    assert seen["body"] == {
        "model": "vscode-model-id",
        "messages": [{"role": "user", "content": "Hello"}],
        "requestId": "client-request-id",
        "metadata": {"source": "test"},
    }
    assert seen["timeout"] == 5.0


def test_stream_chat_yields_zero_chunk_done_stream_and_closes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = StubStreamResponse(
        sse_event(
            "done",
            {
                "id": "gwchat_empty",
                "model": "model-id",
                "finishReason": "stop",
                "metadata": {},
            },
        )
    )

    def stub_urlopen(request: object, timeout: float | None = None) -> StubStreamResponse:
        return response

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152", token="synthetic-token")
    )

    events = list(
        client.stream_chat(
            ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hello")])
        )
    )

    assert events == [
        StreamDoneEvent(id="gwchat_empty", model="model-id", finish_reason="stop", metadata={})
    ]
    assert response.closed is True


def test_stream_chat_yields_error_event_and_closes(monkeypatch: pytest.MonkeyPatch) -> None:
    token = "synthetic-stream-error-token"
    response = StubStreamResponse(
        sse_event("chunk", {"text": "partial"})
        + sse_event(
            "error",
            {
                "error": {
                    "code": "unknown_model_error",
                    "message": f"Rejected bearer value {token}.",
                    "requestId": "gwreq_stream",
                    "metadata": {"category": "model"},
                }
            },
        )
    )

    def stub_urlopen(request: object, timeout: float | None = None) -> StubStreamResponse:
        return response

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(GatewayClientConfig(base_url="http://127.0.0.1:49152", token=token))

    events = list(
        client.stream_chat(
            ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hello")])
        )
    )

    assert events == [
        StreamChunkEvent(text="partial"),
        StreamErrorEvent(
            error=GatewayErrorPayload(
                code="unknown_model_error",
                message="Rejected bearer value <redacted>.",
                request_id="gwreq_stream",
                metadata={"category": "model"},
            )
        ),
    ]
    assert token not in events[-1].error.message
    assert response.closed is True


def test_stream_chat_pre_stream_native_http_error_maps_to_request_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def stub_urlopen(request: object, timeout: float | None = None) -> StubStreamResponse:
        raise http_error(
            request.full_url,
            401,
            {
                "error": {
                    "code": "unauthorized",
                    "message": "Missing bearer token.",
                    "requestId": "gwreq_auth",
                    "metadata": {},
                }
            },
        )

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152", token="synthetic-token")
    )

    with pytest.raises(GatewayRequestError) as error_info:
        list(
            client.stream_chat(
                ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hello")])
            )
        )

    assert error_info.value.status_code == 401
    assert error_info.value.code == "unauthorized"


@pytest.mark.parametrize("token", [None, "", "   "])
def test_stream_chat_requires_non_empty_token_at_method_call(
    monkeypatch: pytest.MonkeyPatch, token: str | None
) -> None:
    def stub_urlopen(request: object, timeout: float | None = None) -> StubStreamResponse:
        raise AssertionError("HTTP should not be attempted without a token")

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(GatewayClientConfig(base_url="http://127.0.0.1:49152", token=token))

    with pytest.raises(GatewayConfigurationError):
        client.stream_chat(
            ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hello")])
        )


@pytest.mark.parametrize(
    "body",
    [
        b"event: chunk\ndata: not-json\n\n",
        sse_event("chunk", {"text": 42}),
        sse_event(
            "done",
            {
                "id": "gwchat_bad",
                "model": "model-id",
                "finishReason": "length",
                "metadata": {},
            },
        ),
    ],
)
def test_malformed_success_stream_payloads_raise_response_error_and_close(
    monkeypatch: pytest.MonkeyPatch, body: bytes
) -> None:
    response = StubStreamResponse(body)

    def stub_urlopen(request: object, timeout: float | None = None) -> StubStreamResponse:
        return response

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152", token="synthetic-token")
    )

    with pytest.raises(GatewayResponseError):
        list(
            client.stream_chat(
                ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hello")])
            )
        )

    assert response.closed is True


def test_stream_chat_unknown_event_raises_response_error_and_closes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = StubStreamResponse(sse_event("future", {"text": "Hello"}))

    def stub_urlopen(request: object, timeout: float | None = None) -> StubStreamResponse:
        return response

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152", token="synthetic-token")
    )

    with pytest.raises(GatewayResponseError):
        list(
            client.stream_chat(
                ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hello")])
            )
        )

    assert response.closed is True


def test_stream_chat_missing_terminal_event_raises_response_error_and_closes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = StubStreamResponse(sse_event("chunk", {"text": "partial"}))

    def stub_urlopen(request: object, timeout: float | None = None) -> StubStreamResponse:
        return response

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152", token="synthetic-token")
    )

    with pytest.raises(GatewayResponseError):
        list(
            client.stream_chat(
                ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hello")])
            )
        )

    assert response.closed is True


def test_stream_chat_rejects_forbidden_sentinel_shaped_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sentinel = "[" + "DONE" + "]"
    response = StubStreamResponse(f"event: chunk\ndata: {sentinel}\n\n")

    def stub_urlopen(request: object, timeout: float | None = None) -> StubStreamResponse:
        return response

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152", token="synthetic-token")
    )

    with pytest.raises(GatewayResponseError):
        list(
            client.stream_chat(
                ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hello")])
            )
        )

    assert response.closed is True


def test_stream_chat_explicit_close_after_partial_consumption_closes_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = StubStreamResponse(
        sse_event("chunk", {"text": "partial"})
        + sse_event(
            "done",
            {"id": "gwchat", "model": "model-id", "finishReason": "stop", "metadata": {}},
        )
    )

    def stub_urlopen(request: object, timeout: float | None = None) -> StubStreamResponse:
        return response

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152", token="synthetic-token")
    )

    stream = client.stream_chat(
        ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hello")])
    )

    assert next(stream) == StreamChunkEvent(text="partial")
    assert response.closed is False
    stream.close()
    assert response.closed is True


def test_stream_chat_transport_failure_before_stream_raises_without_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token = "synthetic-stream-transport-token"

    def stub_urlopen(request: object, timeout: float | None = None) -> StubStreamResponse:
        raise urllib_error.URLError(f"connection failed with {token}")

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(GatewayClientConfig(base_url="http://127.0.0.1:49152", token=token))

    with pytest.raises(GatewayTransportError) as error_info:
        list(
            client.stream_chat(
                ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hello")])
            )
        )

    assert token not in str(error_info.value)
    assert token not in repr(error_info.value)
    assert error_info.value.__cause__ is None


def test_stream_chat_transport_failure_during_stream_raises_without_token_and_closes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token = "synthetic-during-stream-token"
    response = StubStreamResponse(b"", readline_error=urllib_error.URLError(f"lost {token}"))

    def stub_urlopen(request: object, timeout: float | None = None) -> StubStreamResponse:
        return response

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(GatewayClientConfig(base_url="http://127.0.0.1:49152", token=token))

    with pytest.raises(GatewayTransportError) as error_info:
        list(
            client.stream_chat(
                ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hello")])
            )
        )

    assert token not in str(error_info.value)
    assert token not in repr(error_info.value)
    assert response.closed is True


def test_native_gateway_type_construction() -> None:
    health = GatewayHealth(
        status="ok",
        version="0.0.1",
        host="127.0.0.1",
        port=49152,
        started_at="2026-05-01T00:00:00.000Z",
    )
    capabilities = GatewayModelCapabilities(streaming=True, tool_calling=False, structured_output=False)
    model = GatewayModel(
        id="vscode-model-id",
        name="Display Name",
        vendor="provider",
        family="family",
        version=None,
        capabilities=capabilities,
    )
    request = ChatRequest(
        model=model.id,
        messages=[
            ChatMessage(role="system", content="Instruction"),
            ChatMessage(role="user", content="Hello"),
        ],
        request_id="client-request-id",
        metadata={"source": "test"},
    )
    response = ChatResponse(
        id="gwchat_opaque-id",
        model=model.id,
        created="2026-05-01T00:00:00.000Z",
        message=ChatMessage(role="assistant", content="Model response text"),
        finish_reason="stop",
    )

    assert health.auth == "bearer"
    assert model.capabilities.streaming is True
    assert request.messages[0].role == "system"
    assert response.usage is None
    assert response.message.role == "assistant"


def test_stream_event_type_construction() -> None:
    error_payload = GatewayErrorPayload(
        code="unknown_model_error",
        message="The model request failed.",
        request_id="gwreq_opaque-id",
    )

    chunk = StreamChunkEvent(text="partial text")
    done = StreamDoneEvent(id="gwchat_opaque-id", model="model-id", finish_reason="stop")
    error = StreamErrorEvent(error=error_payload)

    assert chunk.text == "partial text"
    assert done.metadata == {}
    assert error.error.code == "unknown_model_error"


def test_health_gets_public_endpoint_without_authorization(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    def stub_urlopen(request: object, timeout: float | None = None) -> StubResponse:
        seen["url"] = request.full_url
        seen["method"] = request.get_method()
        seen["headers"] = request_headers(request)
        seen["timeout"] = timeout
        return StubResponse(
            {
                "status": "ok",
                "version": "0.0.1",
                "host": "127.0.0.1",
                "port": 49152,
                "startedAt": "2026-05-01T00:00:00.000Z",
                "auth": "bearer",
            }
        )

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)

    client = GatewayClient(
        GatewayClientConfig(
            base_url="http://127.0.0.1:49152/gateway/", token="synthetic-token", timeout=7.0
        )
    )

    health = client.health()

    assert health == GatewayHealth(
        status="ok",
        version="0.0.1",
        host="127.0.0.1",
        port=49152,
        started_at="2026-05-01T00:00:00.000Z",
        auth="bearer",
    )
    assert seen["url"] == "http://127.0.0.1:49152/gateway/health"
    assert seen["method"] == "GET"
    assert seen["headers"] == {"accept": "application/json"}
    assert seen["timeout"] == 7.0


def test_list_models_gets_authenticated_endpoint_and_preserves_base_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token = "synthetic-model-token"
    seen: dict[str, object] = {}

    def stub_urlopen(request: object, timeout: float | None = None) -> StubResponse:
        seen["url"] = request.full_url
        seen["method"] = request.get_method()
        seen["headers"] = request_headers(request)
        seen["timeout"] = timeout
        return StubResponse(
            {
                "models": [
                    {
                        "id": "vscode-model-id",
                        "name": "Display Name",
                        "vendor": "provider",
                        "family": "family",
                        "version": None,
                        "capabilities": {
                            "streaming": True,
                            "toolCalling": False,
                            "structuredOutput": False,
                        },
                    }
                ]
            }
        )

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)

    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152/prefix/", token=token, timeout=2.5)
    )

    models = client.list_models()

    assert seen["url"] == "http://127.0.0.1:49152/prefix/v1/models"
    assert seen["method"] == "GET"
    assert seen["headers"] == {
        "accept": "application/json",
        "authorization": f"Bearer {token}",
    }
    assert seen["timeout"] == 2.5
    assert models == [
        GatewayModel(
            id="vscode-model-id",
            name="Display Name",
            vendor="provider",
            family="family",
            version=None,
            capabilities=GatewayModelCapabilities(
                streaming=True, tool_calling=False, structured_output=False
            ),
        )
    ]


def test_chat_posts_authenticated_native_json(monkeypatch: pytest.MonkeyPatch) -> None:
    token = "synthetic-chat-token"
    seen: dict[str, object] = {}

    def stub_urlopen(request: object, timeout: float | None = None) -> StubResponse:
        seen["url"] = request.full_url
        seen["method"] = request.get_method()
        seen["headers"] = request_headers(request)
        seen["body"] = json.loads(request.data.decode("utf-8"))
        seen["timeout"] = timeout
        return StubResponse(
            {
                "id": "gwchat_opaque-id",
                "model": "vscode-model-id",
                "created": "2026-05-01T00:00:00.000Z",
                "message": {"role": "assistant", "content": "Hello"},
                "finishReason": "stop",
                "usage": None,
                "metadata": {"trace": "ok"},
            }
        )

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)

    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152", token=token, timeout=3.0)
    )
    request = ChatRequest(
        model="vscode-model-id",
        messages=[ChatMessage(role="user", content="Hello")],
        request_id="client-request-id",
        metadata={"source": "test"},
    )

    response = client.chat(request)

    assert seen["url"] == "http://127.0.0.1:49152/v1/chat/completions"
    assert seen["method"] == "POST"
    assert seen["headers"] == {
        "accept": "application/json",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    assert seen["body"] == {
        "model": "vscode-model-id",
        "messages": [{"role": "user", "content": "Hello"}],
        "requestId": "client-request-id",
        "metadata": {"source": "test"},
    }
    assert seen["timeout"] == 3.0
    assert response == ChatResponse(
        id="gwchat_opaque-id",
        model="vscode-model-id",
        created="2026-05-01T00:00:00.000Z",
        message=ChatMessage(role="assistant", content="Hello"),
        finish_reason="stop",
        usage=None,
        metadata={"trace": "ok"},
    )


def test_chat_omits_unset_optional_request_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    def stub_urlopen(request: object, timeout: float | None = None) -> StubResponse:
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return StubResponse(
            {
                "id": "gwchat_opaque-id",
                "model": "vscode-model-id",
                "created": "2026-05-01T00:00:00.000Z",
                "message": {"role": "assistant", "content": "done"},
                "finishReason": "stop",
                "usage": None,
                "metadata": {},
            }
        )

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152/", token="synthetic-token")
    )

    client.chat(ChatRequest(model="vscode-model-id", messages=[ChatMessage(role="user", content="Hi")]))

    assert seen["body"] == {
        "model": "vscode-model-id",
        "messages": [{"role": "user", "content": "Hi"}],
    }


@pytest.mark.parametrize(
    ("method_name", "chat_request"),
    [
        ("list_models", None),
        ("chat", ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hi")])),
    ],
)
@pytest.mark.parametrize("token", [None, "", "   "])
def test_protected_methods_require_non_empty_token_before_http(
    monkeypatch: pytest.MonkeyPatch,
    method_name: str,
    chat_request: ChatRequest | None,
    token: str | None,
) -> None:
    def stub_urlopen(request_object: object, timeout: float | None = None) -> StubResponse:
        raise AssertionError("HTTP should not be attempted without a token")

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(GatewayClientConfig(base_url="http://127.0.0.1:49152", token=token))

    with pytest.raises(GatewayConfigurationError):
        if chat_request is None:
            getattr(client, method_name)()
        else:
            getattr(client, method_name)(chat_request)


@pytest.mark.parametrize(
    ("status_code", "code"),
    [
        (400, "invalid_json"),
        (400, "validation_error"),
        (401, "unauthorized"),
        (403, "model_access_denied"),
        (404, "not_found"),
        (404, "model_not_found"),
        (405, "method_not_allowed"),
        (415, "unsupported_media_type"),
        (429, "quota_or_rate_limited"),
        (499, "cancelled"),
        (500, "internal_error"),
        (501, "not_implemented"),
        (502, "unknown_model_error"),
        (503, "gateway_not_ready"),
    ],
)
def test_native_error_envelopes_map_to_request_error(
    monkeypatch: pytest.MonkeyPatch, status_code: int, code: str
) -> None:
    def stub_urlopen(request: object, timeout: float | None = None) -> StubResponse:
        raise http_error(
            request.full_url,
            status_code,
            {
                "error": {
                    "code": code,
                    "message": "Sanitized gateway failure.",
                    "requestId": "gwreq_opaque-id",
                    "metadata": {"category": code},
                }
            },
        )

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152", token="synthetic-token")
    )

    with pytest.raises(GatewayRequestError) as error_info:
        client.list_models()

    error = error_info.value
    assert error.status_code == status_code
    assert error.code == code
    assert error.request_id == "gwreq_opaque-id"
    assert error.payload.metadata == {"category": code}


def test_unknown_future_error_code_is_preserved(monkeypatch: pytest.MonkeyPatch) -> None:
    def stub_urlopen(request: object, timeout: float | None = None) -> StubResponse:
        raise http_error(
            request.full_url,
            418,
            {
                "error": {
                    "code": "future_native_error",
                    "message": "A future gateway failed.",
                    "requestId": "gwreq_future",
                    "metadata": {"future": True},
                }
            },
        )

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152", token="synthetic-token")
    )

    with pytest.raises(GatewayRequestError) as error_info:
        client.list_models()

    assert error_info.value.status_code == 418
    assert error_info.value.code == "future_native_error"
    assert error_info.value.request_id == "gwreq_future"
    assert error_info.value.payload.metadata == {"future": True}


def test_request_error_message_redacts_config_token(monkeypatch: pytest.MonkeyPatch) -> None:
    token = "synthetic-secret-token"

    def stub_urlopen(request: object, timeout: float | None = None) -> StubResponse:
        raise http_error(
            request.full_url,
            401,
            {
                "error": {
                    "code": "unauthorized",
                    "message": f"Rejected bearer value {token}.",
                    "requestId": "gwreq_auth",
                    "metadata": {},
                }
            },
        )

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(GatewayClientConfig(base_url="http://127.0.0.1:49152", token=token))

    with pytest.raises(GatewayRequestError) as error_info:
        client.list_models()

    assert token not in str(error_info.value)
    assert token not in repr(error_info.value)
    assert "<redacted>" in str(error_info.value)


@pytest.mark.parametrize(
    "payload",
    [
        {"status": "ok"},
        {"models": [{"id": "model-id", "name": "Model"}]},
        {
            "id": "gwchat_opaque-id",
            "model": "model-id",
            "created": "2026-05-01T00:00:00.000Z",
            "message": {"role": "user", "content": "not assistant"},
            "finishReason": "stop",
            "usage": None,
            "metadata": {},
        },
    ],
)
def test_malformed_success_payloads_raise_response_error(
    monkeypatch: pytest.MonkeyPatch, payload: object
) -> None:
    calls = iter([payload])

    def stub_urlopen(request: object, timeout: float | None = None) -> StubResponse:
        return StubResponse(next(calls))

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152", token="synthetic-token")
    )

    with pytest.raises(GatewayResponseError):
        if isinstance(payload, dict) and "status" in payload:
            client.health()
        elif isinstance(payload, dict) and "models" in payload:
            client.list_models()
        else:
            client.chat(ChatRequest(model="model-id", messages=[ChatMessage(role="user", content="Hi")]))


@pytest.mark.parametrize(
    "payload",
    [
        {"message": "plain failure"},
        {"error": {"code": "internal_error"}},
    ],
)
def test_malformed_error_envelopes_raise_response_error(
    monkeypatch: pytest.MonkeyPatch, payload: object
) -> None:
    def stub_urlopen(request: object, timeout: float | None = None) -> StubResponse:
        raise http_error(request.full_url, 500, payload)

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152", token="synthetic-token")
    )

    with pytest.raises(GatewayResponseError):
        client.list_models()


def test_malformed_json_error_response_raises_response_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def stub_urlopen(request: object, timeout: float | None = None) -> StubResponse:
        raise urllib_error.HTTPError(
            request.full_url,
            500,
            "native gateway error",
            hdrs={},
            fp=BytesIO(b"not-json"),
        )

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(
        GatewayClientConfig(base_url="http://127.0.0.1:49152", token="synthetic-token")
    )

    with pytest.raises(GatewayResponseError):
        client.list_models()


def test_transport_failure_raises_transport_error_without_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token = "synthetic-transport-token"

    def stub_urlopen(request: object, timeout: float | None = None) -> StubResponse:
        raise urllib_error.URLError(f"connection failed with {token}")

    monkeypatch.setattr("llm_gateway.client.urllib_request.urlopen", stub_urlopen)
    client = GatewayClient(GatewayClientConfig(base_url="http://127.0.0.1:49152", token=token))

    with pytest.raises(GatewayTransportError) as error_info:
        client.list_models()

    assert token not in str(error_info.value)
    assert token not in repr(error_info.value)
    assert error_info.value.__cause__ is None


def test_readme_reflects_p2_3_client_scope() -> None:
    readme = README.read_text(encoding="utf-8")

    stale_phrase = "health`, `list_models`, and `chat` methods intentionally raise"
    assert stale_phrase not in readme
    assert "Current P2.4 scope" in readme
    assert "synchronous native SSE streaming" in readme
    assert "llm_gateway.langchain_adapter.GatewayChatModel" in readme
    assert "with_structured_output(...)` raises `NotImplementedError`" in readme
    assert "bind_tools(...)` raises `NotImplementedError`" in readme


def test_source_and_tests_avoid_forbidden_boundaries_and_facade_terms() -> None:
    forbidden_terms = (
        "trading" + "agents",
        "from " + "c" + "li",
        "import " + "c" + "li",
        "cho" + "ices",
        "del" + "ta",
        "[" + "DONE" + "]",
    )
    checked_files = list(SOURCE_ROOT.glob("*.py")) + list((PACKAGE_ROOT / "tests").glob("*.py"))

    for checked_file in checked_files:
        content = checked_file.read_text(encoding="utf-8").lower()
        for forbidden_term in forbidden_terms:
            assert forbidden_term.lower() not in content