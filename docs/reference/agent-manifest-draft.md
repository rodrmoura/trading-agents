# Agent Manifest Draft

This is a draft contract for generalized agent collaboration. It is not yet implemented.

## Goals

- Describe agents without hardcoding domain-specific Python classes.
- Make roles, tools, inputs, outputs, memory, and stopping conditions explicit.
- Allow TradingAgents to become one workflow template rather than the platform core.

## Draft Agent Manifest

```yaml
id: market_researcher
name: Market Researcher
description: Collects market context relevant to a goal.
role: research
model:
  preference: balanced
  fallback: quick
prompt:
  path: prompts/shared/market_researcher.prompt.md
inputs:
  - goal
  - shared_context
outputs:
  schema: research_report
tools:
  allowed:
    - web_search
    - document_reader
memory:
  scope: run
stopping:
  max_iterations: 3
  requires_final_output: true
```

## Draft Workflow Manifest

```yaml
id: product_strategy_review
goal_schema: strategy_goal
state_schema: strategy_review_state
flow:
  start:
    - market_researcher
    - competitor_researcher
  then:
    - risk_reviewer
  final:
    - strategy_manager
approvals:
  - before: final_decision
```

The first non-finance workflow target is product strategy review. It should prove parallel research agents, a risk reviewer, and a final strategy manager without importing TradingAgents internals.

## Required Concepts

- `agent`: role plus model, prompt, tools, inputs, outputs, memory, and stopping rules.
- `workflow`: graph of agent execution.
- `tool`: callable capability with permissions and typed arguments.
- `artifact`: durable output from an agent or tool.
- `event`: append-only record of workflow activity.
- `checkpoint`: resumable workflow state.
- `approval`: human decision point.

## Open Decisions

- Should manifests be YAML, JSON, or both?
- Should schemas use JSON Schema, Pydantic models, TypeScript types, or generated code?
- How much of LangGraph should be exposed in the generic workflow model?
- How should prompt versioning and provenance work across repositories?
