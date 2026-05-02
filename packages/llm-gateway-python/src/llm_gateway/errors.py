"""SDK errors for the native LLM gateway."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class GatewayErrorPayload:
    """Native gateway error envelope payload."""

    code: str
    message: str
    request_id: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)


class LLMGatewayError(Exception):
    """Base class for SDK errors."""


class GatewayConfigurationError(LLMGatewayError):
    """Raised when local client configuration is invalid."""


class GatewayRequestError(LLMGatewayError):
    """Raised for native gateway error responses."""

    def __init__(self, payload: GatewayErrorPayload, status_code: int | None = None) -> None:
        super().__init__(payload.message)
        self.payload = payload
        self.status_code = status_code

    @property
    def code(self) -> str:
        return self.payload.code

    @property
    def request_id(self) -> str | None:
        return self.payload.request_id


class GatewayResponseError(LLMGatewayError):
    """Raised when a gateway response is not valid native JSON."""


class GatewayTransportError(LLMGatewayError):
    """Raised when the SDK cannot complete the HTTP request."""