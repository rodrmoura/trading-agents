# Gate Checklist

Each gate is a stop/go checkpoint. Do not move to the next phase because code exists; move only when the gate passes or a blocker is explicitly accepted and documented.

## Gate Rules

- Reasoning Engineer reviews gate readiness.
- Codex Coding Engineer performs validation commands and fixes only from ready ledgers.
- Failed gates produce a TODO item or blocker note.
- Passing a gate should update `TODO.md` and, when historical handoff matters, `docs/CHANGELOG.md`.
- Durable gate decisions should become ADRs.

## G0: Governance And Structure Ready

Must pass before implementation begins.

Inputs to read:

- `PROJECT-GUIDE.md`
- `TODO.md`
- `DOCS-GOVERNANCE.md`
- `.github/copilot-instructions.md`
- `.github/instructions/model-routing.instructions.md`
- `docs/architecture/repository-layout.md`
- `docs/architecture/repository-strategy.md`

Pass criteria:

- `origin` points to `https://github.com/rodrmoura/trading-agents.git`.
- `upstream` fetches from `https://github.com/TauricResearch/TradingAgents`.
- Local `upstream` push is disabled.
- Source-of-truth docs exist and are linked from `docs/README.md`.
- App/package/prompt/example scaffolds exist.
- Model routing policy is present in repo instructions.
- `requirements.txt` is aligned with the dependency ownership rule and `uv.lock` is current with `pyproject.toml`.
- VS Code is opened at `TradingAgents/` root when using repository slash commands.
- Working tree is clean or the only changes are intentionally staged for a governance commit.

Validation:

```powershell
git status --short --branch
git remote -v
git diff --check
rg -n '[^\x00-\x7F]' .github docs apps packages prompts examples PROJECT-GUIDE.md TODO.md DOCS-GOVERNANCE.md CODING-STANDARDS.md SECURITY.md DEPLOY.md CONTRIBUTING.md PROJECT-CHANGELOG.md
uv lock --check
& "c:/VSCode/Tauric/TradingAgents/.venv/Scripts/python.exe" -m pytest -q
```

## G1: VS Code Gateway Spike Ready

Must pass before Python SDK work depends on the gateway.

Pass criteria:

- Extension package builds.
- Gateway starts through explicit VS Code command.
- Gateway binds to `127.0.0.1`.
- Gateway token is required.
- `GET /health` works.
- `GET /v1/models` returns at least one available model or a clear no-model error.
- One chat request succeeds against a selected model or fails with a documented model-access blocker.
- Gateway stops cleanly.
- No prompts, responses, tokens, or credentials are logged by default.
- App-specific tools remain outside the gateway extension.

Files likely touched:

- `packages/vscode-llm-gateway/**`
- `docs/reference/gateway-api-draft.md`
- `docs/runbooks/**`
- `SECURITY.md`
- `TODO.md`

Validation:

- package build/check command for the extension
- focused tests if present
- manual smoke run for start, health, models, chat, stop
- `git diff --check`

## G2: Python SDK And Adapter Ready

Must pass before TradingAgents provider integration depends on the SDK.

Pass criteria:

- Python SDK can call health, model list, and chat endpoints.
- SDK maps gateway errors into typed exceptions.
- Token and base URL configuration do not expose secrets.
- LangChain-compatible adapter can be instantiated and invoked in a focused test.
- Structured-output compatibility has either a working path or a documented fallback.

Files likely touched:

- `packages/llm-gateway-python/**`
- `docs/reference/gateway-api-draft.md`
- `CODING-STANDARDS.md`
- `TODO.md`

Validation:

- targeted Python tests for SDK and adapter
- import smoke check
- `git diff --check`

## G3: TradingAgents VS Code Provider Ready

Must pass before generalized runtime work begins.

Pass criteria:

- `vscode` provider is selectable through the existing provider path.
- One ticker analysis reaches final decision using VS Code-provided model calls.
- Structured decision agents work or fallback is documented.
- Tool-calling compatibility for analysts is tested or explicitly tracked.
- Upstream-derived patches are narrow and documented.
- No direct LLM provider API key is required for the LLM path.

Files likely touched:

- `tradingagents/llm_clients/**`
- `cli/**`
- `apps/tradingagents-adapter/**`
- `packages/llm-gateway-python/**`
- `docs/architecture/code-governance.md`
- `TODO.md`

Validation:

- targeted provider tests
- existing structured-agent tests
- one smoke analysis through the gateway
- `git diff --check`

## G4: Generalized Contracts Ready

Must pass before runtime implementation.

Pass criteria:

- Agent manifest schema is drafted.
- Workflow graph schema is drafted.
- Tool registry and permission model are drafted.
- State, artifact, memory, checkpoint, and event contracts are drafted.
- Product strategy review example is represented through the draft contracts.
- Decision exists on whether to create the separate platform repo now.

Files likely touched:

- `docs/reference/agent-manifest-draft.md`
- `docs/reference/**`
- `packages/agent-schemas/**`
- `docs/decisions/**`
- `TODO.md`

Validation:

- schema validation tests if schemas are implemented
- review against `docs/architecture/project-vision.md`
- `git diff --check`

## G5: Runtime Prototype Ready

Must pass before control-room UI work.

Pass criteria:

- Runtime loads manifests.
- Runtime executes product strategy review without TradingAgents imports.
- Tool registry enforces allow-list permissions.
- Event log captures enough information for a UI to observe a run.
- Minimal checkpoint/resume works or is explicitly deferred.
- Human approval pause is represented or explicitly deferred.

Files likely touched:

- `packages/agent-runtime/**`
- `packages/agent-schemas/**`
- `examples/**`
- `docs/reference/**`
- `TODO.md`

Validation:

- runtime unit tests
- product strategy review demo run
- event-log replay check
- `git diff --check`

## G6: Control Room Prototype Ready

Must pass before treating UI as a product direction.

Pass criteria:

- UI consumes generic event logs.
- UI displays runs, agents, tool calls, artifacts, memory, and approvals.
- UI does not import TradingAgents internals.
- Product strategy review replay works.
- TradingAgents can be added later as a workflow template.

Files likely touched:

- `apps/control-room/**`
- `packages/agent-runtime/**`
- `packages/agent-schemas/**`
- `docs/reference/**`
- `docs/runbooks/**`

Validation:

- UI build/test command once package exists
- screenshot/manual smoke if frontend exists
- event-log replay smoke
- `git diff --check`
