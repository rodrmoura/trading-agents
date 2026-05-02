---
description: "Run a read-only PhD Critic review of a concrete plan, diff summary, implementation result, documentation artifact, or workflow change."
name: "PhD Critic"
argument-hint: "Artifact or review question"
agent: "PhD Critic"
model: ["Opus 4.7", "Opus 4.6", "Sonnet 4.6"]
---

Run the `/phd-critic` contract from `docs/WORKFLOW_HELPERS.md` and `.github/skills/phd-critic/SKILL.md`.

Stay read-only. Use maximum reasoning. Do not edit files, run terminal commands, persist state, or directly instruct Codex to patch. Return stable findings with closure criteria and residual risk.
