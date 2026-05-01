# Project Vision

## Objective

Build a reusable local-first agent platform where specialized agents collaborate toward a shared goal, using TradingAgents as the first proving workflow.

TradingAgents already demonstrates a useful pattern:

```text
goal
  -> specialist analysts gather evidence
  -> opposing agents debate conclusions
  -> manager agents synthesize plans
  -> final decision agent commits
  -> memory and checkpoints preserve run history
```

Our long-term goal is to generalize that pattern beyond finance.

This is two projects in one:

1. Put TauricResearch/TradingAgents to work with the VS Code LLM gateway/extension.
2. Create a generalized agent collaboration platform for future multi-agent applications.

## Project 1: Tauric VS Code LLM Integration

Create a reusable VS Code extension and local gateway so TradingAgents and future local apps can call the language models available inside VS Code.

The gateway should be generic and reusable. TradingAgents should be the first consumer, not the only design target.

Target shape:

```text
TradingAgents or future app
  -> Python or OpenAI-compatible client
  -> localhost VS Code model gateway
  -> VS Code Language Model API
  -> available VS Code/Copilot models
```

Expected capabilities:

- list available VS Code chat models
- invoke a selected model
- stream responses
- count tokens when supported
- support cancellation
- expose useful errors for missing consent, missing model, and quota limits
- support structured output and tool-calling loops over time

## Project 2: Generalized Agent Collaboration Platform

Create a manifest-driven runtime for reusable agent teams and workflows.

The framework should define agents through contracts, not hardcoded finance-specific Python functions.

Example agent definition:

```yaml
id: competitor_researcher
name: Competitor Researcher
role: Finds competitor positioning and risks
model: quick
prompt: prompts/agents/competitor_researcher.prompt.md
tools:
  - web_search
  - document_reader
inputs:
  - goal
  - shared_context
outputs:
  schema: research_report
memory:
  scope: project
```

Example workflow definition:

```yaml
id: product_strategy_review
flow:
  parallel:
    - market_researcher
    - competitor_researcher
    - financial_analyst
  then:
    - risk_reviewer
  final:
    - strategy_manager
```

## Design Principles

- TradingAgents is the first integrated ecosystem, not the foundation of all future code.
- Generic packages must avoid finance assumptions.
- Agents need explicit roles, tool permissions, input contracts, output contracts, and stopping conditions.
- The frontend should visualize agent collaboration, artifacts, tool calls, debate, memory, and human approvals.
- Do not over-generalize before the first vertical slice works.
