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
- The LangChain adapter supports `invoke()` and `stream()` through the native SDK client, maps system/user/human/assistant message roles to native `ChatMessage` values, normalizes text blocks, redacts configured tokens from stream errors, and explicitly defers structured output and native tool calling with `NotImplementedError`.
- The Python SDK sends bearer tokens only for protected endpoints, redacts configured tokens from repr/string and SDK exception surfaces, and has no OpenAI facade concepts or TradingAgents/CLI imports.
- The Python SDK maps native gateway error envelopes to `GatewayRequestError`, malformed native JSON/SSE payloads to `GatewayResponseError`, and local HTTP failures to `GatewayTransportError`.

## Reopen Rules

- Reopen model-route decisions if VS Code cannot resolve the confirmed custom-agent model labels.
- Reopen validation commands when lint, typecheck, build, or CI commands are added.
- Reopen dependency packaging facts when runtime dependencies, test-runner requirements, or lockfile policy changes.
- Reopen Python environment facts if the interpreter path/version changes, dependencies are removed, or tests fail again because packages are missing.
- Reopen lifecycle command behavior if prompt/skill metadata semantics change.
- Reopen document ownership if duplicate current-truth stores appear.
- Reopen gateway stability facts if future live VS Code model smoke fails or if stable VS Code LM API behavior differs from the tested assumptions.
- Reopen SDK facts if provider integration changes adapter behavior, package metadata, public import names, token redaction behavior, streaming behavior, structured-output/tool-calling support, or the no-OpenAI-facade boundary.

## Superseded Or Contested Knowledge

- Prior TODO placeholders for model routes are superseded by the confirmed route labels recorded here.
- Prior lifecycle docs that require reading broad historical changelogs on resume are superseded by `ACTIVE_STATE` and `PROVEN_KNOWLEDGE` first.
