"""Full-graph TradingAgents smoke harness for VS Code Gateway models."""

from __future__ import annotations

import argparse
import copy
import os
import sys
import tempfile
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph


_GATEWAY_URL_ENV = "TRADINGAGENTS_VSCODE_GATEWAY_URL"
_GATEWAY_TOKEN_ENV = "TRADINGAGENTS_VSCODE_GATEWAY_TOKEN"
_REDACTION = "[REDACTED]"
_TEMP_PREFIX = "tradingagents-vscode-graph-smoke-"
_ANALYST_REPORT_FIELDS = {
    "market": "market_report",
    "social": "sentiment_report",
    "news": "news_report",
    "fundamentals": "fundamentals_report",
}
_FIXED_FINAL_STATE_FIELDS = (
    "investment_plan",
    "trader_investment_plan",
    "final_trade_decision",
)


class _InputError(ValueError):
    pass


class _SmokeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise _InputError(message)


def _nonblank(value: object) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    return text


def _redact(value: object, token: str | None) -> str:
    text = str(value)
    if token:
        text = text.replace(token, _REDACTION)
    return text


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc

    if parsed < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return parsed


def _build_parser() -> argparse.ArgumentParser:
    parser = _SmokeArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        required=True,
        help="Required opaque VS Code Gateway model ID selected from /v1/models.",
    )
    parser.add_argument("--ticker", default="NVDA", help="Ticker symbol to run.")
    parser.add_argument(
        "--trade-date",
        default="2024-05-10",
        help="ISO trade date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--analysts",
        default="market",
        help="Comma-separated analysts: market,social,news,fundamentals.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output root. Defaults to a persistent temp directory.",
    )
    parser.add_argument(
        "--max-debate-rounds",
        type=_positive_int,
        default=1,
        help="Research debate rounds; must be >= 1.",
    )
    parser.add_argument(
        "--max-risk-discuss-rounds",
        type=_positive_int,
        default=1,
        help="Risk discussion rounds; must be >= 1.",
    )
    return parser


def _input_error(message: str, token: str | None = None) -> int:
    print(f"Error: {_redact(message, token)}")
    return 2


def _failure(message: object, token: str | None) -> int:
    print(f"Smoke FAILED: {_redact(message, token)}")
    return 1


def _require_nonblank(value: object, option_name: str) -> str:
    text = _nonblank(value)
    if text is None:
        raise _InputError(f"Missing required {option_name} value.")
    return text


def _parse_trade_date(value: object) -> str:
    trade_date = _require_nonblank(value, "--trade-date")
    try:
        parsed = datetime.strptime(trade_date, "%Y-%m-%d")
    except ValueError as exc:
        raise _InputError("Invalid --trade-date value; expected ISO YYYY-MM-DD.") from exc

    if parsed.strftime("%Y-%m-%d") != trade_date:
        raise _InputError("Invalid --trade-date value; expected ISO YYYY-MM-DD.")
    return trade_date


def _parse_analysts(value: object) -> list[str]:
    analysts_text = _require_nonblank(value, "--analysts")
    analysts: list[str] = []
    seen: set[str] = set()
    allowed = ", ".join(_ANALYST_REPORT_FIELDS)

    for raw_part in analysts_text.split(","):
        analyst = raw_part.strip().lower()
        if not analyst:
            raise _InputError("Invalid --analysts value; blank entries are not allowed.")
        if analyst not in _ANALYST_REPORT_FIELDS:
            raise _InputError(
                f"Invalid --analysts value '{analyst}'. Allowed values: {allowed}."
            )
        if analyst in seen:
            raise _InputError(f"Duplicate --analysts value: {analyst}.")
        seen.add(analyst)
        analysts.append(analyst)

    return analysts


def _output_root(value: object) -> Path:
    if value is None:
        return Path(tempfile.mkdtemp(prefix=_TEMP_PREFIX))

    output_dir = _require_nonblank(value, "--output-dir")
    return Path(output_dir).expanduser().resolve()


def _build_config(
    *,
    model: str,
    gateway_url: str,
    output_root: Path,
    max_debate_rounds: int,
    max_risk_discuss_rounds: int,
) -> dict[str, Any]:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config.update(
        {
            "llm_provider": "vscode",
            "deep_think_llm": model,
            "quick_think_llm": model,
            "backend_url": gateway_url,
            "results_dir": output_root / "results",
            "data_cache_dir": output_root / "cache",
            "memory_log_path": output_root / "memory" / "trading_memory.md",
            "max_debate_rounds": max_debate_rounds,
            "max_risk_discuss_rounds": max_risk_discuss_rounds,
            "checkpoint_enabled": False,
        }
    )
    return config


def _checked_fields(analysts: Sequence[str]) -> list[str]:
    return [
        *[_ANALYST_REPORT_FIELDS[analyst] for analyst in analysts],
        *_FIXED_FINAL_STATE_FIELDS,
    ]


def _validate_success_evidence(
    final_state: object,
    processed_decision: object,
    analysts: Sequence[str],
) -> tuple[str, dict[str, int]]:
    if not isinstance(final_state, Mapping):
        raise ValueError("propagate() final_state must be a mapping.")

    counts: dict[str, int] = {}
    for field_name in _checked_fields(analysts):
        if field_name not in final_state:
            raise ValueError(f"final_state['{field_name}'] is missing.")
        value = final_state[field_name]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"final_state['{field_name}'] must be a nonblank string.")
        counts[field_name] = len(value)

    if processed_decision is None:
        raise ValueError("processed decision from propagate() must be nonblank.")
    processed_text = str(processed_decision).strip()
    if not processed_text:
        raise ValueError("processed decision from propagate() must be nonblank.")

    return processed_text, counts


def _print_success(
    *,
    model: str,
    ticker: str,
    trade_date: str,
    analysts: Sequence[str],
    processed_decision: str,
    field_counts: Mapping[str, int],
    output_root: Path,
    token: str,
) -> None:
    print("TradingAgentsGraph construction and propagate() succeeded.")
    print(f"model: {_redact(model, token)}")
    print(f"ticker: {_redact(ticker, token)}")
    print(f"trade_date: {_redact(trade_date, token)}")
    print(f"analysts: {_redact(', '.join(analysts), token)}")
    print(f"processed_decision: {_redact(processed_decision, token)}")
    print("checked_final_state_field_char_counts:")
    for field_name, count in field_counts.items():
        print(f"  {field_name}: {count}")
    print(f"output_root: {_redact(output_root, token)}")


def main(argv: Sequence[str] | None = None) -> int:
    token = _nonblank(os.environ.get(_GATEWAY_TOKEN_ENV))
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except _InputError as exc:
        return _input_error(str(exc), token)

    gateway_url = _nonblank(os.environ.get(_GATEWAY_URL_ENV))

    if gateway_url is None:
        return _input_error(f"Missing required environment variable {_GATEWAY_URL_ENV}.")
    if token is None:
        return _input_error(f"Missing required environment variable {_GATEWAY_TOKEN_ENV}.")

    try:
        model = _require_nonblank(args.model, "--model")
        ticker = _require_nonblank(args.ticker, "--ticker")
        trade_date = _parse_trade_date(args.trade_date)
        analysts = _parse_analysts(args.analysts)
        output_root = _output_root(args.output_dir)
    except _InputError as exc:
        return _input_error(str(exc), token)

    try:
        output_root.mkdir(parents=True, exist_ok=True)
        config = _build_config(
            model=model,
            gateway_url=gateway_url,
            output_root=output_root,
            max_debate_rounds=args.max_debate_rounds,
            max_risk_discuss_rounds=args.max_risk_discuss_rounds,
        )
        graph = TradingAgentsGraph(selected_analysts=analysts, debug=False, config=config)
        final_state, processed_decision = graph.propagate(ticker, trade_date)
        processed_text, field_counts = _validate_success_evidence(
            final_state,
            processed_decision,
            analysts,
        )
        _print_success(
            model=model,
            ticker=ticker,
            trade_date=trade_date,
            analysts=analysts,
            processed_decision=processed_text,
            field_counts=field_counts,
            output_root=output_root,
            token=token,
        )
        return 0
    except Exception as exc:
        return _failure(exc, token)


if __name__ == "__main__":
    sys.exit(main())