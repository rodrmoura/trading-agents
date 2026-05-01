# Contributing

## Project Boundary

This repository currently combines upstream-derived TradingAgents code with local governance for the Tauric VS Code LLM integration.

Treat `tradingagents/` and `cli/` as upstream-derived. Keep changes there narrow and documented.

Generic platform work should live outside upstream-derived folders whenever possible while it is being prototyped here. Once reusable gateway/runtime code begins, move it to the separate generalized agent collaboration platform repository.

## Workflow

1. Read [PROJECT-GUIDE.md](PROJECT-GUIDE.md), [TODO.md](TODO.md), and [DOCS-GOVERNANCE.md](DOCS-GOVERNANCE.md).
2. Check `git status --short` before editing.
3. Keep upstream sync work separate from feature work.
4. Update docs in the same change when scope, architecture, setup, security, or governance changes.
5. Run validation appropriate to the changed files.
6. Do not commit unless explicitly asked or a lifecycle command such as `/session-wrap` has been invoked.

## Upstream Updates

Recommended remote layout for this integration repository:

```text
origin   -> our repo or fork
upstream -> https://github.com/TauricResearch/TradingAgents
```

In this workspace, `origin` is `https://github.com/rodrmoura/trading-agents.git` and `upstream` fetches from `https://github.com/TauricResearch/TradingAgents`. Local upstream push is disabled.

Sync upstream separately from local feature work.

## Commit Style

Use concise messages:

- `docs: add project governance guide`
- `docs: record vscode gateway decision`
- `feat: add vscode llm provider`
- `test: cover gateway structured output`

## Pull Request Expectations

- Explain whether the change touches upstream-derived code or generic platform code.
- List validation performed.
- Call out secrets, gateway, tool-calling, or model-access implications.
- Link ADRs for durable architecture decisions.
