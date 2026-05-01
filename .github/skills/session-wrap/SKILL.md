---
name: session-wrap
description: "Use when: finishing a completed session, finalizing work, updating relevant markdown state, running scoped validation, reviewing diffs, staging intended files, and creating a git commit when the user wants durable closure. Deeper than state-sync; use state-sync for lightweight checkpoints and session-wrap for final closure."
argument-hint: "finalize | commit | handoff | release-note"
user-invocable: true
disable-model-invocation: false
---

# Session Wrap

Use this skill to finish a session in a durable, reviewable state. It goes beyond `/state-sync`: it performs a full state update, validates the changed scope, reviews the final diff, and creates a commit when the user wants completed work committed.

Invoking `/session-wrap` is explicit permission to prepare a commit for completed work after validation and final review. Push only when the user explicitly asks to push or the project has adopted push-on-wrap as a documented policy. Do not use this skill for starting a session or mid-session checkpoints; use `/session-resume` or `/state-sync` instead. See [../README.md](../README.md) for the lifecycle matrix.

## When To Use

- The user invokes `/session-wrap`.
- The user asks to finish, wrap, close out, finalize, commit, or create an end-of-session closure.
- Work is believed complete and should be left in a committed state.
- A broad session changed code, docs, local setup, governance, prompts, skills, gateway code, runtime code, tests, or architecture.

## Relationship To State Sync

- `/state-sync` is lightweight: preserve current state in markdown so a future session can resume, even if work is incomplete.
- `/session-wrap` is comprehensive: finish the session, update relevant markdown, run validation, stage only intended changes, commit if appropriate, and report closure status.
- If `/session-wrap` discovers incomplete work, blockers, failing checks, or ambiguous unrelated changes, update markdown honestly and do not commit until the issue is resolved or the user explicitly approves a narrowed commit.

## Safety Rules

- Never commit `.env`, `.env.*`, API keys, local VS Code gateway tokens, credentials, generated local caches, customer data, or build artifacts.
- Never revert user changes unless explicitly requested.
- Include only intended files in the commit. If unrelated changes are present, leave them unstaged or ask for direction when separation is unclear.
- If validation fails because of pre-existing unrelated issues, document the failure and ask before committing.
- Do not push if validation fails, the commit fails, secrets are staged, intended changes are unclear, the branch has no upstream, the push is rejected, or the remote has diverged.
- Do not force-push, merge, rebase, stash, reset, or otherwise rewrite history unless the user explicitly asks in a separate instruction.

## Non-Goals

- Do not pull fresh remote code as part of wrapping unless the user explicitly asks and the worktree is safe.
- Do not commit unrelated local changes.
- Do not commit or push when required checks fail, secrets are staged, or intended changes are unclear.
- Do not force-push unless the user explicitly asks in a separate instruction.
- Do not use this as a lightweight progress checkpoint; use `/state-sync`.

## Required State Gathering

Before editing or committing:

1. Run `git status --short`.
2. Inspect tracked and untracked changes relevant to the session.
3. Review docs changed or implicated by the session.
4. Check whether local services are running if the session involved local environment setup.
5. Identify secrets or generated files that must remain untracked.

## Markdown Update Requirements

Update every relevant markdown file before committing:

- `PROJECT-GUIDE.md`: required when roadmap, product direction, platform architecture, or frontend/runtime goals changed.
- `TODO.md`: required when task state changed.
- `DOCS-GOVERNANCE.md`: required when documentation ownership, routing, lifecycle commands, update triggers, or drift-control rules changed.
- `PROJECT-CHANGELOG.md`: required for notable local platform changes.
- `docs/architecture/project-vision.md`: required when supporting architecture details changed.
- `docs/architecture/code-governance.md`: required when ownership boundaries, upstream sync policy, or folder responsibilities changed.
- `docs/guidance/copilot-and-skills.md`: required when prompts, skills, slash commands, or imported-guidance policy changed.
- `docs/decisions/*.md`: required when a durable architecture or product decision needs rationale and consequences.
- `.github/copilot-instructions.md`: required when future agent behavior should change.
- `.github/skills/*/SKILL.md` and `.github/skills/README.md`: required when lifecycle command behavior changes.
- `README.md`: required when user-facing setup or usage changes.
- `CHANGELOG.md`: avoid changing upstream project changelog for our local governance work unless we deliberately contribute upstream.

Prefer concise, source-of-truth updates. Do not duplicate long prose across files.

## Validation Checklist

Choose checks based on changed files and risk.

For documentation-only sessions, run:

1. VS Code diagnostics on touched files when available.
2. `git diff --check`.
3. A non-ASCII scan if the project expects ASCII docs.

For Python code changes, also consider:

1. targeted tests with `pytest`
2. full test suite when shared behavior changes
3. import or smoke checks for touched modules

For VS Code extension work, also consider:

1. package manager install/build/test commands for the extension package
2. TypeScript checks
3. manual gateway smoke tests for model listing, auth, streaming, cancellation, and error handling

Do not mark tasks done unless the relevant validation passed or the limitation is documented.

## Commit Procedure

1. Review final `git status --short` and relevant diffs.
2. Run `git diff --name-only` and identify the intended commit scope.
3. Ensure ignored local files such as `.env`, `.env.*`, virtual environments, caches, build outputs, and local gateway tokens are not staged.
4. Stage only intended changes with explicit paths.
5. Run `git diff --cached --name-only`, `git diff --cached --stat`, and `git diff --cached --check`.
6. Inspect staged paths for forbidden files or secrets before committing.
7. Commit with a concise message that matches the work, for example:
   - `docs: add session lifecycle skills`
   - `docs: record vscode gateway architecture`
   - `feat: add vscode llm gateway provider`
8. Capture the commit SHA with `git rev-parse --short HEAD`.

If the commit fails, inspect the failure, fix in-scope issues, rerun validation as needed, and retry. If failure is out of scope or requires a decision, stop and report the blocker.

## Push Procedure

Push only when the user explicitly asks or a documented project policy says `/session-wrap` includes push.

When pushing:

1. Confirm the current branch has an upstream, for example with `git rev-parse --abbrev-ref --symbolic-full-name @{u}`.
2. Review `git status --short --branch` to confirm the branch is ahead only by the completed commit and there are no unclear staged changes.
3. Push with a normal non-destructive command such as `git push`.
4. If the branch has no upstream, the push is rejected, the remote has diverged, or any blocker appears, stop and report the blocker. Do not force-push, merge, rebase, stash, reset, or rewrite history unless the user explicitly asks in a separate instruction.

## Final Report

When complete, report:

- Markdown files updated.
- Validation commands run and result.
- Commit message and short SHA if committed.
- Push result if pushed.
- Any services still running.
- Remaining risks or next recommended task.

Keep the final report concise and do not paste secrets.
