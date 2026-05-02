# Planning

This folder turns the project guide and roadmap into execution-ready work.

Use these files in this order:

1. [Execution Plan](execution-plan.md) - phases, objectives, dependencies, outputs, and gates.
2. [Gate Checklist](gates.md) - pass/fail criteria for each milestone gate.
3. [Codex Task Packets](codex-task-packets.md) - implementation tasks written so a coding model can execute with minimal interpretation.
4. [Documentation Map](documentation-map.md) - what each document owns and when to update it.

## Rules

- `PROJECT-GUIDE.md` remains the source of truth for product and architecture direction.
- `docs/architecture/roadmap.md` remains the milestone overview.
- Planning docs own execution detail, gates, dependencies, and model-ready task packets.
- `TODO.md` tracks active task state; do not duplicate the full execution plan there.
- Use `docs/WORKFLOW_HELPERS.md` as the canonical governance contract for planning, ledgers, implementation handoff, and review.
- Use Reasoning Engineer to convert project task packets into ready `Coding-Agent Task Ledger` items before Codex Coding Engineer implements them.
