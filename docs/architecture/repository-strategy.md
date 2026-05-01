# Repository Strategy

## Decision

Use two GitHub repositories:

1. **TradingAgents integration repo:** tracks TauricResearch/TradingAgents and contains our VS Code LLM integration patches, governance docs, and TradingAgents-specific adapters.
2. **Generalized agent collaboration repo:** contains reusable platform code for future agent ecosystems.

## Why Two Repositories

The TradingAgents integration needs to stay close to upstream so we can receive updates from TauricResearch/TradingAgents. The generalized platform needs a clean boundary so it does not inherit finance-specific assumptions or upstream-derived code unnecessarily.

Keeping these separate gives us:

- cleaner upstream syncs
- clearer ownership
- easier licensing and provenance review
- less pressure to generalize too early
- a reusable platform that future apps can consume without depending on TradingAgents

## Recommended Names

TradingAgents integration repo options:

- `trading-agents`
- `tradingagents-vscode`
- `tauric-tradingagents-vscode`

Generalized platform repo options:

- `agent-collaboration-platform`
- `agent-ecosystem`
- `collaborative-agents`

The selected integration repo is `rodrmoura/trading-agents`. The current preference for the future generalized platform repo is `agent-collaboration-platform`.

## Fork Or Private Mirror

There are two good ways to create the TradingAgents integration repo.

### Preferred For Upstream Tracking: Named Fork

Use a GitHub fork when public visibility is acceptable. This preserves the GitHub relationship to TauricResearch/TradingAgents and makes upstream comparisons clearer.

Expected command:

```powershell
gh repo fork TauricResearch/TradingAgents --fork-name trading-agents --remote
```

The GitHub CLI can rename the current `origin` remote to `upstream` and set the fork as `origin` when run with `--remote`.

In this workspace, the fork was created successfully, then remotes were set manually because the CLI offered to clone the fork instead of remapping the current checkout.

### Preferred For Private Draft Work: Standalone Mirror

Use a private standalone repository if we want to keep the integration work private at first. This does not preserve GitHub's fork relationship, but we can still fetch and merge upstream through the `upstream` remote.

Expected commands:

```powershell
git remote rename origin upstream
gh repo create trading-agents --private --source . --remote origin
git remote -v
```

If using this path, rename the current remote first so the upstream reference is not overwritten or lost.

## Remote Layout For Integration Repo

After creating our GitHub repository, the local clone should use this remote layout:

```text
origin   -> https://github.com/rodrmoura/trading-agents
upstream -> https://github.com/TauricResearch/TradingAgents
```

The current clone now uses this remote layout. Local `upstream` push is disabled:

```text
origin   -> https://github.com/rodrmoura/trading-agents.git
upstream -> https://github.com/TauricResearch/TradingAgents (fetch)
upstream -> DISABLED (push)
```

Expected commands after the new GitHub repo exists:

```powershell
git remote rename origin upstream
git remote add origin https://github.com/<owner>/<repo>.git
git remote set-url --push upstream DISABLED
git remote -v
```

Do not push local governance docs or integration patches to TauricResearch/TradingAgents.

## Upstream Sync Flow

Keep upstream updates separate from feature work:

```powershell
git fetch upstream
git switch main
git merge upstream/main
```

If our integration patches conflict with upstream changes, resolve that in a dedicated upstream-sync branch or pull request.

## Extraction Rule

When code becomes reusable outside TradingAgents, move it toward the generalized platform repo.

Examples that belong in the platform repo:

- VS Code LLM gateway extension
- Python SDK
- model adapter contracts
- agent manifest schemas
- workflow graph schemas
- tool registry contracts
- shared state, artifact, memory, checkpoint, and event-log models

Examples that belong in the TradingAgents integration repo:

- TradingAgents provider selection changes
- TradingAgents prompt extraction with provenance
- TradingAgents CLI integration options
- finance workflow template wiring
- docs explaining how this integration tracks upstream
