"""Public native gateway data types."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Literal, TypeAlias

from .errors import GatewayErrorPayload

ChatRole: TypeAlias = Literal["system", "user", "assistant", "tool"]
FinishReason: TypeAlias = Literal["stop", "toolCalls"]


@dataclass(frozen=True, slots=True)
class GatewayHealth:
    status: str
    version: str
    host: str
    port: int
    started_at: str
    auth: Literal["bearer"] = "bearer"


@dataclass(frozen=True, slots=True)
class GatewayModelCapabilities:
    streaming: bool
    tool_calling: bool = False
    structured_output: bool = False


@dataclass(frozen=True, slots=True)
class GatewayModel:
    id: str
    name: str
    vendor: str | None = None
    family: str | None = None
    version: str | None = None
    capabilities: GatewayModelCapabilities = field(
        default_factory=lambda: GatewayModelCapabilities(streaming=False)
    )


@dataclass(frozen=True, slots=True)
class GatewayTool:
    name: str
    description: str = ""
    input_schema: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GatewayToolCall:
    id: str
    name: str
    input: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: ChatRole
    content: str
    tool_calls: Sequence[GatewayToolCall] = ()
    tool_call_id: str | None = None


@dataclass(frozen=True, slots=True)
class ChatRequest:
    model: str
    messages: Sequence[ChatMessage]
    request_id: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)
    tools: Sequence[GatewayTool] = ()


@dataclass(frozen=True, slots=True)
class ChatResponse:
    id: str
    model: str
    created: str
    message: ChatMessage
    finish_reason: FinishReason
    usage: None = None
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class StreamChunkEvent:
    text: str


@dataclass(frozen=True, slots=True)
class StreamDoneEvent:
    id: str
    model: str
    finish_reason: FinishReason
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class StreamErrorEvent:
    error: GatewayErrorPayload


ChatStreamEvent: TypeAlias = StreamChunkEvent | StreamDoneEvent | StreamErrorEvent