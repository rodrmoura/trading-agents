# Project Changelog

This changelog preserves earlier local platform/governance history. New session-level governance handoff belongs in `docs/CHANGELOG.md`.

The upstream `CHANGELOG.md` remains the TauricResearch/TradingAgents release history.

## [Unreleased]

### Added

- Initial project governance docs: `PROJECT-GUIDE.md`, `DOCS-GOVERNANCE.md`, `TODO.md`, `CODING-STANDARDS.md`, `SECURITY.md`, `DEPLOY.md`, and `CONTRIBUTING.md`.
- Initial architecture docs and ADRs under `docs/`.
- Repo-level Copilot instructions and session lifecycle skills under `.github/`.
- Explicit two-project governance rule separating the Tauric VS Code LLM integration from the generalized agent collaboration platform.
- Two-repository strategy for a TradingAgents integration repo plus a separate generalized agent collaboration platform repo.
- Public integration fork created at `rodrmoura/trading-agents`; local remotes set to `origin` for the fork and `upstream` for TauricResearch/TradingAgents with upstream push disabled.
- Initial document and code scaffold for `apps/`, `packages/`, `prompts/`, `examples/`, `docs/runbooks/`, and `docs/reference/`.
- Roadmap, gateway API draft, agent manifest draft, upstream-sync runbook, and documentation-validation runbook.
- Planning decisions recorded: native minimal gateway API first, platform repo after TradingAgents vertical slice, product strategy review as first generic workflow, and control room deferred until event contracts exist.
- Mandatory model routing policy: GPT reasoning model for reasoning/planning/review and Codex coding model for code/edit/test/verification work, with high or extra-high reasoning by complexity.
- Detailed planning layer under `docs/planning/`: execution plan, gate checklist, Codex task packets, and documentation map.
- Resolved planning choices: use `TradingAgents/` as the workspace root for slash commands, build an extension-only gateway first, keep app-specific tool execution in Python/runtime, and name the future platform repo `agent-collaboration-platform`.
- Added callable `Codex Coding Engineer` custom agent for one-packet-at-a-time implementation work.
- Installed reusable AI-agent governance: `docs/WORKFLOW_HELPERS.md`, current-truth repo-state docs, Reasoning Engineer, Codex Coding Engineer, PhD Critic, prompt wrappers, and PhD skills.
