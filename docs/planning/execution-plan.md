# Execution Plan

This plan exists to keep the two projects controlled, inspectable, and easy to execute without over-engineering.

The work is intentionally phased. Each phase has a clear objective, inputs, dependencies, outputs, gate, and validation scope. Use [../WORKFLOW_HELPERS.md](../WORKFLOW_HELPERS.md) to convert project tasks into ready `Coding-Agent Task Ledger` items before implementation handoff.

## Execution Principles

- Prove the VS Code LLM path with TradingAgents before building the generalized runtime.
- Keep upstream-derived TradingAgents changes narrow and documented.
- Build generic pieces in `packages/` only when the integration needs them.
- Use task packets instead of vague implementation prompts.
- Require a gate before moving from one phase to the next.
- Avoid building UI before event contracts exist.
- Keep docs updated in the same change as decisions, architecture, setup, or code boundary changes.

## Phase Overview

| Phase | Name | Primary Outcome | Gate |
| --- | --- | --- | --- |
| 0 | Governance And Structure | Repository is safe, documented, and ready for implementation | G0 |
| 1 | VS Code Gateway Spike | Extension can expose a local model gateway and call a VS Code model | G1 |
| 2 | Python SDK And LangChain Adapter | Python can call the gateway through a generic SDK/adapter | G2 |
| 3 | TradingAgents VS Code Provider | One TradingAgents analysis runs through VS Code-provided models | G3 |
| 4 | Generalized Collaboration Contracts | Agent/workflow/tool/event contracts are defined | G4 |
| 5 | Runtime Prototype | Product strategy review runs through generalized runtime | G5 |
| 6 | Control Room Prototype | UI can observe generic event logs and approvals | G6 |

## Phase 0: Governance And Structure

Objective: make the fork, docs, scaffold, model-routing policy, and lifecycle commands reliable enough for implementation.

Status: mostly complete; current uncommitted customization changes should be committed before implementation begins.

Read first:

- `PROJECT-GUIDE.md`
- `TODO.md`
- `DOCS-GOVERNANCE.md`
- `.github/copilot-instructions.md`
- `.github/instructions/model-routing.instructions.md`
- `docs/architecture/repository-layout.md`
- `docs/architecture/repository-strategy.md`

Tasks:

- Confirm `origin` points to `rodrmoura/trading-agents`.
- Confirm `upstream` points to `TauricResearch/TradingAgents` with local push disabled.
- Keep dependency setup coherent: `pyproject.toml` owns runtime dependencies, `requirements.txt` stays a compatibility/test-install shim, and `uv.lock` passes `uv lock --check`.
- Commit model-routing customization changes.
- Open VS Code at the `TradingAgents/` root so repository skills and instructions are discoverable.
- Keep scaffold folders as README-only until implementation starts.
- Add a patch log only when the first upstream-derived source patch is made.

Outputs:

- Clean working tree after committed governance changes.
- Visible workspace customization files.
- Planning docs linked from `docs/README.md`.

Gate: G0 in [gates.md](gates.md).

## Phase 1: VS Code Gateway Spike

Objective: prove a VS Code extension can start a localhost gateway and call an available VS Code model.

Read first:

- `docs/reference/gateway-api-draft.md`
- `packages/vscode-llm-gateway/README.md`
- `SECURITY.md`
- `CODING-STANDARDS.md`
- VS Code Language Model API docs as needed

Dependencies:

- VS Code extension package skeleton.
- User has at least one VS Code language model available.
- Gateway API direction remains native minimal API first.
- Phase 1 gateway packaging remains extension-only.

Tasks:

- Create a TypeScript VS Code extension package in `packages/vscode-llm-gateway/`.
- Add commands to start, show status, and stop the gateway.
- Bind the gateway to `127.0.0.1` only.
- Generate a per-session token and require it on every endpoint.
- Keep app-specific tool execution in the Python app/runtime, outside the gateway extension.
- Implement `GET /health`.
- Implement `GET /v1/models` through VS Code model selection/listing.
- Implement one non-streaming chat request endpoint.
- Add initial streaming or explicitly defer it behind a tracked task.
- Add clear error categories for auth, missing model, denied model access, quota/rate limit, cancellation, gateway-not-ready, and unknown model errors.
- Add basic tests or smoke scripts appropriate to the package.

Outputs:

- Running gateway from VS Code command palette.
- Model list response.
- One successful model response through localhost.
- Documented manual smoke steps in `docs/runbooks/` if package tests are not enough.

Gate: G1 in [gates.md](gates.md).

## Phase 2: Python SDK And LangChain Adapter

Objective: let Python apps call the gateway without knowing VS Code extension internals.

Read first:

- `packages/llm-gateway-python/README.md`
- `docs/reference/gateway-api-draft.md`
- `tradingagents/llm_clients/base_client.py`
- `tradingagents/llm_clients/factory.py`
- `tradingagents/llm_clients/model_catalog.py`
- `tests/test_structured_agents.py`

Dependencies:

- Phase 1 gateway endpoints exist.
- Error response shape is stable enough for SDK exceptions.

Tasks:

- Create a Python package scaffold in `packages/llm-gateway-python/`.
- Add a typed client for health, model listing, chat, and streaming if implemented.
- Add typed errors that map gateway error categories.
- Add token and base URL configuration without printing secrets.
- Add a LangChain-compatible adapter with the smallest surface TradingAgents needs.
- Add structured-output compatibility path or document fallback.
- Add focused tests for request construction, error mapping, and adapter behavior.

Outputs:

- Python SDK can call gateway model listing and chat.
- Adapter can be instantiated in a TradingAgents-like context.
- Tests prove error mapping and basic chat behavior.

Gate: G2 in [gates.md](gates.md).

## Phase 3: TradingAgents VS Code Provider

Objective: add the smallest TradingAgents integration needed to run an existing analysis through the VS Code gateway.

Read first:

- `docs/architecture/code-governance.md`
- `docs/reference/gateway-api-draft.md`
- `apps/tradingagents-adapter/README.md`
- `tradingagents/llm_clients/factory.py`
- `tradingagents/llm_clients/base_client.py`
- `tradingagents/llm_clients/model_catalog.py`
- `cli/utils.py`
- `cli/main.py`
- `tradingagents/graph/trading_graph.py`
- `tradingagents/agents/schemas.py`

Dependencies:

- Phase 2 SDK/adapter works.
- Gateway is running locally.
- A test ticker and model selection are chosen.

Tasks:

- Add provider name `vscode` at the provider boundary only.
- Route `vscode` provider calls through the Python SDK/adapter.
- Add configuration for gateway base URL, token, and model id without storing secrets.
- Add CLI provider selection support if needed.
- Add smoke test or script for one ticker analysis through the gateway.
- Preserve existing TradingAgents graph, data tools, memory, and reports.
- Document every upstream-derived source patch.

Outputs:

- One ticker analysis runs through VS Code-provided models.
- Structured manager/trader outputs work or fallback is documented.
- Tool-calling compatibility is tested or explicitly tracked as the next task.

Gate: G3 in [gates.md](gates.md).

## Phase 4: Generalized Collaboration Contracts

Objective: define the reusable contracts before building the generalized platform runtime.

Read first:

- `docs/reference/agent-manifest-draft.md`
- `packages/agent-schemas/README.md`
- `docs/architecture/project-vision.md`
- `docs/architecture/roadmap.md`
- TradingAgents agent state and graph files for inspiration, not dependency

Dependencies:

- Phase 3 proves a real workflow through the gateway.
- Product strategy review remains the first non-finance workflow.

Tasks:

- Decide schema format: YAML/JSON input with JSON Schema, Pydantic, TypeScript types, or generated contracts.
- Define agent manifest fields.
- Define workflow graph fields.
- Define tool registry and permission model.
- Define shared state, artifact, event, memory, and checkpoint contracts.
- Define prompt provenance/version fields.
- Create product strategy review example manifests.
- Decide when to create the generalized platform repo.

Outputs:

- Draft contracts in `docs/reference/` and/or `packages/agent-schemas/`.
- Example product strategy review workflow.
- ADRs for durable schema/runtime decisions.

Gate: G4 in [gates.md](gates.md).

## Phase 5: Generalized Runtime Prototype

Objective: run product strategy review through a generic manifest-driven runtime without TradingAgents imports.

Read first:

- `packages/agent-runtime/README.md`
- `packages/agent-schemas/README.md`
- `docs/reference/agent-manifest-draft.md`
- `docs/architecture/roadmap.md`

Dependencies:

- Phase 4 contracts are stable enough for a prototype.
- Platform repo decision is resolved: future repo name is `agent-collaboration-platform`.
- Gateway model adapter is available without TradingAgents dependencies.

Tasks:

- Create runtime package scaffold if not already implemented.
- Load agent and workflow manifests.
- Execute a simple directed workflow.
- Add tool registry with allow-list enforcement.
- Add shared state and artifact store.
- Emit event logs for agent start, model request, tool call, artifact created, approval requested, and run completed.
- Add checkpoint/resume for minimal workflow state.
- Run product strategy review as the first non-finance workflow.

Outputs:

- Generic runtime can run product strategy review.
- Runtime has no TradingAgents imports.
- Event log is sufficient for future UI.

Gate: G5 in [gates.md](gates.md).

## Phase 6: Control Room Prototype

Objective: visualize agent collaboration using generic event contracts.

Read first:

- `apps/control-room/README.md`
- `docs/reference/agent-manifest-draft.md`
- event log contract from Phase 4/5
- `docs/architecture/project-vision.md`

Dependencies:

- Phase 5 emits stable event logs.
- UI surface decision is made: VS Code webview or standalone browser app.

Tasks:

- Choose first UI surface.
- Display runs, agents, tool calls, artifacts, memory, and approvals.
- Read generic event logs; do not hardcode TradingAgents concepts.
- Add minimal approval interaction if runtime supports approval pauses.
- Add one demo run replay from product strategy review.

Outputs:

- Control room prototype visualizes a generic run.
- TradingAgents can appear later as one workflow template, not as the UI core.

Gate: G6 in [gates.md](gates.md).

## Anti-Drift Rules

- If a task changes product direction, update `PROJECT-GUIDE.md` and `TODO.md`.
- If a task changes architecture, add or update an ADR.
- If a task changes file ownership, update `docs/architecture/code-governance.md` and `docs/architecture/repository-layout.md`.
- If a task changes setup or commands, update `DEPLOY.md` and `docs/runbooks/`.
- If a task changes gateway or manifest contracts, update `docs/reference/`.
- If a task touches upstream-derived files, document why and keep the patch narrow.
- If a task produces reusable code, check whether it belongs in `packages/` or the future generalized platform repo.
