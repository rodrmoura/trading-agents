# Custom Agents

Custom agents are callable workspace agents for focused work.

## Available Agents

| Agent | File | Use When |
| --- | --- | --- |
| Reasoning Engineer | `reasoning-engineer.agent.md` | GPT-owned planning, architecture, documentation governance, ledgers, and review coordination |
| Codex Coding Engineer | `codex-coding-engineer.agent.md` | Codex-owned implementation of exactly one ready Coding-Agent Task Ledger |
| PhD Critic | `phd-critic.agent.md` | Read-only devil's-advocate review of plans, implementation results, docs, and workflow changes |

## Usage

Open VS Code at the repository root, then select the custom agent from chat or invoke it as a subagent when supported.

Recommended prompt shape:

```text
Use Reasoning Engineer to create a ready Coding-Agent Task Ledger, then use Codex Coding Engineer for that ledger only.
```

The canonical workflow contract lives in `docs/WORKFLOW_HELPERS.md`. Current routes are GPT 5.5 for Reasoning Engineer, Codex 5.3 for Codex Coding Engineer, and Opus 4.7 for PhD Critic with Opus 4.6 and Sonnet 4.6 fallbacks.
