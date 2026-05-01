# Project Changelog

This changelog tracks our local platform and governance work around the cloned TradingAgents repository.

The upstream `CHANGELOG.md` remains the TauricResearch/TradingAgents release history.

## [Unreleased]

### Added

- Initial project governance docs: `PROJECT-GUIDE.md`, `DOCS-GOVERNANCE.md`, `TODO.md`, `CODING-STANDARDS.md`, `SECURITY.md`, `DEPLOY.md`, and `CONTRIBUTING.md`.
- Initial architecture docs and ADRs under `docs/`.
- Repo-level Copilot instructions and session lifecycle skills under `.github/`.
- Explicit two-project governance rule separating the Tauric VS Code LLM integration from the generalized agent collaboration platform.
- Two-repository strategy for a TradingAgents integration repo plus a separate generalized agent collaboration platform repo.
- Public integration fork created at `rodrmoura/trading-agents`; local remotes set to `origin` for the fork and `upstream` for TauricResearch/TradingAgents with upstream push disabled.
