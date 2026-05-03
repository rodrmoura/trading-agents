import importlib
import os
from typing import Any, Optional

from .base_client import BaseLLMClient


_GATEWAY_URL_ENV = "TRADINGAGENTS_VSCODE_GATEWAY_URL"
_GATEWAY_TOKEN_ENV = "TRADINGAGENTS_VSCODE_GATEWAY_TOKEN"
_INSTALL_ERROR = (
    "VS Code Gateway provider requires the package-local Python SDK with "
    "LangChain support. Install packages/llm-gateway-python with the "
    "llm-gateway[langchain] extra."
)


def _nonblank(value: object) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    return text


def _first_nonblank(*values: object) -> str | None:
    for value in values:
        text = _nonblank(value)
        if text:
            return text
    return None


def _load_gateway_classes():
    try:
        gateway_module = importlib.import_module("llm_gateway")
        adapter_module = importlib.import_module("llm_gateway.langchain_adapter")
    except ImportError as exc:
        raise ImportError(_INSTALL_ERROR) from exc

    try:
        return (
            gateway_module.GatewayClient,
            gateway_module.GatewayClientConfig,
            adapter_module.GatewayChatModel,
        )
    except AttributeError as exc:
        raise RuntimeError(_INSTALL_ERROR) from exc


class VSCodeClient(BaseLLMClient):
    """Client for the generic VS Code LLM Gateway provider."""

    def __init__(self, model: str, base_url: Optional[str] = None, **kwargs):
        super().__init__(model, base_url, **kwargs)
        self.provider = "vscode"

    def get_llm(self) -> Any:
        """Return configured GatewayChatModel instance."""
        self.warn_if_unknown_model()

        base_url = _first_nonblank(self.base_url, os.environ.get(_GATEWAY_URL_ENV))
        if base_url is None:
            raise ValueError(
                "VS Code Gateway base URL is required. "
                f"Pass base_url or set {_GATEWAY_URL_ENV}."
            )

        token = _first_nonblank(self.kwargs.get("token"), os.environ.get(_GATEWAY_TOKEN_ENV))
        if token is None:
            raise ValueError(
                "VS Code Gateway token is required. "
                f"Pass token or set {_GATEWAY_TOKEN_ENV}."
            )

        GatewayClient, GatewayClientConfig, GatewayChatModel = _load_gateway_classes()
        return GatewayChatModel(
            client=GatewayClient(GatewayClientConfig(base_url=base_url, token=token)),
            model=self.model,
        )

    def validate_model(self) -> bool:
        """VS Code Gateway model IDs are opaque and gateway-defined."""
        return True