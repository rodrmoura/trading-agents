# Session Lifecycle Skills

Use these slash commands as a lifecycle, not as interchangeable handoff tools.

| Command | Use When | Pulls From GitHub | Edits Markdown | Runs Full Validation | Commits | Pushes To GitHub |
| --- | --- | --- | --- | --- | --- | --- |
| `/session-resume` | Starting or resuming a session | Yes, only when safe | No | No | No | No |
| `/state-sync` | Mid-session checkpoint or pre-compaction preservation | No | Yes, focused | Markdown checks only | No | No |
| `/session-wrap` | Finishing a completed session | No, unless explicitly needed and safe | Yes, comprehensive | Yes, scoped to changes | Yes, only after validation and user intent is clear | Optional; only when explicitly desired for this repo/fork |

## Decision Rules

- Use `/session-resume` to fetch remote state safely, read project markdown, and recommend next steps before implementation.
- Use `/state-sync` when work is in progress and repository markdown needs enough context for a future session to continue.
- Use `/session-wrap` when the session is complete and the work should be validated, staged, and committed. Push only when the user explicitly wants the branch updated remotely.

## Safety Rules

- Never print or commit API keys, local VS Code gateway tokens, `.env`, `.env.*`, raw credentials, customer data, or generated local caches.
- Never merge, rebase, stash, reset, revert, or overwrite user work without explicit user approval.
- Never force-push from `/session-wrap`.
- Treat `tradingagents/` and `cli/` as upstream-derived code. Keep patches narrow and documented.
- Keep `PROJECT-GUIDE.md` as the project and architecture source of truth, `TODO.md` as the active backlog, and `DOCS-GOVERNANCE.md` as the documentation routing guide.
