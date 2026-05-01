# Code Governance

## Current Situation

This repository is cloned from `TauricResearch/TradingAgents`. It contains upstream-derived code that we want to keep easy to update while we build our own reusable agent platform around it.

This is two projects in one:

- **Tauric VS Code LLM integration:** upstream-derived TradingAgents finance workflow plus the smallest provider/adapter patches needed to run through our VS Code LLM gateway/extension.
- **Generalized agent collaboration platform:** reusable VS Code model gateway, SDK, agent runtime, prompt/workflow system, memory/tooling model, and future frontend.

The integration can depend on the platform, but the platform should not depend on TradingAgents.

## Ownership Boundaries

| Area | Ownership | Rule |
| --- | --- | --- |
| `tradingagents/` | Upstream-derived | Patch minimally and document why. |
| `cli/` | Upstream-derived | Patch only for integration points such as provider selection. |
| `packages/vscode-llm-gateway/` | Ours | Generic VS Code model gateway. No TradingAgents imports. |
| `packages/llm-gateway-python/` | Ours | Generic Python SDK and LangChain adapter. No finance assumptions. |
| `packages/agent-runtime/` | Ours | Generic workflow runtime. No TradingAgents imports. |
| `apps/tradingagents-adapter/` | Ours | May depend on both generic packages and TradingAgents. |
| `prompts/upstream-tradingagents/` | Mixed | Extracted/adapted TradingAgents prompts with provenance. |
| `docs/` | Ours | Architecture, decisions, and guidance. |

These folders do not all exist yet. They define the intended boundaries as the project grows.

When deciding where code belongs, ask whether the behavior is useful outside TradingAgents. If yes, it belongs in generic platform code. If no, it belongs in the TradingAgents adapter or upstream-derived integration layer.

## Dependency Direction

Allowed:

```text
apps/tradingagents-adapter -> TradingAgents
apps/tradingagents-adapter -> generic packages
TradingAgents integration patch -> generic LLM SDK, only at provider boundary
```

Avoid:

```text
generic packages -> TradingAgents
TradingAgents core -> frontend app
TradingAgents core -> generic runtime internals
```

## Upstream Update Strategy

When we create our own GitHub repo or fork for the TradingAgents integration, use this remote layout:

```text
origin   -> our repo/fork
upstream -> https://github.com/TauricResearch/TradingAgents
```

The current clone still has `origin` pointing at TauricResearch/TradingAgents. Before pushing our work, rename that remote to `upstream` and add our new GitHub repository as `origin`.

Preferred sync flow:

```powershell
git fetch upstream
git switch main
git merge upstream/main
```

Keep upstream syncs separate from feature changes. If a future upstream update conflicts with our patches, resolve it in a dedicated sync branch or pull request.

Create the generalized agent collaboration platform in a separate repository once reusable gateway/runtime code begins. Do not make that platform repository depend on TradingAgents internals.

## Patch Rules

- Prefer adapter code outside upstream-derived folders.
- If a TradingAgents source patch is necessary, keep it narrow.
- Document why each upstream-derived patch exists.
- Do not mix upstream sync changes with generic platform feature work.
- Do not store API keys, VS Code gateway tokens, model credentials, or generated local caches in the repository.

## First Integration Target

The first expected TradingAgents patch should be a thin LLM provider integration:

- add provider `vscode`
- route it through the generic Python SDK
- keep existing agent graph, data tools, memory, and reports intact

The goal is to prove the model gateway without turning TradingAgents into the generic platform itself.
