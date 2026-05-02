# Workflow Skills

Canonical workflow rules live in `docs/WORKFLOW_HELPERS.md`. Skills are slash-command wrappers around that contract.

| Command | Canonical Use | Edits Files | Runs Commands | Persists State |
| --- | --- | --- | --- | --- |
| `/session-resume` | Restore current truth at chat start | No | Minimal git history only when available | No |
| `/state-sync` | Minimal current-truth refresh before compaction/handoff | Yes, current-truth docs only | No broad validation | Yes, current truth only |
| `/session-wrap` | Durable closure after meaningful work | Yes, as needed | Scoped validation plus approved commit/push | Yes, current truth, history, and approved GitHub persistence |
| `/phd-critic` | Read-only devil's-advocate review | No | No | No |
| `/phd-quality-gate` | Full readiness workflow before commit/deploy/major handoff | May convert accepted findings into plans/ledgers | Yes, relevant checks | Yes, if current truth changed |

## Ownership Rules

- GPT owns reasoning, planning, architecture, documentation governance, task shaping, and review.
- Codex owns implementation from one ready `Coding-Agent Task Ledger`.
- PhD Critic is read-only and never instructs Codex directly.
- Reasoning route: GPT 5.5, high or xhigh reasoning depending on complexity.
- Coding route: Codex 5.3, high or xhigh reasoning depending on complexity.
- Critic route: Opus 4.7, falling back to Opus 4.6 or Sonnet 4.6. Always use maximum reasoning for critic work and inspections.
