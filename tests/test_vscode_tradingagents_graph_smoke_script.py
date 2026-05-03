from pathlib import Path

import pytest

from scripts import smoke_vscode_tradingagents_graph as smoke


URL = "http://127.0.0.1:48123"
TOKEN = "synthetic-secret-token"
MODEL = "copilot/gpt-test"


def _set_gateway_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(smoke._GATEWAY_URL_ENV, URL)
    monkeypatch.setenv(smoke._GATEWAY_TOKEN_ENV, TOKEN)


class FailingGraph:
    def __init__(self, *args, **kwargs):
        raise AssertionError("graph should not be constructed")


def _valid_state() -> dict[str, str]:
    return {
        "market_report": "MARKET_REPORT_BODY_SHOULD_NOT_PRINT",
        "sentiment_report": "SENTIMENT_REPORT_BODY_SHOULD_NOT_PRINT",
        "news_report": "NEWS_REPORT_BODY_SHOULD_NOT_PRINT",
        "fundamentals_report": "FUNDAMENTALS_REPORT_BODY_SHOULD_NOT_PRINT",
        "investment_plan": "INVESTMENT_PLAN_BODY_SHOULD_NOT_PRINT",
        "trader_investment_plan": "TRADER_PLAN_BODY_SHOULD_NOT_PRINT",
        "final_trade_decision": "FINAL_DECISION_BODY_SHOULD_NOT_PRINT",
    }


def _install_graph(
    monkeypatch: pytest.MonkeyPatch,
    *,
    final_state: dict[str, object] | None = None,
    processed_decision: object = "Processed HOLD",
) -> dict[str, object]:
    captured: dict[str, object] = {}

    class DummyGraph:
        def __init__(self, selected_analysts, debug, config):
            captured["selected_analysts"] = selected_analysts
            captured["debug"] = debug
            captured["config"] = config

        def propagate(self, ticker, trade_date):
            captured["ticker"] = ticker
            captured["trade_date"] = trade_date
            return final_state if final_state is not None else _valid_state(), processed_decision

    monkeypatch.setattr(smoke, "TradingAgentsGraph", DummyGraph)
    return captured


@pytest.mark.parametrize(
    ("url_value", "token_value", "expected_name"),
    [
        (None, TOKEN, smoke._GATEWAY_URL_ENV),
        ("   ", TOKEN, smoke._GATEWAY_URL_ENV),
        (URL, None, smoke._GATEWAY_TOKEN_ENV),
        (URL, "   ", smoke._GATEWAY_TOKEN_ENV),
    ],
)
def test_missing_or_blank_env_returns_input_error_before_graph_construction(
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

    monkeypatch.setattr(smoke, "TradingAgentsGraph", FailingGraph)

    result = smoke.main(["--model", MODEL])

    output = capsys.readouterr().out
    assert result == 2
    assert expected_name in output
    assert TOKEN not in output


def test_parser_level_errors_redact_configured_token_before_env_validation(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.delenv(smoke._GATEWAY_URL_ENV, raising=False)
    monkeypatch.setenv(smoke._GATEWAY_TOKEN_ENV, TOKEN)
    monkeypatch.setattr(smoke, "TradingAgentsGraph", FailingGraph)

    result = smoke.main(["--model", MODEL, "--unexpected-token", TOKEN])

    output = capsys.readouterr().out
    assert result == 2
    assert "unrecognized arguments" in output
    assert smoke._REDACTION in output
    assert TOKEN not in output
    assert smoke._GATEWAY_URL_ENV not in output


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        ([], "--model"),
        (["--model", "   "], "--model"),
        (["--model", MODEL, "--ticker", "   "], "--ticker"),
        (["--model", MODEL, "--trade-date", "   "], "--trade-date"),
        (["--model", MODEL, "--trade-date", "2024/05/10"], "YYYY-MM-DD"),
        (["--model", MODEL, "--trade-date", "2024-5-10"], "YYYY-MM-DD"),
        (["--model", MODEL, "--analysts", "market,"], "blank entries"),
        (["--model", MODEL, "--analysts", "market,charts"], "Invalid --analysts"),
        (["--model", MODEL, "--analysts", "market,Market"], "Duplicate --analysts"),
        (["--model", MODEL, "--max-debate-rounds", "0"], ">= 1"),
        (["--model", MODEL, "--max-risk-discuss-rounds", "0"], ">= 1"),
    ],
)
def test_invalid_inputs_return_two_before_graph_construction(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    args: list[str],
    expected: str,
) -> None:
    _set_gateway_env(monkeypatch)
    monkeypatch.setattr(smoke, "TradingAgentsGraph", FailingGraph)

    result = smoke.main(args)

    output = capsys.readouterr().out
    assert result == 2
    assert expected in output
    assert TOKEN not in output


def test_success_builds_isolated_vscode_graph_config_and_runs_propagate(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _set_gateway_env(monkeypatch)
    captured = _install_graph(monkeypatch)

    result = smoke.main(
        [
            "--model",
            MODEL,
            "--ticker",
            "MSFT",
            "--trade-date",
            "2024-05-10",
            "--analysts",
            "market,News",
            "--output-dir",
            str(tmp_path),
            "--max-debate-rounds",
            "2",
            "--max-risk-discuss-rounds",
            "3",
        ]
    )

    output = capsys.readouterr().out
    config = captured["config"]
    assert result == 0
    assert captured["selected_analysts"] == ["market", "news"]
    assert captured["debug"] is False
    assert captured["ticker"] == "MSFT"
    assert captured["trade_date"] == "2024-05-10"
    assert config["llm_provider"] == "vscode"
    assert config["deep_think_llm"] == MODEL
    assert config["quick_think_llm"] == MODEL
    assert config["backend_url"] == URL
    assert config["results_dir"] == tmp_path / "results"
    assert config["data_cache_dir"] == tmp_path / "cache"
    assert config["memory_log_path"] == tmp_path / "memory" / "trading_memory.md"
    assert config["max_debate_rounds"] == 2
    assert config["max_risk_discuss_rounds"] == 3
    assert config["checkpoint_enabled"] is False
    assert smoke.DEFAULT_CONFIG["llm_provider"] != "vscode"
    assert "construction and propagate() succeeded" in output
    assert "analysts: market, news" in output
    assert TOKEN not in output


def test_omitted_output_dir_uses_persistent_temp_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    generated_root = tmp_path / "generated-temp-root"
    _set_gateway_env(monkeypatch)
    captured = _install_graph(monkeypatch)
    monkeypatch.setattr(smoke.tempfile, "mkdtemp", lambda prefix: str(generated_root))

    result = smoke.main(["--model", MODEL])

    output = capsys.readouterr().out
    config = captured["config"]
    assert result == 0
    assert config["results_dir"] == generated_root / "results"
    assert generated_root.exists()
    assert str(generated_root) in output


def test_success_summary_redacts_token_and_omits_full_report_bodies(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _set_gateway_env(monkeypatch)
    _install_graph(
        monkeypatch,
        processed_decision=f"Processed HOLD with token {TOKEN}.",
    )

    result = smoke.main(["--model", MODEL, "--output-dir", str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert smoke._REDACTION in output
    assert TOKEN not in output
    assert "MARKET_REPORT_BODY_SHOULD_NOT_PRINT" not in output
    assert "INVESTMENT_PLAN_BODY_SHOULD_NOT_PRINT" not in output
    assert "market_report:" in output
    assert "investment_plan:" in output


@pytest.mark.parametrize(
    ("analysts", "field_name", "field_value"),
    [
        ("market", "market_report", "   "),
        ("social", "sentiment_report", ""),
        ("market", "investment_plan", None),
        ("market", "trader_investment_plan", "   "),
        ("market", "final_trade_decision", ""),
    ],
)
def test_final_state_selected_and_downstream_fields_must_be_nonblank_strings(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    analysts: str,
    field_name: str,
    field_value: object,
) -> None:
    _set_gateway_env(monkeypatch)
    state: dict[str, object] = _valid_state()
    state[field_name] = field_value
    _install_graph(monkeypatch, final_state=state)

    result = smoke.main(
        ["--model", MODEL, "--analysts", analysts, "--output-dir", str(tmp_path)]
    )

    output = capsys.readouterr().out
    assert result == 1
    assert "Smoke FAILED" in output
    assert field_name in output
    assert TOKEN not in output


def test_processed_decision_must_be_nonblank(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _set_gateway_env(monkeypatch)
    _install_graph(monkeypatch, processed_decision="   ")

    result = smoke.main(["--model", MODEL, "--output-dir", str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "processed decision" in output
    assert TOKEN not in output


@pytest.mark.parametrize("stage", ["construct", "propagate"])
def test_graph_construction_and_propagate_exceptions_are_redacted(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    stage: str,
) -> None:
    _set_gateway_env(monkeypatch)

    class ExplodingGraph:
        def __init__(self, selected_analysts, debug, config):
            if stage == "construct":
                raise RuntimeError(f"construction failed with {TOKEN}")

        def propagate(self, ticker, trade_date):
            raise RuntimeError(f"propagate failed with {TOKEN}")

    monkeypatch.setattr(smoke, "TradingAgentsGraph", ExplodingGraph)

    result = smoke.main(["--model", MODEL, "--output-dir", str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Smoke FAILED" in output
    assert smoke._REDACTION in output
    assert TOKEN not in output