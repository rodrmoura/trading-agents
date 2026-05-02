---
description: "Durably wrap a meaningful session by validating changes, updating current-truth and historical handoff docs, then committing and pushing approved work to GitHub."
name: "Session Wrap"
argument-hint: "wrap | handoff | final | commit-and-push"
agent: "Reasoning Engineer"
model: "GPT 5.5"
---

Run the `/session-wrap` contract from `docs/WORKFLOW_HELPERS.md` and `.github/skills/session-wrap/SKILL.md`.

Update current truth before historical narrative. Prepare an explicit commit/push scope; after user approval, stage only approved files, commit, and push the current branch to `origin`. Never include secrets, generated artifacts, or unrelated changes, and never push to `upstream`.
