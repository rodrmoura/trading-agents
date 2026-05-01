# Project Guide

Tauric VS Code LLM Integration and Generalized Agent Collaboration Platform

---

## Governance And Source Of Truth

This file is the product and architecture source of truth for our work around the cloned TradingAgents repository and the future generalized agent collaboration platform.

## Two Projects In One

This workspace intentionally carries two related projects:

1. **Tauric VS Code LLM integration:** put the cloned TauricResearch/TradingAgents app to work with the VS Code LLM gateway/extension while keeping upstream-derived code usable, updateable, and minimally patched.
2. **Generalized agent collaboration platform:** build a reusable agent-collaboration system with gateway, SDK, runtime, prompts, workflows, memory, tools, and future frontend pieces that can serve many apps, not only TradingAgents.

These projects should collaborate through narrow adapter boundaries. Do not let TradingAgents-specific finance assumptions leak into generic platform packages, and do not let generic platform experiments make the upstream-derived TradingAgents code hard to update.

When project documents conflict, use this order:

1. `PROJECT-GUIDE.md` - product scope, end goal, architecture direction, project boundaries, and launch constraints.
2. `TODO.md` - active implementation backlog translated from this guide.
3. `DOCS-GOVERNANCE.md` - documentation ownership, routing, update triggers, and drift control.
4. `docs/decisions/` - durable architecture and product decisions with rationale and consequences.
5. `CODING-STANDARDS.md` - code, testing, integration, and boundary rules.
6. `SECURITY.md` and `DEPLOY.md` - security and operations runbooks.
7. `docs/architecture/` and `docs/guidance/` - supporting architecture and working guidance.
8. `.github/copilot-instructions.md` and `.github/skills/` - agent behavior and lifecycle commands.
9. `README.md` - upstream TradingAgents overview and user-facing quick start.
10. `PROJECT-CHANGELOG.md` - notable repository-visible changes for our local platform work.

The upstream `CHANGELOG.md` belongs to TauricResearch/TradingAgents. Do not use it for our local platform governance notes unless we intentionally contribute upstream.

Any change that affects product scope, architecture, upstream boundary policy, VS Code model gateway design, generic agent runtime design, security, deployment, prompts, skills, or documentation governance must update this guide and `TODO.md` in the same change. Use `DOCS-GOVERNANCE.md` to decide which supporting files also need updates.

## Current Status

> Last updated: 2026-05-01

- **Upstream clone:** Done. `TauricResearch/TradingAgents` is cloned locally, our fork is configured as `origin`, and upstream push is disabled locally.
- **Repository understanding:** Done. The TradingAgents architecture, CLI, LLM provider layer, data tools, memory log, checkpointing, tests, and Docker setup have been reviewed.
- **Project direction:** Drafted. The work is split into Tauric VS Code LLM integration and the generalized agent collaboration platform.
- **Repository strategy:** Active. `rodrmoura/trading-agents` is the public TradingAgents integration fork; `TauricResearch/TradingAgents` is preserved as `upstream` with local push disabled. The generalized platform repository will be created later when reusable code starts.
- **Governance docs:** Baseline committed and pushed. The initial document/code scaffold, roadmap, reference drafts, and runbooks are ready for the next implementation pass.
- **VS Code model gateway:** Not started. No extension or gateway code exists yet.
- **TradingAgents VS Code provider:** Not started. No code changes have been made inside upstream-derived TradingAgents files.
- **Generalized agent collaboration platform:** Not started. Current work is planning and governance only.
- **Frontend control room:** Not started. Long-term target only.

---

## 1. Vision And Goals

Build a local-first agent platform where specialized agents collaborate toward shared goals, using TradingAgents as the first proving workflow.

The immediate goal is to let TradingAgents use the language models available inside VS Code instead of requiring direct external provider API keys for every run.

The long-term goal is a generic agent ecosystem with reusable agents, tools, workflows, memory, checkpoints, human approvals, and a frontend control room.

## 2. Project Boundaries

### Project 1: Tauric VS Code LLM Integration

Build a reusable VS Code extension and local model gateway, then use it to run TradingAgents through the models available inside VS Code.

Expected shape:

```text
TradingAgents or future local app
  -> Python SDK or OpenAI-compatible client
  -> localhost VS Code model gateway
  -> VS Code Language Model API
  -> models available in VS Code
```

Project 1 deliverables:

- VS Code extension command to start/stop the gateway.
- Localhost-only API with generated token protection.
- Model listing endpoint.
- Chat invocation and streaming.
- Python SDK and LangChain-compatible adapter.
- Thin TradingAgents `vscode` LLM provider integration.
- Structured-output compatibility for decision agents.
- Tool-calling compatibility for analyst agents.

Project 1 success criteria:

- TradingAgents can run one end-to-end analysis through VS Code-provided models.
- The integration does not require direct model provider API keys for the LLM path.
- The gateway can stream responses, fail clearly, and stop cleanly.
- TradingAgents upstream-derived code changes are limited to provider/adapter boundaries.
- The gateway and SDK remain reusable by a second non-TradingAgents app.

### Project 2: Generalized Agent Collaboration Platform

Build a manifest-driven multi-agent runtime that can support TradingAgents-like collaboration in other domains.

Project 2 deliverables:

- Agent manifest schema.
- Workflow graph schema.
- Tool registry.
- Shared state and artifact model.
- Memory and checkpoint model.
- Event log for replay and UI visualization.
- Frontend control room for goals, agents, runs, artifacts, approvals, and memory.
- TradingAgents packaged as a finance workflow template.

Project 2 success criteria:

- At least one non-finance workflow runs through the generalized runtime.
- Agents are configured through manifests, not hardcoded Python teams.
- Tools, memory, artifacts, checkpoints, and event logs have explicit contracts.
- A frontend can observe a run without depending on TradingAgents internals.
- TradingAgents can be represented as one workflow template instead of the platform core.

## 3. First Vertical Slice

The first implementation slice should prove the smallest useful loop:

```text
VS Code extension starts local gateway
  -> Python SDK lists/selects a VS Code model
  -> TradingAgents uses provider = "vscode"
  -> one ticker analysis runs through the existing graph
  -> structured decision output is returned
  -> logs show gateway/model errors clearly
```

This slice intentionally excludes the generalized runtime and frontend control room. Those start after the gateway path works against a real TradingAgents run.

## 4. Repository Strategy

Use two GitHub repositories, matching the two-project split.

### Repository 1: TradingAgents Integration

Purpose: keep a working fork or mirror of TauricResearch/TradingAgents where we can commit integration patches, governance docs, and VS Code LLM gateway adapters while still receiving upstream TradingAgents updates.

Repository: `https://github.com/rodrmoura/trading-agents`.

Creation path: named public fork. GitHub preserves the upstream relationship to TauricResearch/TradingAgents.

Recommended remote layout after creation:

```text
origin   -> https://github.com/rodrmoura/trading-agents
upstream -> https://github.com/TauricResearch/TradingAgents
```

Local `upstream` push is disabled to reduce accidental pushes to TauricResearch/TradingAgents.

This repository may contain upstream-derived TradingAgents code, local governance docs, narrow provider integration patches, and adapter code that exists only to make TradingAgents use the VS Code gateway.

### Repository 2: Generalized Agent Collaboration Platform

Purpose: keep reusable platform code clean: VS Code LLM gateway, SDKs, agent runtime, schemas, prompt/workflow abstractions, memory, tool registry, event log, and future frontend.

Recommended name: `agent-collaboration-platform`, `agent-ecosystem`, or `collaborative-agents`.

This repository should not import TradingAgents internals. TradingAgents can become one example, template, or adapter that consumes the platform.

### Recommended Sequence

1. Commit and push the governance docs and any future TradingAgents integration patches to `rodrmoura/trading-agents`.
2. Keep upstream syncs separate from local feature work.
3. Create the generalized platform repo only when we start extracting reusable gateway/runtime code.
4. Move reusable code from the integration repo to the platform repo when it is no longer TradingAgents-specific.

## 5. Non-Goals

- Do not build live brokerage or real trade execution unless explicitly scoped later.
- Do not rewrite TradingAgents into a generic framework before the VS Code gateway works.
- Do not make generic runtime packages depend on TradingAgents internals.
- Do not store secrets, local gateway tokens, provider API keys, or generated caches in the repository.
- Do not modify upstream-derived files casually.
- Do not create the generalized platform repository until reusable code is ready to move or start there.
- Do not build a frontend before the gateway/runtime contracts are clear enough to visualize.

## 6. Architecture Principles

- Always reason about the work as two projects in one: the Tauric VS Code LLM integration and the generalized agent collaboration platform.
- TradingAgents is the first integrated ecosystem, not the foundation of every future abstraction.
- Generic packages must avoid finance assumptions.
- Integration patches inside `tradingagents/` and `cli/` should be narrow and documented.
- Agents should have explicit roles, tools, inputs, outputs, memory scope, and stopping conditions.
- Workflows should be graph-shaped and contract-driven, not loose multi-agent chat.
- The frontend should visualize collaboration, tool calls, artifacts, memory, disagreements, and human approvals.
- Upstream syncs should be explicit and separate from feature work.

## 7. Decision Backlog

Resolved decisions from the current planning pass:

- Gateway API shape: native minimal API first; add OpenAI-compatible facade later if useful.
- Platform repo timing: create the generalized platform repo after the TradingAgents gateway vertical slice works here.
- First non-finance workflow: product strategy review.
- Control room timing: defer UI until event contracts exist.

Open decisions that should be resolved before implementation goes far:

- Gateway packaging: VS Code extension only, or extension plus separate local service later.
- Tool execution boundary: app process, extension process, or hybrid.
- Future platform repo name and initial package ownership.

## 8. Intended Repository Shape

Near term inside this clone:

```text
.github/                    # Copilot instructions and lifecycle skills
docs/                       # Architecture notes, ADRs, and guidance
examples/                   # Local examples and future demo workflows
packages/                   # Future generic gateway/runtime packages
apps/                       # Future app/adapters/frontend
prompts/                    # Future extracted and generic prompts
tradingagents/              # Upstream-derived TradingAgents package
cli/                        # Upstream-derived TradingAgents CLI
```

Long term, the generalized platform should live in its own repository. The TradingAgents integration repository should either remain a fork/mirror or become a thin integration app that consumes the platform.

## 9. Update Rules

- Update `TODO.md` whenever task state changes.
- Add or update an ADR in `docs/decisions/` for durable decisions with meaningful alternatives.
- Update `DOCS-GOVERNANCE.md` when documentation routing or lifecycle command behavior changes.
- Update `CODING-STANDARDS.md` when implementation conventions change.
- Update `SECURITY.md` when gateway auth, secrets, model access, or data handling rules change.
- Update `DEPLOY.md` when local setup, packaging, gateway operation, or release flow changes.
- Update `PROJECT-CHANGELOG.md` for notable local platform changes.
