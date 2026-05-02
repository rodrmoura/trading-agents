---
name: session-resume
description: "Use when: starting or resuming a session, restoring current project truth from ACTIVE_STATE and PROVEN_KNOWLEDGE, checking recent git history, and recommending next actions without editing files."
argument-hint: "start | resume | continue"
user-invocable: true
disable-model-invocation: false
---

# Session Resume

Canonical contract: `docs/WORKFLOW_HELPERS.md` under `Session Resume`.

## Procedure

1. Read `docs/repo_state/ACTIVE_STATE.md`.
2. Read `docs/repo_state/PROVEN_KNOWLEDGE.md`.
3. Read `git log --oneline -5` if available.
4. Follow ACTIVE_STATE resume pointers only if relevant.
5. Read `docs/ROADMAP.md` only if priority is unclear or the user asks what is next.
6. Do not read the whole changelog by default.
7. Do not read session capsules by default unless ACTIVE_STATE points to one.
8. Summarize under 20 lines: current focus, blockers, recent evidence, next actions, and deeper context intentionally skipped.

## Rules

- If ACTIVE_STATE is missing or stale, say so explicitly.
- If PROVEN_KNOWLEDGE is contradicted by fresh repo evidence, mark the prior as contested.
- Do not edit, persist state, commit, push, merge, rebase, reset, stash, or run full validation during resume unless the user explicitly asks.
