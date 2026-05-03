# TradingAgents VS Code Provider Audit

P3.1 audit result for adding a thin `vscode` LLM provider to TradingAgents.

Current truth on 2026-05-02: the VS Code gateway and Python SDK/LangChain adapter are implemented and targeted tests pass. The gateway API draft remains useful for contract semantics, but its early status sentence is superseded by `docs/repo_state/ACTIVE_STATE.md`.

## Goal

Enable TradingAgents to select a `vscode` provider that routes LLM calls through the generic Python SDK package at `packages/llm-gateway-python`, without changing agent graph logic in the first provider patch.

P3.1 is audit-only. Do not wire the provider in this packet.

## Current Integration Points

- `tradingagents/llm_clients/factory.py` owns provider dispatch through `create_llm_client(provider, model, base_url, **kwargs)`. Add a `provider_lower == "vscode"` branch here in P3.2.
- `tradingagents/llm_clients/base_client.py` defines the client contract: subclasses implement `get_llm()` and `validate_model()` and may call `warn_if_unknown_model()`.
- `tradingagents/graph/trading_graph.py` creates both deep and quick LLM clients from `config["llm_provider"]`, `config["deep_think_llm"]`, `config["quick_think_llm"]`, and `config.get("backend_url")`, forwarding provider-specific kwargs from `_get_provider_kwargs()`.
- `cli/utils.py` owns interactive provider and model selection. `select_llm_provider()` must expose `vscode`, and `_select_model()` should prompt for an opaque VS Code model ID rather than using the static model catalog.
- `cli/main.py` copies CLI selections into graph config, so a `vscode` provider can flow through the existing `llm_provider`, `backend_url`, `quick_think_llm`, and `deep_think_llm` keys.
- `tradingagents/llm_clients/model_catalog.py` should not receive static VS Code model IDs. VS Code model identifiers are runtime-discovered and can change over time.
- `tradingagents/llm_clients/validators.py` already accepts providers absent from `VALID_MODELS`, so leaving `vscode` out of `MODEL_OPTIONS` allows arbitrary opaque model IDs without warnings.

## Recommended P3.2 Patch

Add one TradingAgents-specific client module:

- `tradingagents/llm_clients/vscode_client.py`

Recommended behavior:

1. Implement `VSCodeClient(BaseLLMClient)`.
2. Keep `llm_gateway` imports lazy inside `get_llm()` so clean environments fail with a clear setup message instead of failing during test collection.
3. Resolve base URL from `base_url`, then `TRADINGAGENTS_VSCODE_GATEWAY_URL`, then a safe default only if the implementation has an explicit reason to choose one. Prefer requiring a URL because gateway ports are ephemeral.
4. Resolve token from `kwargs.get("token")`, then `TRADINGAGENTS_VSCODE_GATEWAY_TOKEN`. Never print or log the token.
5. Build `GatewayClientConfig(base_url=<url>, token=<token>)`, `GatewayClient`, and `GatewayChatModel(client=<client>, model=<model>)`.
6. Return the `GatewayChatModel` from `get_llm()`.
7. Return `True` from `validate_model()` because VS Code model IDs are opaque runtime values and the gateway validates them against `/v1/models`.

Update dispatch:

- Add a `vscode` branch in `tradingagents/llm_clients/factory.py` that imports `VSCodeClient` lazily and passes `model`, `base_url`, and `**kwargs`.

Update CLI selection:

- Add `("VS Code Gateway", "vscode", None)` to `select_llm_provider()`.
- Add an `_select_model()` branch for `provider.lower() == "vscode"` that prompts for a VS Code gateway model ID, with examples pointing users to the gateway `/v1/models` command/runbook.
- Do not add `vscode` to `MODEL_OPTIONS` unless a future version implements dynamic model discovery inside the CLI.

Do not change graph setup or agent factories in P3.2 unless tests prove there is no narrower path.

## Configuration Contract

Use these names for P3.2/P3.3 unless a later review chooses different names:

- `TRADINGAGENTS_VSCODE_GATEWAY_URL`: gateway base URL such as `http://127.0.0.1:<port>`.
- `TRADINGAGENTS_VSCODE_GATEWAY_TOKEN`: bearer token copied from the VS Code gateway command.

The CLI/config flow may continue to use existing keys:

- `config["llm_provider"] = "vscode"`
- `config["backend_url"]` as the explicit gateway base URL when supplied.
- `config["quick_think_llm"]` and `config["deep_think_llm"]` as opaque VS Code model IDs.

P3.2 should avoid editing `pyproject.toml`, `requirements.txt`, and `uv.lock`. The SDK is still package-local and optional for TradingAgents users. Keep the dependency optional with a clear runtime setup error, then document the editable install in P3.3 runbook work. Reopen dependency metadata only if the provider becomes a default-supported install path.

## Compatibility Risks

### Tool Calling

Analyst agents call `llm.bind_tools(tools)`:

- `tradingagents/agents/analysts/market_analyst.py`
- `tradingagents/agents/analysts/social_media_analyst.py`
- `tradingagents/agents/analysts/news_analyst.py`
- `tradingagents/agents/analysts/fundamentals_analyst.py`

Update after P3.3b: the SDK adapter now supports non-stream native `bind_tools(...)` roundtrip through the VS Code gateway and LangGraph can still execute Python tools locally. This audit section is retained as historical rationale for why P3.3b was needed.

A live full one-ticker run through analysts is still unproven until a later smoke packet records it against a running VS Code gateway/model. If that live path fails, reopen one of these strategies:

- additional native gateway tool-calling support and SDK adapter support,
- a TradingAgents-specific analyst fallback that runs tools outside `bind_tools`, or
- a smoke path that starts after analyst reports already exist.

Do not pretend empty tool results are supported.

### Structured Output

Trader, Research Manager, and Portfolio Manager use `with_structured_output(...)` through `tradingagents/agents/utils/structured.py`. The current gateway adapter raises `NotImplementedError`, and the structured helper catches that at agent creation and falls back to free-text generation. This is degraded behavior, not an immediate provider construction blocker.

P3.2 tests should confirm free-text fallback still works for `vscode`-backed LLM objects. Later G3 work should decide whether free text is acceptable for the first smoke or whether native structured output must be added first.

### Stop Sequences And Generation Options

`GatewayChatModel` rejects non-empty stop sequences and unsupported generation kwargs. The audited TradingAgents call sites primarily use `invoke(...)`, `bind_tools(...)`, and `with_structured_output(...)`; no required stop-sequence flow was found in this pass.

## Test Plan For P3.2

Add focused unit tests before any live smoke:

- Factory creates a `VSCodeClient` for `provider="vscode"` without importing SDK modules at factory import time.
- `VSCodeClient.get_llm()` returns `GatewayChatModel` when URL and token are configured.
- Missing SDK import raises a clear install/setup error.
- Missing gateway URL or token raises a clear configuration error without leaking token-like values.
- `validate_model()` accepts arbitrary opaque VS Code model IDs.
- CLI provider selection includes `vscode` and model selection prompts for a custom ID.
- Existing provider tests continue to pass.
- Structured fallback tests still pass with a model whose `with_structured_output` raises `NotImplementedError`.

Suggested existing tests to update:

- `tests/test_model_validation.py`
- provider/factory-focused tests, either existing or new under `tests/`
- `tests/test_structured_agents.py` if a `vscode`-specific fallback regression is added

## P3.3 Follow-Up

P3.3 should make a repeatable gateway-backed run easier after provider construction exists:

- Add a runbook that starts the VS Code gateway, copies the token, exports `TRADINGAGENTS_VSCODE_GATEWAY_URL` and `TRADINGAGENTS_VSCODE_GATEWAY_TOKEN`, lists models, and runs a minimal TradingAgents command or script.
- Add a smoke script only after deciding how to handle analyst tool calls.
- Keep token values out of logs, docs, saved reports, and terminal examples.

## Boundaries

- Keep generic SDK behavior in `packages/llm-gateway-python`.
- Keep TradingAgents-specific provider wiring in `tradingagents/llm_clients` and CLI/runbook code.
- Do not edit agent graph or analyst/trader/manager internals for P3.2 unless a ready follow-up ledger explicitly authorizes it.
- Do not commit, stage, or change G0 scope as part of provider work.
