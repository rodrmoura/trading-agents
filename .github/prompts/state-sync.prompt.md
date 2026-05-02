---
description: "Perform a minimal current-truth sync before compaction or handoff when no full historical wrap is needed."
name: "State Sync"
argument-hint: "sync | checkpoint | pre-compact"
agent: "Reasoning Engineer"
model: "GPT 5.5"
---

Run the `/state-sync` contract from `docs/WORKFLOW_HELPERS.md` and `.github/skills/state-sync/SKILL.md`.

Update only `docs/repo_state/ACTIVE_STATE.md` and, when durable priors changed, `docs/repo_state/PROVEN_KNOWLEDGE.md`. Switch to `/session-wrap` if broader docs are required.
