# Upstream Sync Runbook

Use this runbook to receive updates from TauricResearch/TradingAgents without mixing upstream changes with local integration work.

## Preconditions

- Working tree is clean or unrelated local work is committed/stashed.
- `origin` points to `https://github.com/rodrmoura/trading-agents.git`.
- `upstream` fetches from `https://github.com/TauricResearch/TradingAgents`.
- Local `upstream` push is disabled.

Check:

```powershell
git status --short --branch
git remote -v
```

## Sync Steps

```powershell
git fetch upstream --prune
git switch main
git merge upstream/main
```

If conflicts occur, stop and resolve them in a dedicated upstream-sync branch or pull request.

## After Sync

Run validation appropriate to changed files. At minimum:

```powershell
git diff --check
```

If upstream changed Python code used by our integration, run targeted tests before pushing.

## Rules

- Do not combine upstream sync with feature work.
- Do not push to `upstream`.
- Document any conflict resolution that changes local integration behavior.
