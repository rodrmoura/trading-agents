import pytest

from scripts import smoke_vscode_provider as smoke


URL = "http://127.0.0.1:48123"
TOKEN = "synthetic-secret-token"
MODEL = "copilot/gpt-test"


def _set_gateway_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(smoke._GATEWAY_URL_ENV, URL)
    monkeypatch.setenv(smoke._GATEWAY_TOKEN_ENV, TOKEN)


def _fail_factory(**kwargs):
    raise AssertionError("factory should not be called")


@pytest.mark.parametrize(
    ("url_value", "token_value", "expected_name"),
    [
        (None, TOKEN, smoke._GATEWAY_URL_ENV),
        ("   ", TOKEN, smoke._GATEWAY_URL_ENV),
        (URL, None, smoke._GATEWAY_TOKEN_ENV),
        (URL, "   ", smoke._GATEWAY_TOKEN_ENV),
    ],
)
def test_missing_or_blank_env_returns_nonzero_without_factory_call(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    url_value: str | None,
    token_value: str | None,
    expected_name: str,
) -> None:
    if url_value is None:
        monkeypatch.delenv(smoke._GATEWAY_URL_ENV, raising=False)
    else:
        monkeypatch.setenv(smoke._GATEWAY_URL_ENV, url_value)

    if token_value is None:
        monkeypatch.delenv(smoke._GATEWAY_TOKEN_ENV, raising=False)
    else:
        monkeypatch.setenv(smoke._GATEWAY_TOKEN_ENV, token_value)

    monkeypatch.setattr(smoke, "create_llm_client", _fail_factory)

    result = smoke.main(["--model", MODEL, "--no-invoke"])

    output = capsys.readouterr().out
    assert result != 0
    assert expected_name in output
    assert TOKEN not in output


@pytest.mark.parametrize("args", [[], ["--model", ""], ["--model", "   "]])
def test_missing_or_blank_model_returns_nonzero_before_construction(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    args: list[str],
) -> None:
    _set_gateway_env(monkeypatch)
    monkeypatch.setattr(smoke, "create_llm_client", _fail_factory)

    result = smoke.main(args)

    output = capsys.readouterr().out
    assert result != 0
    assert "--model" in output
    assert TOKEN not in output


def test_construction_only_mode_builds_client_without_invoking(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _set_gateway_env(monkeypatch)
    calls = []

    class DummyLLM:
        def invoke(self, prompt: str):
            raise AssertionError("invoke should not be called")

    class DummyClient:
        get_llm_called = False

        def get_llm(self):
            self.get_llm_called = True
            return DummyLLM()

    client = DummyClient()

    def fake_factory(**kwargs):
        calls.append(kwargs)
        return client

    monkeypatch.setattr(smoke, "create_llm_client", fake_factory)

    result = smoke.main(["--model", MODEL, "--no-invoke"])

    output = capsys.readouterr().out
    assert result == 0
    assert calls == [
        {
            "provider": "vscode",
            "model": MODEL,
            "base_url": URL,
            "token": TOKEN,
        }
    ]
    assert client.get_llm_called is True
    assert "construction succeeded" in output
    assert "No invocation requested" in output
    assert TOKEN not in output


def test_direct_invocation_mode_invokes_and_prints_assistant_content(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _set_gateway_env(monkeypatch)
    prompts = []

    class DummyResponse:
        content = "Direct provider smoke passed."

    class DummyLLM:
        def invoke(self, prompt: str):
            prompts.append(prompt)
            return DummyResponse()

    class DummyClient:
        def get_llm(self):
            return DummyLLM()

    monkeypatch.setattr(smoke, "create_llm_client", lambda **kwargs: DummyClient())

    result = smoke.main(["--model", MODEL, "--prompt", "Say hello once."])

    output = capsys.readouterr().out
    assert result == 0
    assert prompts == ["Say hello once."]
    assert "Assistant response:" in output
    assert "Direct provider smoke passed." in output
    assert TOKEN not in output


def test_successful_assistant_output_redacts_configured_token(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _set_gateway_env(monkeypatch)

    class DummyResponse:
        content = f"Smoke passed with token {TOKEN}."

    class DummyLLM:
        def invoke(self, prompt: str):
            return DummyResponse()

    class DummyClient:
        def get_llm(self):
            return DummyLLM()

    monkeypatch.setattr(smoke, "create_llm_client", lambda **kwargs: DummyClient())

    result = smoke.main(["--model", MODEL])

    output = capsys.readouterr().out
    assert result == 0
    assert "Assistant response:" in output
    assert smoke._REDACTION in output
    assert TOKEN not in output


def test_blank_prompt_returns_nonzero_before_construction(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _set_gateway_env(monkeypatch)
    monkeypatch.setattr(smoke, "create_llm_client", _fail_factory)

    result = smoke.main(["--model", MODEL, "--prompt", "   "])

    output = capsys.readouterr().out
    assert result != 0
    assert "--prompt" in output
    assert TOKEN not in output


@pytest.mark.parametrize("stage", ["factory", "get_llm", "invoke"])
def test_exception_output_redacts_configured_token(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stage: str,
) -> None:
    _set_gateway_env(monkeypatch)

    class ExplodingLLM:
        def invoke(self, prompt: str):
            raise RuntimeError(f"invoke failed with {TOKEN}")

    class ExplodingGetLLMClient:
        def get_llm(self):
            raise RuntimeError(f"get_llm failed with {TOKEN}")

    class ExplodingInvokeClient:
        def get_llm(self):
            return ExplodingLLM()

    def fake_factory(**kwargs):
        if stage == "factory":
            raise RuntimeError(f"factory failed with {TOKEN}")
        if stage == "get_llm":
            return ExplodingGetLLMClient()
        return ExplodingInvokeClient()

    monkeypatch.setattr(smoke, "create_llm_client", fake_factory)

    result = smoke.main(["--model", MODEL])

    output = capsys.readouterr().out
    assert result != 0
    assert "Smoke FAILED" in output
    assert smoke._REDACTION in output
    assert TOKEN not in output