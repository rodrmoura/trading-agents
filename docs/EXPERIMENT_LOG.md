# Experiment / Validation Log

This file owns measured experiment, validation, benchmark, and readiness evidence. Prefer pointers to commands, commits, files, artifacts, and summarized outcomes over pasted raw output.

## Entries

### 2026-05-01: P2.4 Python Gateway SDK LangChain Adapter Verification

- Date: 2026-05-01
- Question: Did the generic Python SDK gain the smallest LangChain-compatible adapter surface needed before TradingAgents provider integration?
- Baseline: P2.3 provided the native blocking and streaming SDK client, but there was no LangChain Core adapter surface for prompt-template composition, `invoke()`, `stream()`, or structured/tool fallback behavior.
- Change: Added optional LangChain Core extra metadata, `llm_gateway.langchain_adapter.GatewayChatModel`, native request conversion for system/user/human/assistant messages, prompt-template and dict-message compatibility, text block normalization, token-safe stream error handling, and explicit `NotImplementedError` deferrals for structured output and native tool calling.
- Result: Editable install with `[langchain]` passed; package-local pytest passed with `73 passed`; import smoke printed `0.0.1` and `GatewayChatModel`; `git diff --check -- packages/llm-gateway-python` passed; forbidden boundary/facade-term grep was clean after removing generated editable-install artifacts; generated artifact scan returned clean; VS Code diagnostics for changed SDK files were clean.
- Review: PhD Critic Codex implementation review approved P2.4 with no critical issues and no required follow-up patch.
- Verdict: Pass at `V2 targeted` plus `V0 critic approval`; P2.4 is accepted as complete. No live gateway adapter call or TradingAgents provider run was performed because those belong to later packets.
- Artifacts: `packages/llm-gateway-python/src/llm_gateway/langchain_adapter.py`, `packages/llm-gateway-python/tests/test_langchain_adapter.py`, package metadata, package README files, and package test README.

### 2026-05-01: P2.3 Python Gateway SDK Streaming Client Verification

- Date: 2026-05-01
- Question: Did the generic Python SDK gain native synchronous SSE streaming behavior for the accepted gateway contract?
- Baseline: P2.2 implemented `health()`, `list_models()`, and `chat()`, but `stream_chat()` still raised a P2.3 placeholder `NotImplementedError`.
- Change: Implemented standard-library `GatewayClient.stream_chat()` for protected `POST /v1/chat/completions/stream`; added native SSE parsing for `chunk`, `done`, and `error` events; added method-call token validation, lazy HTTP open, token-safe stream error handling, malformed stream detection, and deterministic response cleanup on terminal events, exceptions, and explicit iterator close.
- Result: Editable install passed; package-local pytest passed with `57 passed`; import smoke printed `0.0.1`; `git diff --check -- packages/llm-gateway-python` passed; forbidden implementation-term grep was clean after removing generated editable-install artifacts; generated artifact scan returned clean; VS Code diagnostics for changed SDK files were clean.
- Review: PhD Critic Codex implementation review approved P2.3 with no critical issues and no required follow-up patch.
- Verdict: Pass at `V2 targeted` plus `V0 critic approval`; P2.3 is accepted as complete. No live SDK stream smoke was run because this packet used mocked/stubbed HTTP coverage by design.
- Artifacts: `packages/llm-gateway-python/src/llm_gateway/client.py`, `packages/llm-gateway-python/tests/test_sdk_skeleton.py`, package README files, and package test README.

### 2026-05-01: P2.2 Python Gateway SDK Client And Error Mapping Verification

- Date: 2026-05-01
- Question: Did the generic Python SDK gain native blocking HTTP behavior and typed error mapping for the accepted gateway contract?
- Baseline: P2.1 produced an installable SDK skeleton, but `health()`, `list_models()`, and `chat()` still raised `NotImplementedError` and no native HTTP/error mapping existed.
- Change: Implemented standard-library blocking HTTP calls for public `/health`, authenticated `/v1/models`, and authenticated `/v1/chat/completions`; added camelCase/snake_case native payload mapping, token-safe protected request handling, path-prefix-safe base URL joining, and `GatewayResponseError`/`GatewayTransportError` exports.
- Result: Editable install passed; package-local pytest passed with `42 passed`; import smoke printed `0.0.1`; `git diff --check -- packages/llm-gateway-python` passed; forbidden-import/OpenAI-concept grep was clean after removing generated `egg-info` and `__pycache__`; generated artifact scan returned clean.
- Review: PhD Critic Codex implementation review approved P2.2 with no critical issues and no required follow-up patch.
- Verdict: Pass at `V2 targeted` plus `V0 critic approval`; P2.2 is accepted as complete and P2.3 streaming client is the next planned SDK handoff.
- Artifacts: `packages/llm-gateway-python/src/llm_gateway/client.py`, `packages/llm-gateway-python/src/llm_gateway/errors.py`, `packages/llm-gateway-python/src/llm_gateway/__init__.py`, `packages/llm-gateway-python/tests/test_sdk_skeleton.py`, and package README files.

### 2026-05-01: P2.1 Python Gateway SDK Skeleton Verification

- Date: 2026-05-01
- Question: Did the generic Python gateway SDK skeleton land with package-local metadata, importable modules, scoped tests, boundary hygiene, and implementation review approval?
- Baseline: `packages/llm-gateway-python/` was placeholder-only and had no installable `llm_gateway` package, package-local tests, or public SDK skeleton modules.
- Change: Added package-local setuptools metadata, the `llm_gateway` source package, shallow native gateway types/errors/client placeholders, token-redacting client config, package-local tests, and README setup/test commands.
- Result: Editable install passed; package-local pytest passed with `7 passed`; import smoke printed `0.0.1`; `git diff --check -- packages/llm-gateway-python` passed; forbidden-import/OpenAI-concept grep found no `tradingagents`, `cli`, `choices`, `delta`, or `[DONE]`; generated `egg-info` and `__pycache__` artifacts from verification were removed. Final session-wrap validation also passed full `git diff --check`, VS Code gateway package check/compile/tests (`42` passed), `uv lock --check`, and root pytest (`92 passed, 40 subtests passed`).
- Review: PhD Critic Codex implementation review approved P2.1 with no critical issues and no required follow-up patch.
- Verdict: Pass at `V2 targeted` plus `V0 critic approval`; P2.1 is accepted as complete and P2.2 is the next planned SDK handoff.
- Artifacts: `packages/llm-gateway-python/pyproject.toml`, `packages/llm-gateway-python/src/llm_gateway/**`, `packages/llm-gateway-python/tests/test_sdk_skeleton.py`, and package README files.

### 2026-05-01: Live VS Code Gateway G1 Smoke

- Date: 2026-05-01
- Question: Does the VS Code extension gateway pass the live G1 smoke with an actual VS Code Language Model API model?
- Baseline: Prior endpoint smoke used a fake in-process model service and did not satisfy G1 because the real command-palette start, token-copy path, VS Code model list, model invocation, and SSE runtime path were not exercised.
- Change: Launched the Extension Development Host, ran `TradingAgents Gateway: Start` from the Command Palette, copied the gateway token through the explicit UI path, and ran the G1 smoke commands from `docs/runbooks/gateway-g1-smoke.md` against the live local gateway. The displayed port was `56668`; an initial `5668` attempt was refused because no process was listening there.
- Result: Public `/health` returned `ok` on `127.0.0.1:56668`; authenticated `/v1/models` returned available VS Code models including `gpt-4o-mini`; non-stream `/v1/chat/completions` with `gpt-4o-mini` returned a `gwchat_` assistant response; SSE `/v1/chat/completions/stream` returned `200`, `text/event-stream`, `chunk` events, one `done` event, and no `[DONE]`; authenticated `/shutdown` returned `ok` and the port stopped listening except for `TIME_WAIT`.
- Verdict: Pass at `V4 runtime`; G1 live smoke evidence is complete and accepted for Phase 2 entry. Token value was intentionally not recorded.
- Artifacts: Current-session terminal output, `docs/runbooks/gateway-g1-smoke.md`, and `packages/vscode-llm-gateway`.

### 2026-05-01: Autonomous Gateway HTTP Smoke With Fake Model

- Date: 2026-05-01
- Question: Can the compiled gateway exercise its HTTP endpoints autonomously when live VS Code UI token capture is unavailable?
- Baseline: G1 live smoke still requires an Extension Development Host, explicit gateway start command, explicit token copy action, and a real VS Code model.
- Change: Launched the extension development host with the VS Code CLI, confirmed no gateway `/health` endpoint was already active, then ran a Node module-mode smoke against `dist/index.js` using a fake in-process model service.
- Result: Public `/health`, authenticated `/v1/models`, non-stream `/v1/chat/completions`, SSE `/v1/chat/completions/stream`, no `[DONE]` sentinel, and stop all passed in the autonomous smoke.
- Verdict: Pass at `V2 targeted`; not a G1 pass because no real VS Code command/token/model path was exercised.
- Artifacts: Terminal output from the current session and `docs/runbooks/gateway-g1-smoke.md` for the required manual runtime evidence.

### 2026-05-01: Phase 1 VS Code Gateway P1.1-P1.5 Targeted Verification

- Date: 2026-05-01
- Question: Did the P1.1 through P1.5 VS Code gateway package implementation land with passing package checks and implementation review approval?
- Baseline: `packages/vscode-llm-gateway` started from a placeholder package scaffold and packet-led planning before full Phase 1 endpoint and streaming behavior existed.
- Change: Implemented and reviewed P1.1 through P1.5 for the gateway package, then applied a one-line follow-up export of `GatewayStartedChat` from `packages/vscode-llm-gateway/src/index.ts`.
- Result: Independent package verification passed after P1.5 and the export follow-up: `npm run check`, `npm run compile`, `npm test --if-present` with `42` tests passed (`0` failed), and `git diff --check -- packages/vscode-llm-gateway` with no output.
- Review: P1.5 implementation review via PhD Critic fallback Opus 4.6 returned `approved_with_nonblocking_notes`; critical issues none; no required patch.
- Verdict: Pass at `V2 targeted` plus `V0 critic approval`; live G1 runtime evidence is recorded separately in the 2026-05-01 live smoke entry.
- Artifacts: `packages/vscode-llm-gateway/src/**`, `packages/vscode-llm-gateway/tests/**`, `packages/vscode-llm-gateway/src/index.ts`, and current-session terminal verification output.

### 2026-05-01: Lockfile Refresh And Phase Queue

- Date: 2026-05-01
- Question: Can G0 dependency/package artifacts and Codex handoff planning be made explicit before implementation starts?
- Baseline: `uv.lock` was stale against `pyproject.toml`, and Codex packet details existed without a compact phase-by-phase execution queue.
- Change: Refreshed `uv.lock` with `uv lock`; added a Codex execution queue and missing P0/P6 packet details in `docs/planning/codex-task-packets.md`; added `uv lock --check` and pytest to G0 validation.
- Result: `uv lock --check` passed; `python -m pytest -q` passed with `92 passed, 40 subtests passed in 2.69s` after the lock refresh. Final G0-style validation after planning updates also passed: `git diff --check`, ASCII scan, diagnostics, `uv lock --check`, and `pytest -q` with `92 passed, 40 subtests passed in 2.72s`.
- Verdict: Pass at `V2 targeted`; G0 package-artifact drift is resolved and planning handoff is more explicit.
- Artifacts: `uv.lock`, `docs/planning/codex-task-packets.md`, `docs/planning/gates.md`, and terminal output from the current session.

### 2026-05-01: Requirements Shim Validation

- Date: 2026-05-01
- Question: Does the updated `requirements.txt` compatibility/test-install shim keep local setup and tests working?
- Baseline: `requirements.txt` previously contained only `.` while runtime dependencies lived in `pyproject.toml`.
- Change: Documented `requirements.txt` as a compatibility/test-install shim, kept `.` for local package installation, and added `pytest>=8.3` for the repo test runner.
- Result: Package install specs for the local project plus `pytest>=8.3` installed successfully in `.venv`; `python -m pytest -q` passed with `92 passed, 40 subtests passed in 3.41s`.
- Verdict: Pass at `V2 targeted`; `requirements.txt` is aligned with the current local validation workflow.
- Artifacts: `requirements.txt`, `docs/repo_state/PROVEN_KNOWLEDGE.md`, and terminal output from the current session.

### 2026-05-01: Python 3.13 Patch Upgrade

- Date: 2026-05-01
- Question: Is a newer Python 3.13 patch release available, and does the project still validate after upgrading?
- Baseline: The project `.venv` was configured from system Python 3.13.12.
- Change: Windows Package Manager upgraded `Python.Python.3.13` to 3.13.13, and `.venv` was upgraded in place with `python -m venv --upgrade .venv`.
- Result: `.venv\pyvenv.cfg` and runtime `sys.version` report Python 3.13.13; `python -m pytest -q` passed with `92 passed, 40 subtests passed in 5.07s`.
- Verdict: Pass at `V2 targeted`; project environment upgraded successfully.
- Artifacts: Windows Package Manager output, `.venv\pyvenv.cfg`, and terminal output from the current session.

### 2026-05-01: Local Python Environment Repair

- Date: 2026-05-01
- Question: Can the repository test suite run from a project-local Python environment instead of the configured system Python?
- Baseline: VS Code Python selected system Python 3.13.12, no `.venv` existed, and prior `pytest` collection failed because project dependencies were missing.
- Change: Created an ignored `.venv`, added `.vscode/settings.json` to select `${workspaceFolder}/.venv/Scripts/python.exe`, and installed the local package plus `pytest` into the selected venv.
- Result: `python -m pytest -q` using `.venv` passed with `92 passed, 40 subtests passed in 7.02s`; `git status --short --ignored -- .vscode .venv` showed `.vscode/` untracked and `.venv/` ignored.
- Verdict: Pass at `V2 targeted`; prior pytest environment blocker resolved.
- Artifacts: `.vscode/settings.json`, local ignored `.venv/`, and terminal output from the current session.

### 2026-05-01: Governance Bootstrap Static Validation

- Date: 2026-05-01
- Question: Do the new governance/customization files pass static metadata and markdown hygiene checks?
- Baseline: Governance files were newly created or merged.
- Change: Added canonical workflow helpers, repo-state docs, role agents, prompt wrappers, scoped instructions, and skills.
- Result: Frontmatter scan, stale reference scan, ASCII scan, trailing whitespace/tab scan, generic-governance domain scan, and `git diff --check` passed.
- Verdict: Pass at `V1 static`.
- Artifacts: Terminal validation output in current session; changed-file summary pending final report.

### 2026-05-01: Required Governance Self-Audit

- Date: 2026-05-01
- Question: Does the governance bootstrap satisfy the requested model ownership, critic, lifecycle, documentation, and audit constraints against the actual changed-file list?
- Baseline: Changed-file list included modified `.github` instructions/skills, new agents/prompts/critic skills, canonical workflow docs, repo-state docs, and existing project docs updated to point to the new governance system.
- Change: Manual read-only audit using the newly written PhD Critic contract because newly created custom agents are not invocable inside this already-running chat.
- Result: Approval status `Approved with non-blocking follow-ups`; critical issues none; required fixes none.
- Verdict: Pass at `V0 read` plus existing `V1 static` checks.
- Artifacts: Final report lists changed files, checks, audit result, and remaining confirmations.

### 2026-05-01: Broader Pytest Attempt

- Date: 2026-05-01
- Question: Does the existing project test suite run after governance-only changes?
- Baseline: Python environment configured as system Python 3.13.12.
- Change: Ran `& "C:/Program Files/Python313/python.exe" -m pytest -q`.
- Result: Collection failed because project dependencies were missing from the configured environment, including `langgraph`, `langchain_google_genai`, `langchain_core`, and `questionary`.
- Verdict: Environment blocked; not a governance-file failure.
- Artifacts: Terminal output in current session.

### 2026-05-01: Model Route Confirmation

- Date: 2026-05-01
- Question: Which custom-agent model routes should governance encode?
- Baseline: Previous governance used TODO placeholders for exact route labels.
- Change: User confirmed GPT 5.5 for reasoning, Codex 5.3 for coding, and Opus 4.7 for PhD Critic with Opus 4.6 and Sonnet 4.6 fallbacks.
- Result: Agent and prompt frontmatter now encode the confirmed model routes where supported; prose records high/xhigh reasoning for GPT/Codex by complexity and maximum reasoning for critic work and inspections.
- Verdict: Pass at `V1 static`; runtime model availability still depends on VS Code resolving these labels.
- Artifacts: `.github/agents/*.agent.md`, `.github/prompts/*.prompt.md`, `.github/copilot-instructions.md`, `.github/instructions/model-routing.instructions.md`, and `docs/WORKFLOW_HELPERS.md`.

## Template

- Date:
- Question:
- Baseline:
- Change:
- Result:
- Verdict:
- Artifacts:
