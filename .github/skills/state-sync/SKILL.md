---
name: state-sync
description: "Use when: minimal current-truth refresh before compaction or handoff, updating ACTIVE_STATE and optionally PROVEN_KNOWLEDGE without historical wrap, commits, or broad validation."
argument-hint: "sync | checkpoint | pre-compact"
user-invocable: true
disable-model-invocation: false
---

# State Sync

Canonical contract: `docs/WORKFLOW_HELPERS.md` under `State Sync`.

## Use When

- Only current focus, blockers, next actions, or proven priors changed.
- The session needs a lightweight handoff, not a durable historical record.

## Do Not Use When

- Code changes still need validation.
- Decisions changed materially.
- Experiment, benchmark, or validation results changed.
- A historical session record is needed.
- README or operator docs changed.
- The session needs to be recoverable historically.

## Procedure

1. Scope current changes.
2. Update `docs/repo_state/ACTIVE_STATE.md` if focus, blockers, evidence, or next actions changed.
3. Update `docs/repo_state/PROVEN_KNOWLEDGE.md` only if durable priors changed.
4. Do not update CHANGELOG, DECISIONS, EXPERIMENT_LOG, or README unless their role truly changed.
5. If broader docs are needed, switch to `/session-wrap`.
