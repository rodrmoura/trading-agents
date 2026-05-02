# Decisions

This file owns final governance and workflow decisions with rollback criteria. Architecture ADRs may remain in `docs/decisions/`; do not duplicate their full content here.

## Decision Log

### 2026-05-01: Repository-Local AI Governance Roles

- Problem: The repository needs durable ownership boundaries for reasoning, implementation, and critique.
- Decision: GPT owns reasoning/planning/review, Codex owns code-writing implementation from ready ledgers, and PhD Critic owns read-only devil's-advocate review.
- Evidence: User requested this ownership model explicitly during governance bootstrap.
- Rollback: Revisit only if the environment cannot support distinct agent/prompt routes or if the workflow blocks normal development.

### 2026-05-01: Current-Truth Documentation System

- Problem: Session handoff needs current truth without reading full history by default.
- Decision: `ACTIVE_STATE` and `PROVEN_KNOWLEDGE` are the default resume sources; `CHANGELOG` and session capsules are historical and read only when needed.
- Evidence: User requested minimal state sync, resume, wrap, and no duplicate truth.
- Rollback: Revisit if future sessions cannot resume accurately from the current-truth files.

### 2026-05-02: Session Wrap Includes Approved GitHub Persistence

- Problem: Durable session wrap should not stop at local documentation updates when the user expects completed work to be saved to GitHub.
- Decision: `/session-wrap` validates and updates current-truth/history docs first, then prepares an explicit persistence plan; after user approval, it stages only approved files, commits them, and pushes the current branch to `origin`.
- Evidence: User approved G0 with the condition that the session-wrap skill should commit to GitHub.
- Rollback: Revisit if automatic wrap persistence risks unrelated work, generated artifacts, secrets, or accidental pushes.

## Template

- Date:
- Problem:
- Decision:
- Evidence:
- Rollback:
