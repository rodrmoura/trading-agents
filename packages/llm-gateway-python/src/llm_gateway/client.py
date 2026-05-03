"""Synchronous client for the native LLM gateway."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
import json
import urllib.error as urllib_error
import urllib.parse as urllib_parse
import urllib.request as urllib_request

from .errors import (
    GatewayConfigurationError,
    GatewayErrorPayload,
    GatewayRequestError,
    GatewayResponseError,
    GatewayTransportError,
)
from .types import ChatRequest, ChatResponse, ChatStreamEvent, GatewayHealth, GatewayModel
from .types import ChatMessage, GatewayModelCapabilities
from .types import GatewayTool, GatewayToolCall
from .types import StreamChunkEvent, StreamDoneEvent, StreamErrorEvent


_MISSING = object()


def _redacted_token(token: str | None) -> str:
    if token is None:
        return "None"
    if token == "":
        return "''"
    return "'<redacted>'"


def _redact_token(value: str, token: str | None) -> str:
    if token:
        return value.replace(token, "<redacted>")
    return value


def _as_mapping(value: object, context: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise GatewayResponseError(f"Gateway returned malformed {context}.")
    return value


def _required_mapping(payload: dict[str, object], field_name: str, context: str) -> dict[str, object]:
    value = payload.get(field_name, _MISSING)
    if not isinstance(value, dict):
        raise GatewayResponseError(f"Gateway returned malformed {context}.")
    return value


def _optional_mapping(payload: dict[str, object], field_name: str, context: str) -> dict[str, object]:
    value = payload.get(field_name, _MISSING)
    if value is _MISSING or value is None:
        return {}
    if not isinstance(value, dict):
        raise GatewayResponseError(f"Gateway returned malformed {context}.")
    return value


def _required_sequence(payload: dict[str, object], field_name: str, context: str) -> list[object]:
    value = payload.get(field_name, _MISSING)
    if not isinstance(value, list):
        raise GatewayResponseError(f"Gateway returned malformed {context}.")
    return value


def _required_str(payload: dict[str, object], field_name: str, context: str) -> str:
    value = payload.get(field_name, _MISSING)
    if not isinstance(value, str):
        raise GatewayResponseError(f"Gateway returned malformed {context}.")
    return value


def _required_nonblank_str(payload: dict[str, object], field_name: str, context: str) -> str:
    value = _required_str(payload, field_name, context)
    if value.strip() == "":
        raise GatewayResponseError(f"Gateway returned malformed {context}.")
    return value


def _optional_str(payload: dict[str, object], field_name: str, context: str) -> str | None:
    value = payload.get(field_name, _MISSING)
    if value is _MISSING or value is None:
        return None
    if not isinstance(value, str):
        raise GatewayResponseError(f"Gateway returned malformed {context}.")
    return value


def _required_int(payload: dict[str, object], field_name: str, context: str) -> int:
    value = payload.get(field_name, _MISSING)
    if isinstance(value, bool) or not isinstance(value, int):
        raise GatewayResponseError(f"Gateway returned malformed {context}.")
    return value


def _required_bool(payload: dict[str, object], field_name: str, context: str) -> bool:
    value = payload.get(field_name, _MISSING)
    if not isinstance(value, bool):
        raise GatewayResponseError(f"Gateway returned malformed {context}.")
    return value


def _optional_bool(
    payload: dict[str, object], field_name: str, context: str, *, default: bool
) -> bool:
    value = payload.get(field_name, _MISSING)
    if value is _MISSING or value is None:
        return default
    if not isinstance(value, bool):
        raise GatewayResponseError(f"Gateway returned malformed {context}.")
    return value


@dataclass(frozen=True, repr=False, slots=True)
class GatewayClientConfig:
    """Configuration for a native gateway client.

    Token values are retained for protected requests, but never included in
    string representations.
    """

    base_url: str
    token: str | None = field(default=None, repr=False)
    timeout: float | None = None

    def __repr__(self) -> str:
        return (
            "GatewayClientConfig("
            f"base_url={self.base_url!r}, "
            f"token={_redacted_token(self.token)}, "
            f"timeout={self.timeout!r}"
            ")"
        )

    __str__ = __repr__


class GatewayClient:
    """Blocking native gateway client."""

    def __init__(self, config: GatewayClientConfig) -> None:
        self._config = config

    @property
    def config(self) -> GatewayClientConfig:
        return self._config

    def __repr__(self) -> str:
        return f"GatewayClient(config={self._config!r})"

    __str__ = __repr__

    def health(self) -> GatewayHealth:
        payload = self._request_json("GET", "/health", protected=False)
        return _parse_health(payload)

    def list_models(self) -> list[GatewayModel]:
        payload = self._request_json("GET", "/v1/models", protected=True)
        return _parse_models(payload)

    def chat(self, request: ChatRequest) -> ChatResponse:
        payload = self._request_json(
            "POST",
            "/v1/chat/completions",
            protected=True,
            body=_serialize_chat_request(request),
        )
        return _parse_chat_response(payload)

    def stream_chat(self, request: ChatRequest) -> Iterator[ChatStreamEvent]:
        token = self._require_token()
        _reject_tool_enabled_stream_request(request)
        body = _serialize_chat_request(request)
        return self._stream_chat_events(body, token)

    def _stream_chat_events(
        self, body: dict[str, object], token: str
    ) -> Iterator[ChatStreamEvent]:
        response: object | None = None
        try:
            response = self._open_stream_response(body, token)
            for event_name, event_data in _iter_sse_events(response):
                event = _parse_stream_event(event_name, event_data, token=token)
                if isinstance(event, (StreamDoneEvent, StreamErrorEvent)):
                    _close_response(response)
                    response = None
                    yield event
                    return
                yield event

            raise GatewayResponseError("Gateway stream ended before a terminal event.")
        except (GatewayRequestError, GatewayResponseError):
            raise
        except (urllib_error.URLError, TimeoutError, OSError, ValueError):
            raise GatewayTransportError("Gateway HTTP stream failed.") from None
        finally:
            _close_response(response)

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        protected: bool,
        body: dict[str, object] | None = None,
    ) -> object:
        headers = {"Accept": "application/json"}
        if protected:
            headers["Authorization"] = f"Bearer {self._require_token()}"

        data: bytes | None = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

        request = urllib_request.Request(
            self._endpoint_url(path), data=data, headers=headers, method=method
        )

        try:
            with urllib_request.urlopen(request, timeout=self._config.timeout) as response:
                status_code = response.getcode()
                response_body = response.read()
        except urllib_error.HTTPError as http_error:
            try:
                response_body = http_error.read()
            finally:
                http_error.close()
            raise self._request_error(http_error.code, response_body) from None
        except (urllib_error.URLError, TimeoutError, OSError, ValueError):
            raise GatewayTransportError("Gateway HTTP request failed.") from None

        if status_code < 200 or status_code >= 300:
            raise self._request_error(status_code, response_body)

        return _decode_json(response_body, "response")

    def _open_stream_response(self, body: dict[str, object], token: str) -> object:
        data = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        request = urllib_request.Request(
            self._endpoint_url("/v1/chat/completions/stream"),
            data=data,
            headers={
                "Accept": "text/event-stream",
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            response = urllib_request.urlopen(request, timeout=self._config.timeout)
        except urllib_error.HTTPError as http_error:
            try:
                response_body = http_error.read()
            finally:
                http_error.close()
            raise self._request_error(http_error.code, response_body) from None
        except (urllib_error.URLError, TimeoutError, OSError, ValueError):
            raise GatewayTransportError("Gateway HTTP stream failed.") from None

        try:
            status_code = response.getcode()
            if status_code < 200 or status_code >= 300:
                response_body = response.read()
                raise self._request_error(status_code, response_body)
        except (GatewayRequestError, GatewayResponseError):
            _close_response(response)
            raise
        except (urllib_error.URLError, TimeoutError, OSError, ValueError):
            _close_response(response)
            raise GatewayTransportError("Gateway HTTP stream failed.") from None

        return response

    def _endpoint_url(self, path: str) -> str:
        parsed = urllib_parse.urlsplit(self._config.base_url)
        base_path = parsed.path.rstrip("/")
        endpoint_path = "/" + path.lstrip("/")
        full_path = f"{base_path}{endpoint_path}" if base_path else endpoint_path
        return urllib_parse.urlunsplit((parsed.scheme, parsed.netloc, full_path, "", ""))

    def _require_token(self) -> str:
        token = self._config.token
        if token is None or token.strip() == "":
            raise GatewayConfigurationError("Gateway token is required for this endpoint.")
        return token

    def _request_error(self, status_code: int, response_body: bytes) -> GatewayRequestError:
        payload = _parse_error_payload(response_body, token=self._config.token)
        return GatewayRequestError(payload=payload, status_code=status_code)


def _decode_json(response_body: bytes, context: str) -> object:
    if response_body == b"":
        raise GatewayResponseError(f"Gateway returned empty {context}.")
    try:
        return json.loads(response_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise GatewayResponseError(f"Gateway returned malformed JSON {context}.") from None


def _parse_error_payload(response_body: bytes, *, token: str | None) -> GatewayErrorPayload:
    payload = _as_mapping(_decode_json(response_body, "error response"), "error response")
    error = _required_mapping(payload, "error", "error envelope")
    message = _redact_token(_required_str(error, "message", "error envelope"), token)
    request_id = _optional_str(error, "requestId", "error envelope")
    metadata = _optional_mapping(error, "metadata", "error envelope")
    return GatewayErrorPayload(
        code=_required_str(error, "code", "error envelope"),
        message=message,
        request_id=request_id,
        metadata=metadata,
    )


def _close_response(response: object | None) -> None:
    if response is None:
        return
    close = getattr(response, "close", None)
    if close is not None:
        close()


def _iter_sse_events(response: object) -> Iterator[tuple[str, str]]:
    event_name: str | None = None
    data_lines: list[str] = []

    while True:
        raw_line = response.readline()
        if raw_line == b"" or raw_line == "":
            break

        line = _decode_sse_line(raw_line)
        if line == "":
            if event_name is None and not data_lines:
                continue
            if event_name is None:
                raise GatewayResponseError("Gateway returned malformed native stream event.")

            yield event_name, "\n".join(data_lines)
            event_name = None
            data_lines = []
            continue

        if line.startswith(":"):
            continue

        field, value = _split_sse_line(line)
        if field == "event":
            event_name = value
        elif field == "data":
            data_lines.append(value)

    if event_name is not None or data_lines:
        raise GatewayResponseError("Gateway stream ended before a terminal event.")


def _decode_sse_line(raw_line: object) -> str:
    if isinstance(raw_line, bytes):
        try:
            line = raw_line.decode("utf-8")
        except UnicodeDecodeError:
            raise GatewayResponseError("Gateway returned malformed native stream event.") from None
    elif isinstance(raw_line, str):
        line = raw_line
    else:
        raise GatewayResponseError("Gateway returned malformed native stream event.")

    if line.endswith("\n"):
        line = line[:-1]
    if line.endswith("\r"):
        line = line[:-1]
    return line


def _split_sse_line(line: str) -> tuple[str, str]:
    field, separator, value = line.partition(":")
    if separator and value.startswith(" "):
        value = value[1:]
    if not separator:
        value = ""
    return field, value


def _parse_stream_event(event_name: str, data: str, *, token: str | None) -> ChatStreamEvent:
    if event_name == "chunk":
        payload = _as_mapping(_decode_sse_json(data, "stream chunk event"), "stream chunk event")
        return StreamChunkEvent(text=_required_str(payload, "text", "stream chunk event"))

    if event_name == "done":
        return _parse_stream_done(_decode_sse_json(data, "stream done event"))

    if event_name == "error":
        return StreamErrorEvent(error=_parse_error_payload(data.encode("utf-8"), token=token))

    raise GatewayResponseError("Gateway returned unknown native stream event.")


def _decode_sse_json(data: str, context: str) -> object:
    if data == "":
        raise GatewayResponseError(f"Gateway returned empty {context}.")
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        raise GatewayResponseError(f"Gateway returned malformed JSON {context}.") from None


def _parse_stream_done(value: object) -> StreamDoneEvent:
    payload = _as_mapping(value, "stream done event")
    finish_reason = _required_str(payload, "finishReason", "stream done event")
    if finish_reason != "stop":
        raise GatewayResponseError("Gateway returned malformed stream done event.")

    return StreamDoneEvent(
        id=_required_str(payload, "id", "stream done event"),
        model=_required_str(payload, "model", "stream done event"),
        finish_reason="stop",
        metadata=_required_mapping(payload, "metadata", "stream done event"),
    )


def _parse_health(value: object) -> GatewayHealth:
    payload = _as_mapping(value, "health response")
    return GatewayHealth(
        status=_required_str(payload, "status", "health response"),
        version=_required_str(payload, "version", "health response"),
        host=_required_str(payload, "host", "health response"),
        port=_required_int(payload, "port", "health response"),
        started_at=_required_str(payload, "startedAt", "health response"),
        auth=_required_str(payload, "auth", "health response"),
    )


def _parse_models(value: object) -> list[GatewayModel]:
    payload = _as_mapping(value, "model listing response")
    models = _required_sequence(payload, "models", "model listing response")
    return [_parse_model(model) for model in models]


def _parse_model(value: object) -> GatewayModel:
    payload = _as_mapping(value, "model listing response")
    capabilities = _required_mapping(payload, "capabilities", "model listing response")
    return GatewayModel(
        id=_required_str(payload, "id", "model listing response"),
        name=_required_str(payload, "name", "model listing response"),
        vendor=_optional_str(payload, "vendor", "model listing response"),
        family=_optional_str(payload, "family", "model listing response"),
        version=_optional_str(payload, "version", "model listing response"),
        capabilities=GatewayModelCapabilities(
            streaming=_required_bool(capabilities, "streaming", "model listing response"),
            tool_calling=_optional_bool(
                capabilities, "toolCalling", "model listing response", default=False
            ),
            structured_output=_optional_bool(
                capabilities, "structuredOutput", "model listing response", default=False
            ),
        ),
    )


def _serialize_tool_call(tool_call: GatewayToolCall) -> dict[str, object]:
    return {
        "id": tool_call.id,
        "name": tool_call.name,
        "input": dict(tool_call.input),
    }


def _serialize_chat_message(message: ChatMessage) -> dict[str, object]:
    if message.role == "tool":
        payload: dict[str, object] = {"role": "tool", "content": message.content}
        if message.tool_call_id is not None:
            payload["toolCallId"] = message.tool_call_id
        return payload

    payload = {"role": message.role, "content": message.content}
    if message.tool_calls:
        payload["toolCalls"] = [_serialize_tool_call(tool_call) for tool_call in message.tool_calls]
    return payload


def _serialize_tool(tool: GatewayTool) -> dict[str, object]:
    return {
        "name": tool.name,
        "description": tool.description,
        "inputSchema": dict(tool.input_schema),
    }


def _reject_tool_enabled_stream_request(request: ChatRequest) -> None:
    if request.tools:
        raise GatewayConfigurationError("Native gateway streaming does not support tools yet.")

    for message in request.messages:
        if message.role == "tool" or message.tool_calls:
            raise GatewayConfigurationError("Native gateway streaming does not support tools yet.")


def _serialize_chat_request(request: ChatRequest) -> dict[str, object]:
    payload: dict[str, object] = {
        "model": request.model,
        "messages": [_serialize_chat_message(message) for message in request.messages],
    }
    if request.request_id is not None:
        payload["requestId"] = request.request_id
    if request.metadata:
        payload["metadata"] = dict(request.metadata)
    if request.tools:
        payload["tools"] = [_serialize_tool(tool) for tool in request.tools]
    return payload


def _parse_chat_response(value: object) -> ChatResponse:
    payload = _as_mapping(value, "chat response")
    message = _parse_chat_message(_required_mapping(payload, "message", "chat response"))
    if message.role != "assistant":
        raise GatewayResponseError("Gateway returned malformed chat response.")
    finish_reason = _required_str(payload, "finishReason", "chat response")
    has_tool_calls = bool(message.tool_calls)
    if has_tool_calls and finish_reason != "toolCalls":
        raise GatewayResponseError("Gateway returned malformed chat response.")
    if not has_tool_calls and finish_reason != "stop":
        raise GatewayResponseError("Gateway returned malformed chat response.")
    usage = payload.get("usage", _MISSING)
    if usage is not None:
        raise GatewayResponseError("Gateway returned malformed chat response.")

    return ChatResponse(
        id=_required_str(payload, "id", "chat response"),
        model=_required_str(payload, "model", "chat response"),
        created=_required_str(payload, "created", "chat response"),
        message=message,
        finish_reason=finish_reason,
        usage=None,
        metadata=_required_mapping(payload, "metadata", "chat response"),
    )


def _parse_tool_call(value: object) -> GatewayToolCall:
    payload = _as_mapping(value, "chat response tool call")
    input_value = _required_mapping(payload, "input", "chat response tool call")
    return GatewayToolCall(
        id=_required_nonblank_str(payload, "id", "chat response tool call"),
        name=_required_nonblank_str(payload, "name", "chat response tool call"),
        input=input_value,
    )


def _parse_tool_calls(payload: dict[str, object]) -> tuple[GatewayToolCall, ...]:
    value = payload.get("toolCalls", _MISSING)
    if value is _MISSING:
        return ()
    if not isinstance(value, list) or not value:
        raise GatewayResponseError("Gateway returned malformed chat message.")
    return tuple(_parse_tool_call(item) for item in value)


def _parse_chat_message(payload: dict[str, object]) -> ChatMessage:
    role = _required_str(payload, "role", "chat message")
    if role not in {"system", "user", "assistant", "tool"}:
        raise GatewayResponseError("Gateway returned malformed chat message.")
    return ChatMessage(
        role=role,
        content=_required_str(payload, "content", "chat message"),
        tool_calls=_parse_tool_calls(payload),
    )