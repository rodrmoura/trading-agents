# TODO

Active backlog for the Tauric VS Code LLM integration and generalized agent collaboration platform.

## Current Session

- [x] Clone `TauricResearch/TradingAgents` locally.
- [x] Review repository architecture and explain what the app does.
- [x] Record the two-project roadmap: Tauric VS Code LLM integration first vertical slice, generalized agent collaboration platform second track.
- [x] Add initial architecture docs, ADRs, Copilot instructions, and session lifecycle skills.
- [x] Adapt a reusable structure-only governance model into this project.
- [ ] Review and commit the initial governance documentation when the user is ready.
- [x] Choose exact GitHub repo owner, names, and visibility: public `rodrmoura/trading-agents` for the integration repo; create the generalized platform repo later.
- [x] Choose fork or private standalone mirror for the TradingAgents integration repo: named public fork.
- [x] Create the TradingAgents integration repo.
- [x] Rename current `origin` remote to `upstream` and add our integration repo as `origin`.
- [x] Disable local pushes to the upstream TauricResearch remote.
- [ ] Push the initial governance commit to the integration repo.

## Project 1: Tauric VS Code LLM Integration

- [ ] Create a reusable VS Code extension package skeleton.
- [ ] Add a command to start/stop a localhost-only gateway.
- [ ] Add generated token protection and safe local binding.
- [ ] Implement model listing through the VS Code Language Model API.
- [ ] Implement basic chat invocation and streaming.
- [ ] Implement cancellation and useful error reporting for consent, quota, and unavailable models.
- [ ] Create a Python SDK for the gateway.
- [ ] Create a LangChain-compatible adapter.
- [ ] Add a thin TradingAgents `vscode` LLM provider.
- [ ] Prove Research Manager, Trader, and Portfolio Manager through VS Code models.
- [ ] Add structured-output compatibility.
- [ ] Add tool-calling compatibility for analyst agents.

## Project 2: Generalized Agent Collaboration Platform

- [ ] Define agent manifest schema.
- [ ] Define workflow graph schema.
- [ ] Define tool registry and permission model.
- [ ] Define shared state, event log, artifact, memory, and checkpoint models.
- [ ] Extract TradingAgents prompts into prompt files with provenance.
- [ ] Package TradingAgents as a finance workflow template.
- [ ] Build a minimal non-finance workflow to prove genericity.
- [ ] Design frontend control-room information architecture.

## Governance And Operations

- [x] Decide whether this repo remains a fork or moves into a parent monorepo: use a dedicated TradingAgents integration repo first, then a separate generalized platform repo.
- [x] Add `upstream` remote strategy once our own `origin` exists.
- [ ] Create the generalized agent collaboration platform repo when reusable gateway/runtime code starts.
- [ ] Add a dedicated patch log if upstream-derived code changes.
- [ ] Decide whether `session-wrap` should push by policy or only by explicit user request.
- [ ] Decide whether `PROJECT-CHANGELOG.md` is enough or whether we need release notes later.

## Open Questions

- Should the gateway expose OpenAI-compatible endpoints, native endpoints, or both at first?
- Should app-specific tools execute in Python, the VS Code extension, or a hybrid loop?
- Should the first frontend be a VS Code webview or a standalone browser app?
- What is the first non-finance workflow we want to prove after TradingAgents?
- What exact names should we use for the two GitHub repositories?
