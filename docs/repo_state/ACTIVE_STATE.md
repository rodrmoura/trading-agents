# Active State

## Current Focus

- G0 governance/environment/dependency planning scope is validation-complete and approved for GitHub commit/push.
- Repository-local AI-agent governance is installed and passed required self-audit with non-blocking follow-ups.
- Python environment setup is repaired, upgraded, and validated; `requirements.txt` is a documented compatibility/test-install shim and `uv.lock` is refreshed to current `pyproject.toml` metadata.
- VS Code gateway package implementation packets P1.1 through P1.5 in `packages/vscode-llm-gateway` are implemented and review-approved this session.
- G1 live VS Code extension smoke with a real VS Code model passed and is accepted.
- Phase 2 P2.1 through P2.4 are implemented, verified, and review-approved; P3.1 TradingAgents provider integration audit, P3.2 thin `vscode` provider boundary, P3.3a direct provider smoke/runbook slice, P3.3b mocked non-stream native tool-call roundtrip, P3.3c full-graph smoke harness readiness, P3.3c live full-graph smoke proof, and P3.4 structured-output adapter compatibility are complete.

## Current Mode

- P3.4 structured-output adapter compatibility is implemented, locally validated, and implementation-review approved for the `vscode` provider path.
- Local workspace path cleanup is complete: the repository has been reopened at `C:\VSCode\Tauric\TradingAgents`, hardcoded project text references now use the no-space path, and the repo-local `.venv` was rebuilt at the new path.
- G0 has been committed and pushed to `origin/main` as `10a4a5d`.

## Active Decisions

- GPT owns reasoning, planning, architecture, documentation governance, task shaping, and review.
- Codex owns code-writing implementation only from a ready `Coding-Agent Task Ledger`.
- PhD Critic is read-only and cannot edit files, run terminal commands, persist state, or directly instruct Codex.
- Reasoning Engineer route is GPT 5.5 with high or xhigh reasoning depending on complexity.
- Codex Coding Engineer route is Codex 5.3 with high or xhigh reasoning depending on complexity.
- PhD Critic route is Opus 4.7, with Opus 4.6 and Sonnet 4.6 fallbacks, always using maximum reasoning for critic work and inspections.

## Evidence Snapshot

- `pyproject.toml` defines a Python package using `setuptools` and `pytest` configuration.
- `requirements.txt` installs the local package plus `pytest>=8.3` as a compatibility/test-install shim; `uv.lock` is maintained as the project lockfile and currently passes `uv lock --check`.
- `.github/skills/*/SKILL.md`, `.github/agents/*.agent.md`, `.github/prompts/*.prompt.md`, and `.github/instructions/*.instructions.md` are supported customization surfaces in this environment.
- No `.github/workflows` CI files were found during bootstrap.
- Static validation passed for customization frontmatter, stale references, ASCII, trailing whitespace/tabs, generic-governance domain neutrality, and `git diff --check`.
- Required governance self-audit result: Approved with non-blocking follow-ups; critical issues none; required fixes none.
- Python environment repaired and upgraded on 2026-05-01: `.vscode/settings.json` selects `${workspaceFolder}/.venv/Scripts/python.exe`, `.venv` is ignored by git, and local package dependencies plus `pytest` are installed in `.venv`.
- Local workspace path cleanup completed on 2026-05-02: old space-containing workspace path references were removed from project text and regenerated local environment files, `.vscode/settings.json` remains workspace-relative, the repo-local `.venv` was rebuilt at `C:\VSCode\Tauric\TradingAgents\.venv`, project/test dependencies plus the SDK LangChain extra were reinstalled, the SDK import smoke resolved from the new workspace path, and root `pytest -q` passed with `92 passed, 40 subtests passed in 4.21s`.
- Python 3.13 was upgraded from 3.13.12 to 3.13.13 with Windows Package Manager, and `.venv` was upgraded in place with `python -m venv --upgrade .venv`.
- Using the repo-local `.venv`, `python -m pytest -q` passed after the upgrade: `92 passed, 40 subtests passed in 5.07s`.
- After the `requirements.txt` shim update, package install specs for the local project plus `pytest>=8.3` succeeded and `pytest -q` passed again: `92 passed, 40 subtests passed in 3.41s`.
- `uv lock` refreshed `uv.lock` to `tradingagents` 0.2.4 metadata; `uv lock --check` passed and `pytest -q` passed: `92 passed, 40 subtests passed in 2.69s`.
- `docs/planning/codex-task-packets.md` now contains a phase-by-phase Codex execution queue plus P0.3, P0.4, and P6.2-P6.4 packet details.
- G0-style validation passed after planning updates: `git diff --check`, ASCII scan, `uv lock --check`, diagnostics, and `pytest -q` with `92 passed, 40 subtests passed in 2.72s`.
- Final PhD Critic review of the immediate-plan result approved final reporting, with no critical issues and no required follow-up patch.
- Latest state-sync scope found the dirty worktree contains intended governance/customization docs, `.vscode/settings.json`, `requirements.txt`, and `uv.lock` changes; generated `.venv`, caches, build output, egg-info, and pycache entries remain ignored.
- Phase 1 planning now locks the native VS Code gateway contract: TypeScript extension package, Node built-in `http`, `127.0.0.1`, memory-only bearer token, explicit copy-token command, strict native JSON validation, SSE streaming, and no OpenAI facade/tool-calling/structured-output scope in Phase 1.
- P1.1 through P1.5 package implementation for `packages/vscode-llm-gateway` is complete and reviewed.
- P1.5 Codex implementation review using PhD Critic fallback Opus 4.6 returned `approved_with_nonblocking_notes`, with critical issues none and no required patch.
- One-line post-P1.5 follow-up exported `GatewayStartedChat` from `packages/vscode-llm-gateway/src/index.ts`.
- Independent verification after P1.5 and the export follow-up passed in `packages/vscode-llm-gateway`: `npm run check`, `npm run compile`, `npm test --if-present` (`42` tests passed, `0` failed), and `git diff --check -- packages/vscode-llm-gateway` (no output).
- Autonomous compiled-gateway HTTP smoke passed with a fake in-process model service: public `/health`, authenticated `/v1/models`, non-stream chat, SSE stream, no `[DONE]`, and stop all worked. This is useful endpoint evidence but does not satisfy G1 live VS Code model smoke.
- Live G1 VS Code extension smoke passed on 2026-05-01 using the command-palette start/token-copy path, `127.0.0.1:56668`, `gpt-4o-mini`, public `/health`, authenticated `/v1/models`, non-stream chat, SSE `chunk`/`done` streaming with no `[DONE]`, and authenticated `/shutdown`.
- G1 gate is accepted for proceeding to Phase 2.
- P2.1 Python SDK skeleton is complete in `packages/llm-gateway-python`: package-local setuptools metadata, import package `llm_gateway`, version `0.0.1`, shallow native gateway types/errors/client placeholders, redacting config repr, and package-local tests.
- P2.1 verification passed: editable install, package-local pytest (`7 passed`), import smoke (`0.0.1`), `git diff --check -- packages/llm-gateway-python`, forbidden import/OpenAI-concept grep, generated artifact cleanup, and PhD Critic implementation approval with no required patch.
- Final session-wrap validation after P2.1 passed: full `git diff --check`, VS Code gateway package check/compile/tests (`42` passed), SDK tests (`7` passed), SDK import smoke (`0.0.1`), `uv lock --check`, and root pytest (`92 passed, 40 subtests passed`).
- P2.2 Python SDK client/errors are complete in `packages/llm-gateway-python`: blocking standard-library HTTP client for `/health`, `/v1/models`, and `/v1/chat/completions`; bearer auth only for protected endpoints; camelCase/snake_case native mapping; typed native request, response-shape, and transport errors; `stream_chat()` still deferred to P2.3.
- P2.2 verification passed: editable install, package-local pytest (`42 passed`), import smoke (`0.0.1`), `git diff --check -- packages/llm-gateway-python`, forbidden import/OpenAI-concept grep after generated artifact cleanup, and PhD Critic implementation approval with no required patch.
- P2.3 Python SDK streaming client is complete in `packages/llm-gateway-python`: `GatewayClient.stream_chat()` validates bearer token at method call, opens HTTP lazily on iteration, sends native JSON to `/v1/chat/completions/stream`, parses native SSE `chunk`/`done`/`error` events into stream dataclasses, maps pre-stream native errors, redacts tokens, and closes responses on terminal events, parser errors, transport errors, and explicit iterator close.
- P2.3 verification passed: editable install, package-local pytest (`57 passed`), import smoke (`0.0.1`), `git diff --check -- packages/llm-gateway-python`, forbidden implementation-term grep after generated artifact cleanup, artifact scan clean, diagnostics clean, and PhD Critic implementation approval with no required patch. Validation is targeted/mocked SDK coverage, not a live SDK stream smoke.
- P2.4 Python SDK LangChain-compatible adapter is complete in `packages/llm-gateway-python`: optional `langchain` extra, lightweight root import boundary, `llm_gateway.langchain_adapter.GatewayChatModel`, LangChain `invoke()` and `stream()` paths through native `GatewayClient.chat()` and `GatewayClient.stream_chat()`, prompt-template/message-role mapping, text block normalization, token-safe stream errors, and explicit `NotImplementedError` deferrals at that time for structured output and native tool calling.
- P2.4 verification passed: editable install with `[langchain]`, package-local pytest (`73 passed`), import smoke (`0.0.1` and `GatewayChatModel`), `git diff --check -- packages/llm-gateway-python`, forbidden boundary/facade-term scan after generated artifact cleanup, artifact scan clean, diagnostics clean, and PhD Critic implementation approval with no required patch. Validation is targeted/mocked adapter coverage, not a live gateway or TradingAgents provider run.
- P3.1 TradingAgents provider integration audit is complete in `docs/reference/tradingagents-vscode-provider-audit.md`: the next patch should add a lazy optional `vscode` client/factory path, CLI custom model-ID selection, and token/base-url configuration through `TRADINGAGENTS_VSCODE_GATEWAY_URL` and `TRADINGAGENTS_VSCODE_GATEWAY_TOKEN`; P3.2 may defer analyst smoke, but must not claim a full analyst run works until tool calling or a valid post-analyst bypass exists.
- P3.2 TradingAgents `vscode` provider boundary is complete: `VSCodeClient` resolves gateway URL/token from constructor or environment, lazily imports the optional SDK/LangChain adapter, factory dispatch accepts provider `vscode`, CLI provider/model selection can choose opaque VS Code model IDs, and validators accept opaque `vscode` model names.
- P3.2 verification passed: targeted provider/model tests (`12 passed, 37 subtests passed`), structured-agent fallback tests (`11 passed`), full root pytest (`101 passed, 40 subtests passed`), `git diff --check`, and PhD Critic Codex implementation review approved with no required patch.
- P3.3a TradingAgents VS Code provider smoke is complete: `scripts/smoke_vscode_provider.py` validates gateway env/model/prompt input, constructs provider `vscode`, supports construction-only and direct `llm.invoke(...)` modes, and redacts the configured token from failures and assistant output. The operator runbook lives at `docs/runbooks/tradingagents-vscode-provider.md` and remains explicit that full analyst graph execution is still blocked.
- P3.3a verification passed: smoke-script tests (`14 passed`), combined provider/model tests (`26 passed, 37 subtests passed`), full root pytest (`115 passed, 40 subtests passed`), `git diff --check`, diagnostics on changed files, and PhD Critic implementation review approved with no blocking findings. No live operator gateway smoke was run for P3.3a in this session.
- P3.3b native non-stream tool-call roundtrip is implemented and review-approved: the VS Code gateway accepts native `tools`, assistant `toolCalls`, and `role: "tool"` messages for `/v1/chat/completions`; rejects OpenAI-shaped tool fields; keeps `/v1/chat/completions/stream` text-only; the Python SDK serializes/parses the native tool contract; and `GatewayChatModel.bind_tools()` returns a bound clone that maps LangChain tools, `AIMessage.tool_calls`, and `ToolMessage` values to the native gateway contract.
- P3.3b verification passed: VS Code gateway `npm run check`, `npm run compile`, and `npm test --if-present` (`48` tests); SDK package tests (`89 passed`); targeted TradingAgents provider/structured tests (`37 passed, 37 subtests passed`); full root pytest (`115 passed, 40 subtests passed`); diagnostics on scoped files; and PhD Critic implementation review approved with no blocking findings. `git diff --check` reported only Git's line-ending warning for `docs/reference/gateway-api-draft.md`, not whitespace errors. No live VS Code model tool-call run or full one-ticker TradingAgents smoke was run for P3.3b.
- P3.3c harness readiness is implemented and review-approved: `scripts/smoke_vscode_tradingagents_graph.py` validates gateway env, model, ticker, ISO trade date, analyst list, output root, and round counts; builds an isolated `vscode` `TradingAgentsGraph` config; runs `propagate(ticker, trade_date)`; checks selected analyst reports plus `investment_plan`, `trader_investment_plan`, `final_trade_decision`, and processed decision; and prints token-redacted concise evidence with field character counts instead of report bodies.
- P3.3c harness readiness verification passed: focused provider/harness tests (`50 passed`), full root pytest (`142 passed, 40 subtests passed`), VS Code gateway package `npm run check`, `npm run compile`, and `npm test --if-present` (`48` tests), SDK package tests (`89 passed`), diagnostics on touched files, scoped `git diff --check`, and PhD Critic implementation review approved with no blocking findings. Full `git diff --check` still reports only Git's existing LF-to-CRLF warning for `docs/reference/gateway-api-draft.md`.
- P3.3c live full-graph smoke passed on 2026-05-02 through the Extension Development Host gateway at `127.0.0.1:54593` with `56` listed models and selected model `claude-opus-4.6-1m`. Direct provider construction and direct `llm.invoke(...)` smoke passed. Full graph command `scripts/smoke_vscode_tradingagents_graph.py --model claude-opus-4.6-1m` passed for `NVDA` on `2024-05-10` with analyst `market`, processed decision `Hold`, field counts `market_report=4401`, `investment_plan=1497`, `trader_investment_plan=480`, `final_trade_decision=1117`, and output root `C:\Users\Rodrigo\AppData\Local\Temp\tradingagents-vscode-graph-smoke-xfw285h3`. Research Manager, Trader, and Portfolio Manager used the documented free-text fallback because `with_structured_output(...)` was unsupported by `llm_gateway` at P3.3c time.
- P3.4 structured-output adapter compatibility is implemented and review-approved in `packages/llm-gateway-python`: `GatewayChatModel.with_structured_output(...)` now delegates to LangChain Core's non-streaming tool-call parser path over the native `tools`/`toolCalls` bridge; Pydantic schemas parse to Pydantic instances, dict/JSON schemas parse to dicts, `include_raw=True` returns LangChain's `raw`/`parsed`/`parsing_error` shape, and captured fake gateway requests contain native `tools` only. Explicit unsupported generation kwargs, stop sequences, tool-enabled streaming, named/required/explicit-any `bind_tools()` tool choice, and arbitrary unsupported `bind_tools()` kwargs remain rejected. Local validation passed: package tests `94 passed`; targeted TradingAgents provider/structured tests `47 passed`; PhD Critic implementation review approved with no blocking findings.

## Known Blockers

- No current blocker for non-streaming adapter-level structured output. The gateway still does not enforce tool choice or schema adherence, and a live post-P3.4 full-graph smoke has not been rerun.

## Next Actions

- Decide whether to run a live post-P3.4 full-graph smoke to prove Research Manager, Trader, and Portfolio Manager use the structured parser path against a real VS Code model.
- If continuing live validation, prefer a faster model than `claude-opus-4.6-1m` for routine smoke loops; the successful P3.3c run proves the path but was slow near final manager/trader/portfolio phases.

## Resume Pointers

- Start with `docs/WORKFLOW_HELPERS.md` for canonical governance.
- Read `docs/repo_state/PROVEN_KNOWLEDGE.md` for stable current priors.
- Read `docs/ROADMAP.md` only if priority is unclear.
