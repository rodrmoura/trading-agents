import importlib
import sys
import warnings

import pytest

from tradingagents.llm_clients.factory import create_llm_client
from tradingagents.llm_clients.validators import validate_model
from tradingagents.llm_clients.vscode_client import VSCodeClient


def test_factory_creates_vscode_client_without_importing_sdk() -> None:
    sys.modules.pop("llm_gateway", None)
    sys.modules.pop("llm_gateway.langchain_adapter", None)

    client = create_llm_client(
        "vscode",
        "opaque-model",
        base_url="http://127.0.0.1:12345",
        token="synthetic-token",
    )

    assert isinstance(client, VSCodeClient)
    assert "llm_gateway" not in sys.modules
    assert "llm_gateway.langchain_adapter" not in sys.modules


def test_vscode_client_returns_gateway_chat_model_when_sdk_available() -> None:
    pytest.importorskip("llm_gateway")
    pytest.importorskip("langchain_core")

    from llm_gateway.langchain_adapter import GatewayChatModel

    token = "synthetic-token"
    client = VSCodeClient(
        "opaque-model",
        base_url="http://127.0.0.1:12345",
        token=token,
    )

    llm = client.get_llm()

    assert isinstance(llm, GatewayChatModel)
    assert llm.model == "opaque-model"
    assert llm.client.config.base_url == "http://127.0.0.1:12345"
    assert token not in repr(llm)


def test_vscode_client_requires_gateway_url(monkeypatch: pytest.MonkeyPatch) -> None:
    token = "synthetic-token"
    monkeypatch.delenv("TRADINGAGENTS_VSCODE_GATEWAY_URL", raising=False)
    monkeypatch.setenv("TRADINGAGENTS_VSCODE_GATEWAY_TOKEN", "env-token")

    client = VSCodeClient("opaque-model", token=token)

    with pytest.raises(ValueError) as exc_info:
        client.get_llm()

    message = str(exc_info.value)
    assert "TRADINGAGENTS_VSCODE_GATEWAY_URL" in message
    assert token not in message


def test_vscode_client_requires_gateway_token(monkeypatch: pytest.MonkeyPatch) -> None:
    token_like_value = "synthetic-secret-token"
    monkeypatch.setenv("TRADINGAGENTS_VSCODE_GATEWAY_URL", "http://127.0.0.1:12345")
    monkeypatch.delenv("TRADINGAGENTS_VSCODE_GATEWAY_TOKEN", raising=False)

    client = VSCodeClient("opaque-model", token=" ")

    with pytest.raises(ValueError) as exc_info:
        client.get_llm()

    message = str(exc_info.value)
    assert "TRADINGAGENTS_VSCODE_GATEWAY_TOKEN" in message
    assert token_like_value not in message


def test_vscode_client_missing_sdk_raises_setup_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import_module = importlib.import_module

    def fail_gateway_import(name: str, package: str | None = None):
        if name in {"llm_gateway", "llm_gateway.langchain_adapter"}:
            raise ImportError("No module named 'llm_gateway'")
        return real_import_module(name, package)

    monkeypatch.setattr(importlib, "import_module", fail_gateway_import)
    token = "synthetic-token"
    client = VSCodeClient(
        "opaque-model",
        base_url="http://127.0.0.1:12345",
        token=token,
    )

    with pytest.raises(ImportError) as exc_info:
        client.get_llm()

    message = str(exc_info.value)
    assert "packages/llm-gateway-python" in message
    assert "llm-gateway[langchain]" in message
    assert token not in message


def test_vscode_validation_accepts_opaque_model_ids_without_warning() -> None:
    client = VSCodeClient("any-provider-owned/model:id")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        client.warn_if_unknown_model()

    assert caught == []
    assert client.validate_model() is True
    assert validate_model("vscode", "any-opaque-id") is True


def test_cli_provider_selection_includes_vscode_gateway(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from cli import utils as cli_utils

    captured = {}

    class Prompt:
        def ask(self):
            return "vscode", None

    def fake_select(message, choices, **kwargs):
        captured["choices"] = choices
        return Prompt()

    monkeypatch.setattr(cli_utils.questionary, "select", fake_select)

    assert cli_utils.select_llm_provider() == ("vscode", None)
    provider_choices = [
        (getattr(choice, "title", None), getattr(choice, "value", None))
        for choice in captured["choices"]
    ]
    assert ("VS Code Gateway", ("vscode", None)) in provider_choices


def test_cli_vscode_model_selection_prompts_for_custom_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from cli import utils as cli_utils

    captured = {}

    class Prompt:
        def ask(self):
            return "gateway-model-id "

    def fake_text(message, **kwargs):
        captured["message"] = message
        return Prompt()

    def fail_model_options(provider: str, mode: str):
        raise AssertionError("VS Code Gateway must not use static model options")

    monkeypatch.setattr(cli_utils.questionary, "text", fake_text)
    monkeypatch.setattr(cli_utils, "get_model_options", fail_model_options)

    assert cli_utils._select_model("vscode", "quick") == "gateway-model-id"
    assert "/v1/models" in captured["message"]
    assert "runbook" in captured["message"]


def test_cli_vscode_model_selection_handles_cancellation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from cli import utils as cli_utils

    class Prompt:
        def ask(self):
            return None

    monkeypatch.setattr(cli_utils.questionary, "text", lambda *args, **kwargs: Prompt())

    with pytest.raises(SystemExit) as exc_info:
        cli_utils._select_model("vscode", "deep")

    assert exc_info.value.code == 1