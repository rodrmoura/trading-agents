---
name: session-resume
description: "Use when: starting or resuming a session, safely fetching/pulling fresh GitHub code, reading project markdown state, checking current repo status, and presenting prioritized next steps before implementation. Read-only planning workflow; does not edit, checkpoint, wrap, commit, or push."
argument-hint: "start | resume | after-pull | plan"
user-invocable: true
disable-model-invocation: false
---

# Session Resume

Use this skill at the beginning of a session. It refreshes the local repository from GitHub when safe, reconstructs project state from markdown, and presents the most useful next steps before coding begins.

This is a start-of-session workflow. Use `/state-sync` for mid-session checkpoints and `/session-wrap` for final validation and optional commit. See [../README.md](../README.md) for the lifecycle matrix.

## When To Use

- The user invokes `/session-resume`.
- The user asks to start, resume, continue, pick back up, pull latest code, or identify next steps.
- A previous session ended or context was compacted and the agent needs to rebuild working state from the repo.
- The user wants a fresh read of GitHub state and project markdown before making changes.

## Core Outcome

At the end, present a concise session briefing with:

- Git branch, fetch/pull result, and working tree state.
- Relevant markdown facts from source-of-truth files.
- Active local environment status if relevant.
- Known validation or dependency warnings from docs or recent runs.
- Recommended next steps, ordered by priority.

Do not commit during `/session-resume`.

## Non-Goals

- Do not edit files unless the user explicitly asks to begin implementation after the resume briefing.
- Do not update docs during the resume itself.
- Do not commit, stage, stash, merge, rebase, reset, or revert work.
- Do not run full validation unless the user asks or the resume task specifically requires it.

## Safe Git Refresh

Always protect local work before pulling:

1. Run `git status --short`.
2. Run `git branch --show-current` and inspect remotes with `git remote -v` if needed.
3. Run `git fetch --all --prune`.
4. If the working tree is clean, run `git pull --ff-only` for the current branch.
5. If the working tree has uncommitted changes, do not pull into it automatically. Report that fresh remote data was fetched but pull is blocked by local changes. Recommend `/session-wrap`, `/state-sync`, a commit, or an explicit user-approved stash/branch strategy.
6. If fast-forward pull fails because local and remote diverged, stop and report the divergence. Do not merge or rebase without explicit user approval.

## Required Markdown Reading

Read these files at minimum when present:

- [docs/README.md](../../../docs/README.md): documentation routing and start points.
- [PROJECT-GUIDE.md](../../../PROJECT-GUIDE.md): product and architecture source of truth.
- [TODO.md](../../../TODO.md): active backlog and task state.
- [DOCS-GOVERNANCE.md](../../../DOCS-GOVERNANCE.md): documentation ownership and routing.
- [PROJECT-CHANGELOG.md](../../../PROJECT-CHANGELOG.md): notable local platform changes.
- [docs/architecture/project-vision.md](../../../docs/architecture/project-vision.md): product and architecture direction.
- [docs/architecture/code-governance.md](../../../docs/architecture/code-governance.md): upstream boundary and folder ownership rules.
- [docs/guidance/copilot-and-skills.md](../../../docs/guidance/copilot-and-skills.md): prompt, skill, and imported-guidance rules.
- `docs/decisions/*.md`: accepted/proposed ADRs.
- [.github/copilot-instructions.md](../../copilot-instructions.md): repo-specific agent rules.
- [.github/skills/README.md](../README.md): session lifecycle matrix.
- [README.md](../../../README.md): upstream TradingAgents setup and usage.

Also inspect relevant changed files or diffs if the working tree is dirty.

## Optional Environment Checks

When local testing is likely, check environment status without printing secrets:

- `Test-Path .env`
- Python environment details if configured
- running VS Code gateway process if implemented
- relevant local terminals or dev servers

Never print `.env` values, provider API keys, local gateway tokens, or model credentials.

## Next-Step Analysis

Use markdown and git state to produce a ranked recommendation. Favor tasks that unblock the current roadmap and reduce risk:

1. Upstream boundary and documentation gaps.
2. VS Code model gateway proof of concept.
3. TradingAgents `vscode` provider integration.
4. Tool-calling and structured-output compatibility.
5. Generic agent manifest/runtime design.
6. Frontend control-room planning.

Call out whether each recommended next step is:

- **Now:** best task for this session.
- **Soon:** important but less immediate.
- **Later:** documented but not blocking yet.

## Final Response Pattern

Keep the briefing concise and actionable:

- **Git:** branch, fetch/pull outcome, dirty/clean state.
- **Read:** key markdown files consulted.
- **Current State:** what is already done or in progress.
- **Risks/Blockers:** only the ones that matter now.
- **Recommended Next Steps:** 3-5 prioritized items.

Do not start implementation after `/session-resume` unless the user asked to both resume and begin the next task.
