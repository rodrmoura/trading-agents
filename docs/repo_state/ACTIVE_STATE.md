# Active State

## Current Focus

- G0 governance/environment/dependency planning scope is validation-complete and approved for GitHub commit/push.
- Repository-local AI-agent governance is installed and passed required self-audit with non-blocking follow-ups.
- Python environment setup is repaired, upgraded, and validated; `requirements.txt` is a documented compatibility/test-install shim and `uv.lock` is refreshed to current `pyproject.toml` metadata.
- VS Code gateway package implementation packets P1.1 through P1.5 in `packages/vscode-llm-gateway` are implemented and review-approved this session.
- G1 live VS Code extension smoke with a real VS Code model passed and is accepted.
- Phase 2 P2.1 through P2.4 are implemented, verified, and review-approved; P3.1 TradingAgents provider integration audit is complete, and P3.2 thin `vscode` provider boundary is the next planned handoff.

## Current Mode

- P3.1 provider integration audit complete; P3.2 provider-construction handoff preparation.
- Active next implementation target: P3.2 thin TradingAgents `vscode` provider boundary.
- Local workspace path cleanup is complete: the repository has been reopened at `C:\VSCode\Tauric\TradingAgents`, hardcoded project text references now use the no-space path, and the repo-local `.venv` was rebuilt at the new path.
- G0 commit/push approval has been received; only the approved scope should be staged, committed, and pushed to `origin`.

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
- P2.4 Python SDK LangChain-compatible adapter is complete in `packages/llm-gateway-python`: optional `langchain` extra, lightweight root import boundary, `llm_gateway.langchain_adapter.GatewayChatModel`, LangChain `invoke()` and `stream()` paths through native `GatewayClient.chat()` and `GatewayClient.stream_chat()`, prompt-template/message-role mapping, text block normalization, token-safe stream errors, and explicit `NotImplementedError` deferrals for structured output and native tool calling.
- P2.4 verification passed: editable install with `[langchain]`, package-local pytest (`73 passed`), import smoke (`0.0.1` and `GatewayChatModel`), `git diff --check -- packages/llm-gateway-python`, forbidden boundary/facade-term scan after generated artifact cleanup, artifact scan clean, diagnostics clean, and PhD Critic implementation approval with no required patch. Validation is targeted/mocked adapter coverage, not a live gateway or TradingAgents provider run.
- P3.1 TradingAgents provider integration audit is complete in `docs/reference/tradingagents-vscode-provider-audit.md`: the next patch should add a lazy optional `vscode` client/factory path, CLI custom model-ID selection, and token/base-url configuration through `TRADINGAGENTS_VSCODE_GATEWAY_URL` and `TRADINGAGENTS_VSCODE_GATEWAY_TOKEN`; P3.2 may defer analyst smoke, but must not claim a full analyst run works until tool calling or a valid post-analyst bypass exists.

## Known Blockers

- G0 approval has been received; stage, commit, and push only the approved G0 scope to `origin`.
- A full `vscode` provider TradingAgents run through analyst agents is blocked until native gateway tool calling or a TradingAgents-specific analyst fallback exists.

## Next Actions

- Prepare the P3.2 thin `vscode` provider boundary ledger from `docs/reference/tradingagents-vscode-provider-audit.md`; keep it provider-construction focused and do not claim full analyst smoke support until tool calling is addressed.
- Complete approved G0 commit/push, then prepare the P3.2 thin `vscode` provider boundary ledger from `docs/reference/tradingagents-vscode-provider-audit.md`.

## Resume Pointers

- Start with `docs/WORKFLOW_HELPERS.md` for canonical governance.
- Read `docs/repo_state/PROVEN_KNOWLEDGE.md` for stable current priors.
- Read `docs/ROADMAP.md` only if priority is unclear.
