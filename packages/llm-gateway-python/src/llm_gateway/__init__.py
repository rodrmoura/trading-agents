"""Generic Python SDK skeleton for the native LLM gateway."""

from .client import GatewayClient, GatewayClientConfig
from .errors import (
    GatewayConfigurationError,
    GatewayErrorPayload,
    GatewayRequestError,
    GatewayResponseError,
    GatewayTransportError,
    LLMGatewayError,
)
from .types import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatRole,
    ChatStreamEvent,
    GatewayHealth,
    GatewayModel,
    GatewayModelCapabilities,
    StreamChunkEvent,
    StreamDoneEvent,
    StreamErrorEvent,
)

__version__ = "0.0.1"

__all__ = [
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ChatRole",
    "ChatStreamEvent",
    "GatewayClient",
    "GatewayClientConfig",
    "GatewayConfigurationError",
    "GatewayErrorPayload",
    "GatewayHealth",
    "GatewayModel",
    "GatewayModelCapabilities",
    "GatewayRequestError",
    "GatewayResponseError",
    "GatewayTransportError",
    "LLMGatewayError",
    "StreamChunkEvent",
    "StreamDoneEvent",
    "StreamErrorEvent",
    "__version__",
]