"""LangChain Core adapter for the native gateway SDK."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from pydantic import ConfigDict, Field

from .client import GatewayClient
from .errors import GatewayConfigurationError, GatewayErrorPayload, GatewayRequestError
from .types import (
    ChatMessage,
    ChatRequest,
    StreamChunkEvent,
    StreamDoneEvent,
    StreamErrorEvent,
)


_ROLE_MAP = {
    "ai": "assistant",
    "assistant": "assistant",
    "human": "user",
    "system": "system",
    "user": "user",
}


class GatewayChatModel(BaseChatModel):
    """Small LangChain Core chat model backed by ``GatewayClient``."""

    client: GatewayClient = Field(repr=False, exclude=True)
    model: str
    request_metadata: Mapping[str, object] = Field(default_factory=dict, repr=False, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def _llm_type(self) -> str:
        return "llm_gateway"

    @property
    def _identifying_params(self) -> dict[str, object]:
        return {"model": self.model}

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: object | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        _reject_stop(stop)
        _reject_kwargs(kwargs)

        response = self.client.chat(self._chat_request(messages))
        response_metadata = {
            "id": response.id,
            "model": response.model,
            "finish_reason": response.finish_reason,
        }
        message = AIMessage(content=response.message.content, response_metadata=response_metadata)
        return ChatResult(
            generations=[ChatGeneration(message=message, generation_info=response_metadata)]
        )

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: object | None = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        _reject_stop(stop)
        _reject_kwargs(kwargs)

        for event in self.client.stream_chat(self._chat_request(messages)):
            if isinstance(event, StreamChunkEvent):
                yield ChatGenerationChunk(message=AIMessageChunk(content=event.text))
            elif isinstance(event, StreamDoneEvent):
                return
            elif isinstance(event, StreamErrorEvent):
                raise GatewayRequestError(payload=_safe_error_payload(event.error, self.client))
            else:
                raise GatewayConfigurationError("Unsupported native stream event from gateway client.")

    def with_structured_output(
        self,
        schema: dict[str, Any] | type,
        *,
        include_raw: bool = False,
        **kwargs: Any,
    ) -> object:
        raise NotImplementedError(
            "Structured output is not supported by llm_gateway yet; use free-text generation."
        )

    def bind_tools(
        self,
        tools: Sequence[object],
        *,
        tool_choice: str | None = None,
        **kwargs: Any,
    ) -> object:
        raise NotImplementedError("Native gateway tool calling is deferred for llm_gateway.")

    def _chat_request(self, messages: Sequence[BaseMessage]) -> ChatRequest:
        return ChatRequest(
            model=self.model,
            messages=[_to_native_message(message) for message in messages],
            metadata=dict(self.request_metadata),
        )


def _to_native_message(message: BaseMessage) -> ChatMessage:
    role_value = getattr(message, "role", None) or getattr(message, "type", None)
    role = _ROLE_MAP.get(role_value)
    if role is None:
        raise GatewayConfigurationError("Unsupported LangChain message role for native gateway.")

    return ChatMessage(role=role, content=_content_to_text(message.content))


def _content_to_text(content: object) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, Mapping):
        return _text_from_block(content)

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, Mapping):
                block_text = _text_from_optional_block(item)
                if block_text is not None:
                    parts.append(block_text)
            else:
                raise GatewayConfigurationError(
                    "Unsupported LangChain message content for native gateway."
                )
        return "".join(parts)

    raise GatewayConfigurationError("Unsupported LangChain message content for native gateway.")


def _text_from_optional_block(block: Mapping[object, object]) -> str | None:
    if block.get("type") != "text":
        return None
    return _text_from_block(block)


def _text_from_block(block: Mapping[object, object]) -> str:
    if block.get("type") != "text":
        raise GatewayConfigurationError("Unsupported LangChain message content for native gateway.")
    text = block.get("text")
    if not isinstance(text, str):
        raise GatewayConfigurationError("Unsupported LangChain message content for native gateway.")
    return text


def _reject_stop(stop: list[str] | None) -> None:
    if stop:
        raise NotImplementedError("Stop sequences are not supported by the native gateway adapter.")


def _reject_kwargs(kwargs: Mapping[str, object]) -> None:
    if not kwargs:
        return
    names = ", ".join(sorted(kwargs))
    raise ValueError(f"Unsupported generation options for native gateway adapter: {names}.")


def _safe_error_payload(error: GatewayErrorPayload, client: GatewayClient) -> GatewayErrorPayload:
    token = getattr(getattr(client, "config", None), "token", None)
    message = error.message
    if token:
        message = message.replace(token, "<redacted>")
    return GatewayErrorPayload(
        code=error.code,
        message=message,
        request_id=error.request_id,
        metadata=error.metadata,
    )