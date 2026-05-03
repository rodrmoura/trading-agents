"""LangChain Core adapter for the native gateway SDK."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import ConfigDict, Field

from .client import GatewayClient
from .errors import GatewayConfigurationError, GatewayErrorPayload, GatewayRequestError
from .types import (
    ChatMessage,
    ChatRequest,
    GatewayTool,
    GatewayToolCall,
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
    bound_tools: tuple[GatewayTool, ...] = Field(default_factory=tuple, repr=False, exclude=True)

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
        message_kwargs: dict[str, object] = {
            "content": response.message.content,
            "response_metadata": response_metadata,
        }
        if response.message.tool_calls:
            message_kwargs["tool_calls"] = [
                {
                    "name": tool_call.name,
                    "args": dict(tool_call.input),
                    "id": tool_call.id,
                    "type": "tool_call",
                }
                for tool_call in response.message.tool_calls
            ]
        message = AIMessage(**message_kwargs)
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

    def bind_tools(
        self,
        tools: Sequence[object],
        *,
        tool_choice: str | None = None,
        **kwargs: Any,
    ) -> object:
        allow_any_tool_choice = "ls_structured_output_format" in kwargs
        kwargs.pop("ls_structured_output_format", None)
        _reject_tool_choice(tool_choice, allow_any=allow_any_tool_choice)
        _reject_bind_tool_kwargs(kwargs)
        return self.model_copy(update={"bound_tools": tuple(_to_native_tool(tool) for tool in tools)})

    def _chat_request(self, messages: Sequence[BaseMessage]) -> ChatRequest:
        return ChatRequest(
            model=self.model,
            messages=[_to_native_message(message) for message in messages],
            metadata=dict(self.request_metadata),
            tools=self.bound_tools,
        )


def _to_native_message(message: BaseMessage) -> ChatMessage:
    if isinstance(message, ToolMessage):
        tool_call_id = getattr(message, "tool_call_id", None)
        if not isinstance(tool_call_id, str) or tool_call_id.strip() == "":
            raise GatewayConfigurationError("Unsupported LangChain tool message for native gateway.")
        return ChatMessage(
            role="tool",
            content=_content_to_text(message.content),
            tool_call_id=tool_call_id,
        )

    if isinstance(message, AIMessage):
        return ChatMessage(
            role="assistant",
            content=_content_to_text(message.content),
            tool_calls=tuple(_to_native_tool_call(tool_call) for tool_call in (message.tool_calls or ())),
        )

    role_value = getattr(message, "role", None) or getattr(message, "type", None)
    role = _ROLE_MAP.get(role_value)
    if role is None:
        raise GatewayConfigurationError("Unsupported LangChain message role for native gateway.")

    return ChatMessage(role=role, content=_content_to_text(message.content))


def _to_native_tool_call(tool_call: object) -> GatewayToolCall:
    if not isinstance(tool_call, Mapping):
        raise GatewayConfigurationError("Unsupported LangChain tool call for native gateway.")

    call_id = tool_call.get("id")
    name = tool_call.get("name")
    args = tool_call.get("args")

    if not isinstance(call_id, str) or call_id.strip() == "":
        raise GatewayConfigurationError("Unsupported LangChain tool call for native gateway.")
    if not isinstance(name, str) or name.strip() == "":
        raise GatewayConfigurationError("Unsupported LangChain tool call for native gateway.")
    if not isinstance(args, Mapping):
        raise GatewayConfigurationError("Unsupported LangChain tool call for native gateway.")

    return GatewayToolCall(id=call_id, name=name, input=dict(args))


def _to_native_tool(tool: object) -> GatewayTool:
    converted = convert_to_openai_tool(tool)
    if not isinstance(converted, Mapping):
        raise GatewayConfigurationError("Unsupported LangChain tool definition for native gateway.")

    function = converted.get("function")
    if not isinstance(function, Mapping):
        raise GatewayConfigurationError("Unsupported LangChain tool definition for native gateway.")

    name = function.get("name")
    if not isinstance(name, str) or name.strip() == "":
        raise GatewayConfigurationError("Unsupported LangChain tool definition for native gateway.")

    description = function.get("description", "")
    if not isinstance(description, str):
        description = ""

    parameters = function.get("parameters", {})
    if parameters is None:
        parameters = {}
    if not isinstance(parameters, Mapping):
        raise GatewayConfigurationError("Unsupported LangChain tool definition for native gateway.")

    return GatewayTool(name=name, description=description, input_schema=dict(parameters))


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


def _reject_bind_tool_kwargs(kwargs: Mapping[str, object]) -> None:
    if not kwargs:
        return
    names = ", ".join(sorted(kwargs))
    raise ValueError(f"Unsupported bind_tools options for native gateway adapter: {names}.")


def _reject_tool_choice(tool_choice: object, *, allow_any: bool = False) -> None:
    if tool_choice is None or tool_choice == "auto" or (allow_any and tool_choice == "any"):
        return
    raise NotImplementedError("Only default or auto tool choice is supported by the native gateway adapter.")


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