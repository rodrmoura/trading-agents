# Copilot And Skills Guidance

## Purpose

This document explains how we should use Copilot instructions, prompts, and skills for this project, including how to adapt reusable guidance from prior projects without importing project-specific assumptions.

## Current Recommendation

Start with root governance docs, repo-level Copilot instructions in `.github/copilot-instructions.md`, supporting project docs in `docs/`, and a small session lifecycle skill set adapted from a reusable prior-project structure.

Keep custom skills limited to workflows we expect to repeat. Do not add domain-heavy skills until the workflow has stabilized in this project.

## Reusing Prior-Project Guidance

We can reuse guidance from prior projects, but only after review.

Good candidates to reuse:

- planning and review workflow preferences
- coding style expectations that are not product-specific
- testing and verification habits
- risk analysis habits
- documentation conventions
- multi-agent planning patterns

Do not copy blindly:

- prior-project-specific architecture
- security or domain assumptions that do not apply here
- file paths, package names, services, or commands from that repo
- specialized skills that depend on another project's internals

## Import Process

When prior project files are available in this workspace, import guidance this way:

1. Read the source instruction/skill file.
2. Classify each rule as `generic`, `adaptable`, or `project-specific`.
3. Copy only `generic` rules directly.
4. Rewrite `adaptable` rules for this project.
5. Exclude `project-specific` rules.
6. Record the source and adaptation in this document or a future `docs/guidance/imported-guidance.md` file.

## Imported Structure

Imported from a prior customization structure on 2026-05-01:

- `.github/skills/README.md`: lifecycle matrix for session commands
- `.github/skills/state-sync/SKILL.md`: mid-session markdown checkpoint command
- `.github/skills/session-resume/SKILL.md`: start-of-session read-only resume command
- `.github/skills/session-wrap/SKILL.md`: end-of-session validation and optional commit command

Adaptation notes:

- Removed prior-project product, security, domain, and deployment assumptions.
- Replaced source-of-truth docs with this project's current docs: `PROJECT-GUIDE.md`, `TODO.md`, `DOCS-GOVERNANCE.md`, `docs/architecture/project-vision.md`, `docs/architecture/code-governance.md`, `docs/guidance/copilot-and-skills.md`, and `docs/decisions/*.md`.
- Preserved the lifecycle distinction: resume is read-only, state-sync is lightweight docs preservation, session-wrap is comprehensive closure.
- Made push behavior optional for this project. `session-wrap` may commit when explicitly invoked, but should push only when the user explicitly asks or a future documented policy says so.

## Active Lifecycle Commands

- `/session-resume`: start or resume a session by safely fetching remote state, reading project docs, and recommending next steps. It should not edit files.
- `/state-sync`: preserve in-progress state into the smallest useful set of markdown files. It should not pull, stage, commit, or push.
- `/session-wrap`: finalize completed work by updating relevant docs, running scoped validation, reviewing diffs, and committing when appropriate. It should not force-push or include unrelated changes.

## Suggested Customizations Later

Potential future files:

```text
.github/copilot-instructions.md
.github/instructions/upstream-boundary.instructions.md
.github/instructions/vscode-gateway.instructions.md
.github/instructions/agent-runtime.instructions.md
.github/prompts/architecture-review.prompt.md
.github/prompts/upstream-sync-review.prompt.md
```

Potential future skills:

- `sync-upstream-tradingagents`
- `design-agent-workflow`
- `review-agent-contract`
- `extract-agent-prompt`
- `validate-vscode-gateway`

Do not create these until the workflows repeat at least a few times.

## Working Style

When multiple model/agent roles are available, use a split workflow:

- high-reasoning model for planning, architecture, risk analysis, and review
- implementation-focused model for edits, tests, and patches
- one focused implementation task at a time
- review after each meaningful implementation step

This should remain a preference, not a hard dependency. The project must still be workable when only one model is available.
