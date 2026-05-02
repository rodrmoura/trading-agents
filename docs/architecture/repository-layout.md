# Repository Layout

This repository is the TradingAgents integration repo. It contains upstream-derived TradingAgents code plus local scaffolding for the VS Code LLM integration and early generalized-agent prototypes.

## Top-Level Layout

```text
.github/                    # Copilot instructions, callable agents, prompt wrappers, and workflow skills
apps/                       # App-level integration shells and future UI prototypes
assets/                     # Upstream TradingAgents assets
cli/                        # Upstream-derived TradingAgents CLI
docs/                       # Architecture, ADRs, guidance, runbooks, and reference docs
examples/                   # Small usage examples and future demo workflows
packages/                   # Reusable gateway/runtime packages while they are incubating here
prompts/                    # Prompt inventory, extracted prompts, and shared prompt conventions
scripts/                    # Utility scripts and smoke checks
tests/                      # Upstream-derived and local tests
tradingagents/              # Upstream-derived TradingAgents Python package
```

## Documents

```text
docs/
  README.md
  WORKFLOW_HELPERS.md
  DECISIONS.md
  EXPERIMENT_LOG.md
  CHANGELOG.md
  ROADMAP.md
  repo_state/
    ACTIVE_STATE.md
    PROVEN_KNOWLEDGE.md
  session_capsules/
  architecture/
    code-governance.md
    project-vision.md
    repository-layout.md
    repository-strategy.md
  decisions/
    ADR-TEMPLATE.md
    0001-two-project-roadmap.md
    0002-upstream-boundary-governance.md
    0003-vscode-model-gateway.md
    0004-two-repository-strategy.md
  guidance/
    copilot-and-skills.md
  planning/
    README.md
    execution-plan.md
    gates.md
    codex-task-packets.md
    documentation-map.md
  reference/
    README.md
  runbooks/
    README.md
```

Document routing is governed by `DOCS-GOVERNANCE.md`. Product and architecture truth starts in `PROJECT-GUIDE.md`.

## Code Scaffolds

```text
apps/
  README.md
  tradingagents-adapter/
    README.md
  control-room/
    README.md

packages/
  README.md
  vscode-llm-gateway/
    README.md
    src/README.md
    tests/README.md
  llm-gateway-python/
    README.md
    src/README.md
    tests/README.md
  agent-schemas/
    README.md
    src/README.md
    tests/README.md
  agent-runtime/
    README.md
    src/README.md
    tests/README.md

prompts/
  README.md
  upstream-tradingagents/
    README.md
  shared/
    README.md

examples/
  README.md
```

These are scaffolds, not implemented packages. Add package manifests and source files only when the corresponding implementation work starts.

## Ownership Rules

- `tradingagents/` and `cli/` are upstream-derived. Patch narrowly.
- `apps/tradingagents-adapter/` may depend on both TradingAgents and reusable packages.
- `packages/*` should avoid TradingAgents imports.
- `prompts/upstream-tradingagents/` may contain extracted TradingAgents prompts, but every extracted prompt needs provenance.
- `apps/control-room/` is a placeholder for a future frontend prototype. It should not become coupled to TradingAgents internals.

## Migration Rule

Reusable code can incubate in `packages/` here, but the long-term home is the separate generalized agent collaboration platform repo once that code becomes useful beyond TradingAgents.
