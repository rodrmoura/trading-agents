# Proven Knowledge

## Current Priors

- Repository-local governance should use one canonical home per fact and thin wrappers for prompts and skills.
- Model ownership is role-based: GPT for reasoning/review, Codex for implementation, PhD Critic for read-only critique.
- Confirmed route labels are GPT 5.5 for reasoning, Codex 5.3 for coding, and Opus 4.7 for PhD Critic with Opus 4.6 and Sonnet 4.6 fallbacks.
- Critic work and inspections always use maximum reasoning.
- Codex work must be bounded by a ready `Coding-Agent Task Ledger`.
- Session resume should read current-truth files first and avoid full historical scans by default.
- Session wrap should validate and update handoff docs first, then stage, commit, and push only the user-approved scope to `origin`; it must never push to `upstream`.

## Stable Project Facts

- The repository contains a Python package configured in `pyproject.toml`.
- `pyproject.toml` owns runtime dependencies in `[project.dependencies]`; `requirements.txt` is the compatibility/test-install shim for installing the local package plus repo test runner.
- `pytest` is the discovered test command.
- `requirements.txt` and `uv.lock` are present; `uv.lock` is maintained as the project lockfile and should pass `uv lock --check` when dependency metadata changes.
- Workspace Python is configured to use the repo-local `.venv` through `.vscode/settings.json`; `.venv` is ignored by git.
- The repo-local `.venv` now runs Python 3.13.13 after a Windows Package Manager upgrade and in-place venv upgrade on 2026-05-01.
- On 2026-05-01, `python -m pytest -q` passed in `.venv` with `92 passed, 40 subtests passed` after the Python 3.13.13 upgrade.
- On 2026-05-01, `uv.lock` was refreshed to current `pyproject.toml` metadata for `tradingagents` 0.2.4 and passed `uv lock --check`.
- No CI workflow files were found under `.github/workflows` during bootstrap.
- Existing project-specific docs and planning files remain useful, but generic governance now belongs in `docs/WORKFLOW_HELPERS.md` and the repo-state docs.
- `packages/vscode-llm-gateway` is a TypeScript VS Code extension package that implements a local native gateway in the extension host.
- The gateway server uses Node built-in `http`, binds only to `127.0.0.1`, and uses an in-memory bearer token that is never persisted.
- Native Phase 1 endpoints are implemented at `/health`, `/shutdown`, `/v1/models`, `/v1/chat/completions`, and `/v1/chat/completions/stream`.
- Request validation for chat endpoints is strict native validation with no OpenAI compatibility mode.
- Streaming uses SSE `chunk`, `done`, and `error` events and does not emit an OpenAI `[DONE]` sentinel.
- After P1.5 plus a one-line export follow-up, package verification passed: `npm run check`, `npm run compile`, and `npm test --if-present` with `42` passing tests and `0` failures.
- On 2026-05-01, live G1 VS Code gateway smoke passed through the Extension Development Host command-palette start/token-copy path using `gpt-4o-mini`: `/health`, `/v1/models`, non-stream chat, SSE stream, no `[DONE]`, and authenticated shutdown all worked.
- `packages/llm-gateway-python` owns the generic Python SDK package. Its distribution name is `llm-gateway`, import package is `llm_gateway`, and P2.1 version is `0.0.1`.
- On 2026-05-01, P2.1 SDK skeleton verification passed with editable install, package-local pytest (`7 passed`), import smoke, diff hygiene, and PhD Critic implementation approval.
- On 2026-05-01, P2.2 added blocking standard-library HTTP behavior for SDK `health()`, `list_models()`, and `chat()`.
- On 2026-05-01, P2.3 added synchronous native SSE streaming behavior for SDK `stream_chat()` with method-call token validation, lazy HTTP open, native `chunk`/`done`/`error` event parsing, and deterministic response close on terminal events, parser failures, transport failures, and explicit iterator close.
- On 2026-05-01, P2.4 added the optional LangChain Core adapter at `llm_gateway.langchain_adapter.GatewayChatModel`; the root `llm_gateway` import remains lightweight and does not import LangChain Core.
- The LangChain adapter supports `invoke()` and `stream()` through the native SDK client, maps system/user/human/assistant message roles to native `ChatMessage` values, normalizes text blocks, redacts configured tokens from stream errors, supports non-stream `bind_tools()` roundtrip through the native gateway tool contract, and explicitly defers structured output with `NotImplementedError`.
- The Python SDK sends bearer tokens only for protected endpoints, redacts configured tokens from repr/string and SDK exception surfaces, and has no OpenAI facade concepts or TradingAgents/CLI imports.
- The Python SDK maps native gateway error envelopes to `GatewayRequestError`, malformed native JSON/SSE payloads to `GatewayResponseError`, and local HTTP failures to `GatewayTransportError`.
- The native gateway tool-call contract is non-stream only: `/v1/chat/completions` accepts native `tools`, assistant `toolCalls`, and `role: "tool"` messages, while `/v1/chat/completions/stream` rejects tool-enabled requests before model invocation.
- TradingAgents provider `vscode` is now a thin optional boundary: `tradingagents.llm_clients.vscode_client.VSCodeClient` resolves `TRADINGAGENTS_VSCODE_GATEWAY_URL` and `TRADINGAGENTS_VSCODE_GATEWAY_TOKEN`, lazily imports the package-local SDK adapter, returns `GatewayChatModel`, and accepts opaque VS Code model IDs.
- The interactive CLI now exposes `VS Code Gateway` and prompts for opaque model IDs; it does not discover models dynamically in P3.2.
- `scripts/smoke_vscode_provider.py` is a direct TradingAgents `vscode` provider smoke: it validates `TRADINGAGENTS_VSCODE_GATEWAY_URL`, `TRADINGAGENTS_VSCODE_GATEWAY_TOKEN`, model, and prompt values; supports `--no-invoke`; can call `GatewayChatModel.invoke()` directly; and redacts the configured token from failure and assistant-output text.
- `docs/runbooks/tradingagents-vscode-provider.md` owns the operator steps for the direct provider smoke and the P3.3c full-graph harness; it explicitly does not prove a full analyst graph run until the harness succeeds against a real gateway/model.
- `scripts/smoke_vscode_tradingagents_graph.py` is the repeatable P3.3c full-graph harness: it validates the gateway environment, opaque model ID, ticker, ISO trade date, analysts, output root, and round counts; builds an isolated `vscode` graph config; runs `TradingAgentsGraph(...).propagate(...)`; requires selected analyst reports plus downstream decision fields to be nonblank; and prints only token-redacted concise evidence and field character counts.
- On 2026-05-02, P3.3c live full-graph smoke passed through a running VS Code gateway using model `claude-opus-4.6-1m`: direct provider construction and direct invoke passed, then `scripts/smoke_vscode_tradingagents_graph.py --model claude-opus-4.6-1m` completed for `NVDA` on `2024-05-10` with market analyst selected, processed decision `Hold`, and nonblank `market_report`, `investment_plan`, `trader_investment_plan`, and `final_trade_decision` evidence. Research Manager, Trader, and Portfolio Manager used the documented free-text fallback because structured output remains unsupported.

## Reopen Rules

- Reopen model-route decisions if VS Code cannot resolve the confirmed custom-agent model labels.
- Reopen validation commands when lint, typecheck, build, or CI commands are added.
- Reopen dependency packaging facts when runtime dependencies, test-runner requirements, or lockfile policy changes.
- Reopen Python environment facts if the interpreter path/version changes, dependencies are removed, or tests fail again because packages are missing.
- Reopen lifecycle command behavior if prompt/skill metadata semantics change.
- Reopen document ownership if duplicate current-truth stores appear.
- Reopen gateway stability facts if future live VS Code model smoke fails or if stable VS Code LM API behavior differs from the tested assumptions.
- Reopen SDK facts if provider integration changes adapter behavior, package metadata, public import names, token redaction behavior, streaming behavior, structured-output/tool-calling support, native tool contract shape, or the no-OpenAI-facade boundary.
- Reopen `vscode` provider facts if environment variable names, optional dependency policy, CLI selection behavior, factory dispatch, direct smoke behavior, graph smoke harness behavior, live proof behavior, runbook setup, structured-output fallback behavior, or `bind_tools()` support changes.

## Superseded Or Contested Knowledge

- Prior TODO placeholders for model routes are superseded by the confirmed route labels recorded here.
- Prior lifecycle docs that require reading broad historical changelogs on resume are superseded by `ACTIVE_STATE` and `PROVEN_KNOWLEDGE` first.
