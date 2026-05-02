# Historical Session Log

Newest first. This file is not default resume input; use it when historical reconstruction matters.

## 2026-05-01 (P2.4 SDK LangChain Adapter Wrap)

- Focus: Implement and review the Python SDK's optional LangChain-compatible adapter.
- Outcome: P2.4 is implemented, verified, and PhD Critic-approved with no required follow-up patch.
- What Changed: Added optional LangChain Core extra metadata, `GatewayChatModel`, native `invoke()` and `stream()` behavior through the SDK client, prompt-template/message role coverage, text block normalization, token-safe stream errors, explicit structured-output/tool-calling deferrals, README updates, and expanded package tests to `73 passed`.
- What Failed: Editable install/test verification regenerated SDK package artifacts; they were removed before wrap. No live gateway adapter call or TradingAgents provider run was performed because those belong to later packets.
- Pointers: `docs/EXPERIMENT_LOG.md`, `docs/repo_state/ACTIVE_STATE.md`, `docs/planning/codex-task-packets.md`, `packages/llm-gateway-python/**`.
- Next Direction: Prepare the P3.1 TradingAgents provider integration audit ledger; keep the broad dirty worktree uncommitted until the user explicitly approves commit scope.

## 2026-05-01 (P2.3 SDK Streaming Client Wrap)

- Focus: Implement and review the Python SDK's native synchronous SSE streaming client.
- Outcome: P2.3 is implemented, verified, and PhD Critic-approved with no required follow-up patch.
- What Changed: Replaced the `stream_chat()` placeholder with a token-validated lazy iterator for `/v1/chat/completions/stream`; added native SSE parsing for `chunk`, `done`, and `error`; added token-safe stream error handling, malformed stream detection, response cleanup tests, README updates, and expanded package tests to `57 passed`.
- What Failed: Editable install/test verification regenerated SDK package artifacts; they were removed before wrap. No live SDK stream smoke was run because P2.3 validation is mocked/stubbed HTTP by design.
- Pointers: `docs/EXPERIMENT_LOG.md`, `docs/repo_state/ACTIVE_STATE.md`, `docs/planning/codex-task-packets.md`, `packages/llm-gateway-python/**`.
- Next Direction: Prepare the P2.4 LangChain-compatible adapter ledger; keep the broad dirty worktree uncommitted until the user explicitly approves commit scope.

## 2026-05-01 (P2.2 SDK Client And Errors Wrap)

- Focus: Implement and review the Python SDK's native blocking client and typed error mapping.
- Outcome: P2.2 is implemented, verified, and PhD Critic-approved with no required follow-up patch.
- What Changed: Added standard-library HTTP behavior for `health()`, `list_models()`, and `chat()`; added native payload parsing/serialization, token-safe protected requests, path-prefix-safe URL joining, `GatewayResponseError`, `GatewayTransportError`, README updates, and expanded package tests.
- What Failed: Editable install/test verification regenerated SDK `egg-info` and `__pycache__` artifacts; they were removed before wrap. No live gateway SDK call was run because P2.2 validation is mocked/stubbed HTTP by design.
- Pointers: `docs/EXPERIMENT_LOG.md`, `docs/repo_state/ACTIVE_STATE.md`, `docs/planning/codex-task-packets.md`, `packages/llm-gateway-python/**`.
- Next Direction: Prepare the P2.3 streaming client ledger; keep the broad dirty worktree uncommitted until the user explicitly approves commit scope.

## 2026-05-01 (G1 Acceptance And P2.1 SDK Skeleton Wrap)

- Focus: Accept the live G1 gateway smoke evidence and begin Phase 2 with the Python SDK package skeleton.
- Outcome: G1 is accepted for Phase 2 entry, and P2.1 is implemented, verified, and PhD Critic-approved with no required follow-up patch.
- What Changed: Added the installable `packages/llm-gateway-python` package skeleton, public `llm_gateway` modules, token-redacting config placeholder, native gateway datatypes/errors, package-local tests, and package README commands.
- What Failed: An initial live smoke used port `5668`, but the real listener was `56668`; editable install/test verification also created generated package artifacts that were removed before wrap.
- Pointers: `docs/EXPERIMENT_LOG.md`, `docs/repo_state/ACTIVE_STATE.md`, `docs/planning/codex-task-packets.md`, `packages/llm-gateway-python/**`, `docs/runbooks/gateway-g1-smoke.md`.
- Next Direction: Prepare the P2.2 gateway client and typed errors ledger; keep the broad dirty worktree uncommitted until the user explicitly approves commit scope.

## 2026-05-01 (Phase 1 Gateway Session Wrap)

- Focus: Complete and review the VS Code gateway package Phase 1 implementation packets P1.1 through P1.5.
- Outcome: `packages/vscode-llm-gateway` implementation and review are complete for P1.1-P1.5, including a one-line export follow-up for `GatewayStartedChat`; package checks, compile, tests, diff hygiene, and an autonomous fake-model HTTP smoke passed.
- What Changed: Implemented lifecycle/auth endpoints, model listing, non-streaming chat, SSE streaming, cancellation/error handling, and aligned source exports for Phase 1 package scope.
- What Failed: Manual live VS Code extension smoke with a real model has not been run yet, so G1 is not accepted; the required command start and token-copy path need UI interaction.
- Pointers: `packages/vscode-llm-gateway/src/**`, `packages/vscode-llm-gateway/tests/**`, `docs/EXPERIMENT_LOG.md`, `docs/repo_state/ACTIVE_STATE.md`, `docs/planning/codex-task-packets.md`, `docs/runbooks/gateway-g1-smoke.md`.
- Next Direction: Run manual G1 live smoke and gate acceptance review before any P2.1 Phase 2 implementation handoff; wait for user approval before any commit.

## 2026-05-01

- Focus: Bootstrap reusable AI-agent governance, repair the local Python environment, and make dependency/setup planning resumable.
- Outcome: Governance bootstrap installed and self-audit approved with non-blocking follow-ups; local Python setup now uses an ignored `.venv` on Python 3.13.13, `requirements.txt` and `uv.lock` are aligned with current dependency ownership, and the test suite passes.
- What Changed: Added canonical workflow helpers, current-truth repo-state docs, governance decisions/logs, role agents, prompt wrappers, documentation instruction, lifecycle skills, critic skills, confirmed model route labels, `.vscode` interpreter selection, a documented `requirements.txt` compatibility/test-install shim, refreshed `uv.lock`, and a phase-by-phase Codex execution queue.
- What Failed: Initial agent/skill patch had to be split because the patch format could not delete and add the same existing paths in one operation; the first broad `pytest` attempt failed until the local environment dependencies were installed.
- Pointers: `docs/WORKFLOW_HELPERS.md`, `docs/repo_state/ACTIVE_STATE.md`, `docs/repo_state/PROVEN_KNOWLEDGE.md`, `docs/EXPERIMENT_LOG.md`, `docs/planning/codex-task-packets.md`, `requirements.txt`, `uv.lock`, `.vscode/settings.json`, `.github/agents/README.md`, `.github/skills/README.md`.
- Next Direction: Reload/open VS Code at the repository root, review and commit the prepared G0 scope when approved, then start P1.1 VS Code extension package skeleton.

## Template

- Date:
- Focus:
- Outcome:
- What Changed:
- What Failed:
- Pointers:
- Next Direction:
