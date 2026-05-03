"""Direct smoke for the TradingAgents VS Code Gateway provider boundary.

This smoke verifies that the TradingAgents ``vscode`` provider can construct
the package-local LangChain gateway model and, by default, make one direct
``llm.invoke(...)`` call through a running VS Code gateway.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from typing import Any

from tradingagents.llm_clients import create_llm_client


_GATEWAY_URL_ENV = "TRADINGAGENTS_VSCODE_GATEWAY_URL"
_GATEWAY_TOKEN_ENV = "TRADINGAGENTS_VSCODE_GATEWAY_TOKEN"
_DEFAULT_PROMPT = "Reply with one short sentence."
_REDACTION = "[REDACTED]"


def _nonblank(value: object) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    return text


def _redact(text: object, token: str | None) -> str:
    message = str(text)
    if token:
        message = message.replace(token, _REDACTION)
    return message


def _assistant_text(response: Any) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
            else:
                parts.append(str(item))
        return "".join(parts)

    return str(content)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        default=None,
        help="Opaque VS Code Gateway model ID selected from /v1/models.",
    )
    parser.add_argument(
        "--no-invoke",
        action="store_true",
        help="Construct the provider model without making a direct chat call.",
    )
    parser.add_argument(
        "--prompt",
        default=_DEFAULT_PROMPT,
        help="Prompt for the direct llm.invoke(...) call.",
    )
    return parser


def _input_error(message: str, token: str | None = None) -> int:
    print(f"Error: {_redact(message, token)}")
    return 2


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    url = _nonblank(os.environ.get(_GATEWAY_URL_ENV))
    token = _nonblank(os.environ.get(_GATEWAY_TOKEN_ENV))
    model = _nonblank(args.model)
    prompt = _nonblank(args.prompt)

    if url is None:
        return _input_error(f"Missing required environment variable {_GATEWAY_URL_ENV}.")
    if token is None:
        return _input_error(f"Missing required environment variable {_GATEWAY_TOKEN_ENV}.")
    if model is None:
        return _input_error("Missing required --model value.", token)
    if prompt is None:
        return _input_error("Missing required --prompt value.", token)

    try:
        client = create_llm_client(
            provider="vscode",
            model=model,
            base_url=url,
            token=token,
        )
        llm = client.get_llm()
        print(f"VS Code provider construction succeeded for model: {model}")

        if args.no_invoke:
            print("No invocation requested.")
            return 0

        response = llm.invoke(prompt)
        print("Assistant response:")
        print(_redact(_assistant_text(response), token))
        return 0
    except Exception as exc:
        print(f"Smoke FAILED: {_redact(exc, token)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())