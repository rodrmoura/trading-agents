---
name: session-wrap
description: "Use when: durable end-of-session handoff is needed after code, docs, decisions, experiments, validations, or complex work changed; validates scope, updates current truth, then commits and pushes approved work to GitHub."
argument-hint: "wrap | handoff | final | commit-and-push"
user-invocable: true
disable-model-invocation: false
---

# Session Wrap

Canonical contract: `docs/WORKFLOW_HELPERS.md` under `Session Wrap`.

## Procedure

1. Scope worktree and separate intended changes from unrelated or generated drift.
2. Validate intended changes.
3. Update current truth first:
   - `docs/repo_state/ACTIVE_STATE.md`
   - `docs/repo_state/PROVEN_KNOWLEDGE.md`
4. Update role-specific docs only as needed:
   - `docs/DECISIONS.md`
   - `docs/EXPERIMENT_LOG.md`
   - `docs/ROADMAP.md`
   - `README.md`
5. Update historical handoff docs only as needed:
   - `docs/CHANGELOG.md`
   - `docs/session_capsules/S<N>_capsule.md`
6. Confirm remaining changes are intentional.
7. Prepare an explicit GitHub persistence plan:
   - current branch
   - push remote, normally `origin`
   - exact files to stage
   - files intentionally excluded
   - commit message
8. If commit and push approval is missing, stop with the ready persistence plan and ask for approval.
9. After approval, stage only the approved files, commit them, push the current branch to `origin`, then report the commit hash and push target.
10. Report what was updated, committed, pushed, and intentionally skipped.

## Rules

- ACTIVE_STATE matters more than polished narrative if interrupted.
- Do not commit or push until the user has approved the commit/push scope for the wrap.
- Push only to `origin` unless the user explicitly names another safe remote.
- Never push to `upstream`.
- Do not include unrelated changes.
- Do not include secrets, local tokens, credentials, generated caches, local environments, build output, or ignored artifacts.
- Do not branch, reset, revert, merge, rebase, or stash unless explicitly asked.
