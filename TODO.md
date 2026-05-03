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
- [x] Add mandatory GPT/Codex role ownership policy.
- [x] Add detailed execution plan, gate checklist, Codex task packets, and documentation map.
- [x] Create a callable Codex task implementation agent.
- [x] Install reusable AI-agent governance docs, current-truth state files, role agents, prompt wrappers, and critic skills.
- [x] Repair and validate the project-local Python environment.
- [x] Convert `requirements.txt` into a documented compatibility/test-install shim.
- [x] Refresh `uv.lock` against current `pyproject.toml` metadata.
- [x] Add a phase-by-phase Codex execution queue.
- [x] Run G0-style validation and prepare the commit scope.

## Project 1: Tauric VS Code LLM Integration

- [x] Pass G0 governance and structure gate.
- [x] Create a reusable VS Code extension package skeleton.
- [x] Add a command to start/stop a localhost-only gateway.
- [x] Add generated token protection and safe local binding.
- [x] Implement model listing through the VS Code Language Model API.
- [x] Implement basic chat invocation and streaming.
- [x] Implement cancellation and useful error reporting for consent, quota, and unavailable models.
- [x] Pass G1 manual live VS Code gateway smoke gate.
- [x] Create a Python SDK for the gateway.
- [x] Create a LangChain-compatible adapter.
- [x] Pass G2 Python SDK and adapter gate.
- [x] Add a thin TradingAgents `vscode` LLM provider.
- [ ] Prove Research Manager, Trader, and Portfolio Manager through VS Code models.
- [ ] Add structured-output compatibility.
- [x] Add non-stream native tool-call roundtrip compatibility for analyst agents.

## Project 2: Generalized Agent Collaboration Platform

- [x] Choose the first non-finance workflow to prove genericity: product strategy review.
- [ ] Pass G4 generalized collaboration contracts gate before runtime implementation.
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
- [x] Decide whether `session-wrap` should push by policy or only by explicit user request.
- [x] Confirm exact GPT, Codex, and PhD Critic model route labels.

## Next Recommended Task Packets

- [x] P0.1 Commit governance/model-routing customization when approved.
- [x] P0.2 Confirm VS Code is opened at `TradingAgents/` root for slash-command discovery.
- [x] G1 Run manual live VS Code gateway smoke and record evidence.
- [x] G1 Accept the recorded gate evidence before Phase 2 handoff.
- [x] P2.1 Create Python gateway SDK package skeleton.
- [x] P2.2 Implement gateway client and typed errors.
- [x] P2.3 Implement streaming client.
- [x] P2.4 Implement LangChain-compatible adapter.
- [x] P3.1 Audit TradingAgents provider integration points.
- [x] P3.2 Add thin TradingAgents `vscode` provider boundary.
- [x] P3.3a Prepare operator runbook/direct provider smoke path without claiming full analyst support before tool calling is resolved.
- [x] P3.3b Implement mocked non-stream native tool-call roundtrip support.
- [x] P3.3c Prepare full-graph smoke harness without claiming live proof.
- [ ] P3.3c Run and record live full one-ticker TradingAgents smoke through VS Code models.

## Open Questions

- How should model selection be represented when VS Code model identifiers change over time?
- What initial package ownership should move into `agent-collaboration-platform` after Phase 3?
