---
applyTo: "docs/**/*.md"
---

# Documentation System

Use `docs/WORKFLOW_HELPERS.md` as the canonical governance contract.

Rules:

- One fact gets one home.
- Do not duplicate the same fact across multiple docs unless another doc is only a pointer.
- `docs/repo_state/ACTIVE_STATE.md` owns current focus, blockers, evidence snapshot, next actions, and resume pointers.
- `docs/repo_state/PROVEN_KNOWLEDGE.md` owns durable current priors, known constraints, and reopen rules.
- `docs/DECISIONS.md` owns final governance and workflow decisions with rollback criteria.
- `docs/EXPERIMENT_LOG.md` owns measured experiment, validation, or benchmark outcomes.
- `docs/CHANGELOG.md` owns historical timeline between wraps. It is not default resume input.
- `docs/session_capsules/*.md` owns dense long-form handoff for complex sessions.
- `docs/ROADMAP.md` owns medium-term priorities and parked work.
- `docs/WORKFLOW_HELPERS.md` owns helper routing, model ownership, ledger template, session lifecycle, and review workflow.
- `README.md` should stay shallow and operator-facing.
- Prefer pointers to commits, files, artifacts, and commands over pasted raw output.
- Do not create competing current-truth stores.
- If docs disagree, resolve current truth first in `ACTIVE_STATE` and `PROVEN_KNOWLEDGE`.
