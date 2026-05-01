# TODO

Active backlog for the Tauric VS Code LLM integration and generalized agent collaboration platform.

## Current Session

- [x] Clone `TauricResearch/TradingAgents` locally.
- [x] Review repository architecture and explain what the app does.
- [x] Record the two-project roadmap: Tauric VS Code LLM integration first vertical slice, generalized agent collaboration platform second track.
- [x] Add initial architecture docs, ADRs, Copilot instructions, and session lifecycle skills.
- [x] Adapt a reusable structure-only governance model into this project.
- [x] Review, commit, and push the initial governance documentation.
- [x] Choose exact GitHub repo owner, names, and visibility: public `rodrmoura/trading-agents` for the integration repo; create the generalized platform repo later.
- [x] Choose fork or private standalone mirror for the TradingAgents integration repo: named public fork.
- [x] Create the TradingAgents integration repo.
- [x] Rename current `origin` remote to `upstream` and add our integration repo as `origin`.
- [x] Disable local pushes to the upstream TauricResearch remote.
- [x] Push the initial governance commit to the integration repo.
- [x] Create the initial document/code scaffold.
- [x] Add roadmap, reference drafts, and runbooks for the next implementation pass.
- [x] Decide first gateway API direction: native minimal API first, OpenAI-compatible facade later.
- [x] Decide generalized platform repo timing: after the TradingAgents gateway vertical slice works here.
- [x] Decide first non-finance workflow: product strategy review.
- [x] Decide control room timing: defer until event contracts exist.
- [x] Review and commit the initial document/code scaffold.

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

- [x] Choose the first non-finance workflow to prove genericity: product strategy review.
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

- Should app-specific tools execute in Python, the VS Code extension, or a hybrid loop?
- What exact name should we use for the future generalized platform repository?
- Should the gateway remain extension-only, or eventually use a separate local service?
