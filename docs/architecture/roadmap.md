# Roadmap

This roadmap keeps the two projects moving together without collapsing them into one rewrite.

Detailed execution tasks live in [../planning/execution-plan.md](../planning/execution-plan.md). Gate criteria live in [../planning/gates.md](../planning/gates.md). Coding-model task packets live in [../planning/codex-task-packets.md](../planning/codex-task-packets.md).

## Milestone 0: Governance And Structure

Status: in progress. The remaining gate item is committing the latest model-routing customization and planning docs.

Exit criteria:

- Integration fork exists and tracks upstream safely.
- Project guide, docs governance, ADRs, coding standards, security, deploy, contributing, and changelog exist.
- App/package/prompt/example scaffolds exist and are documented.
- Open decisions are captured in `PROJECT-GUIDE.md` and `TODO.md`.

## Milestone 1: VS Code Gateway Spike

Goal: prove that a VS Code extension can expose a local model gateway safely.

API direction: native minimal API first. Add an OpenAI-compatible facade later only after the native path proves the VS Code model loop.

Packaging direction: extension-only for the first gateway spike. App-specific tools run in the Python app/runtime, not in the extension.

Exit criteria:

- Extension starts and stops a localhost-only gateway.
- Gateway lists VS Code chat models.
- Gateway invokes one selected model and streams output.
- Gateway requires a generated token.
- Errors for missing consent, unavailable model, quota, cancellation, and unknown failures are visible.

## Milestone 2: Python SDK And LangChain Adapter

Goal: make the gateway usable from Python without app-specific code.

Exit criteria:

- Python SDK calls model listing and chat endpoints.
- Streaming and cancellation are represented cleanly.
- LangChain-compatible adapter can be used where TradingAgents expects a chat model.
- Structured-output behavior has a tested compatibility path.

## Milestone 3: TradingAgents VS Code Provider

Goal: run a TradingAgents analysis through VS Code-provided models.

Exit criteria:

- `vscode` provider is available through the existing provider selection path.
- One ticker analysis completes through the existing TradingAgents graph.
- Research Manager, Trader, and Portfolio Manager structured outputs work or have a documented fallback.
- Upstream-derived patches are narrow and documented.

## Milestone 4: Generalized Collaboration Contracts

Goal: define the reusable contracts before building a broad platform.

First non-finance workflow: product strategy review.

Exit criteria:

- Agent manifest draft exists.
- Workflow graph draft exists.
- Tool registry and permission model draft exists.
- Event, artifact, memory, and checkpoint contracts are drafted.
- First non-finance workflow is selected.

## Milestone 5: Generalized Runtime Prototype

Goal: run one non-finance workflow through the generalized runtime.

Planned future repository name: `agent-collaboration-platform`.

Exit criteria:

- Agents load from manifests.
- Workflow graph executes with shared state and event logging.
- Tools are explicitly registered and permissioned.
- Human approval pause is represented, even if minimal.
- Runtime has no TradingAgents imports.

## Milestone 6: Control Room Prototype

Goal: visualize agent collaboration once event contracts exist.

Timing: defer UI work until generic event contracts exist.

Exit criteria:

- UI shows runs, agents, tool calls, artifacts, memory, and approvals.
- UI consumes generic event logs.
- TradingAgents appears as one workflow/template, not as a hardcoded UI assumption.
