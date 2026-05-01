---
name: state-sync
description: "Use when: lightweight checkpointing of in-progress session state, preparing for context compaction, preserving progress before handoff, or updating project markdown with what changed, what is blocked, and what should happen next. Updates docs and guidance as needed. Does not pull, fully validate, commit, or push."
argument-hint: "pre-compact | checkpoint | preserve"
user-invocable: true
disable-model-invocation: false
---

# State Sync

Use this skill to persist the current working state into repository markdown before a session is compacted, handed off, paused, or resumed later.

The goal is to make the next session able to continue from the repository itself, not from fragile chat memory.

This is the lightweight checkpoint workflow. For starting a session, use `/session-resume`; for final session closure with validation and an optional commit, use `/session-wrap`. See [../README.md](../README.md) for the lifecycle matrix.

## When To Use

- The user invokes `/state-sync`.
- The user asks to preserve state, create a checkpoint, or prepare for compaction.
- A meaningful implementation, setup, governance, architecture, VS Code gateway, prompt, skill, or agent-runtime decision has occurred, but the session is not ready for final closure.
- The working tree has important uncommitted changes that future work needs to understand.
- The current conversation has discovered a blocker, decision, risk, or next step that should survive chat compaction.

## Core Rule

Update the smallest set of related markdown files needed to preserve useful state. Do not dump a transcript. Keep it concise, factual, and actionable.

Do not commit work as part of `/state-sync`.

Do not pull from GitHub, stage files, stash work, or run the full validation suite as part of `/state-sync` unless the user explicitly asks.

Never write API keys, local VS Code gateway tokens, `.env` values, credentials, customer data, or generated local caches into markdown.

## Non-Goals

- Do not start a new session from remote state; use `/session-resume`.
- Do not finalize or commit work; use `/session-wrap`.
- Do not rewrite broad documentation when a concise checkpoint is enough.
- Do not mark work complete unless the relevant verification already passed.

## State Gathering

Before editing, inspect enough context to avoid stale notes:

1. Check `git status --short` and relevant diffs.
2. Review [docs/README.md](../../../docs/README.md) for documentation routing.
3. Review [PROJECT-GUIDE.md](../../../PROJECT-GUIDE.md) when product direction, project boundaries, or architecture changed.
4. Review [TODO.md](../../../TODO.md) when active task state changed.
5. Review [DOCS-GOVERNANCE.md](../../../DOCS-GOVERNANCE.md) when documentation routing changed.
6. Review [docs/architecture/code-governance.md](../../../docs/architecture/code-governance.md) when upstream boundaries, folder ownership, or sync policy changed.
7. Review [docs/guidance/copilot-and-skills.md](../../../docs/guidance/copilot-and-skills.md) when prompts, skills, or Copilot behavior changed.
8. Review relevant ADRs in `docs/decisions/` when a durable decision was made.
9. Check validation results from the current session: diagnostics, `git diff --check`, tests, builds, or known failures.

## Markdown Routing

Update files according to the type of state being preserved:

- `PROJECT-GUIDE.md`: project direction, two-project roadmap, frontend/runtime vision, and durable architecture shape.
- `TODO.md`: active done, partial, blocked, and next task state.
- `DOCS-GOVERNANCE.md`: documentation ownership, routing, update triggers, and drift control.
- `PROJECT-CHANGELOG.md`: notable local platform changes under `[Unreleased]`.
- `docs/architecture/project-vision.md`: supporting architecture details.
- `docs/architecture/code-governance.md`: upstream-derived code boundaries, folder ownership, dependency direction, and upstream sync rules.
- `docs/guidance/copilot-and-skills.md`: Copilot instructions, prompt files, skills, slash-command lifecycle, and imported-guidance process.
- `docs/decisions/*.md`: architecture decisions with context, decision, consequences, and open questions.
- `.github/copilot-instructions.md`: persistent repo-level agent behavior.
- `.github/skills/README.md` and `.github/skills/*/SKILL.md`: slash-command lifecycle behavior.
- `README.md`: only when public setup or project usage changes.
- `CHANGELOG.md`: avoid changing upstream project changelog for our local governance work unless we deliberately contribute upstream.

If a fact belongs in more than one file, make one file the source of truth and link or summarize elsewhere. Avoid duplicate prose that will drift.

## Procedure

1. Identify the sync purpose from the slash argument or user request: pre-compact, handoff, checkpoint, or blocker preservation.
2. Summarize the active state in your own notes first:
   - What changed?
   - What was verified?
   - What is still running locally?
   - What remains blocked or pending?
   - What should the next session do first?
3. Choose the markdown files from the routing list.
4. Edit concise bullets or short sections.
5. Keep task state honest:
   - Mark done only after verification.
   - Mark partial when implementation exists but readiness is incomplete.
   - Add blockers with the exact missing dependency or decision.
6. Validate touched markdown with diagnostics and `git diff --check`.
7. Report which files were updated and the key persisted state.

## Handoff Content Checklist

For a pre-compact or handoff sync, make sure the repository captures:

- New files or config that future sessions must not overlook.
- Current validation results and warnings that still matter.
- Unresolved risks such as upstream divergence, gateway API uncertainty, VS Code model API limitations, tool-calling design, prompt provenance, or generic-runtime overreach.
- The next concrete task, not a vague plan.

## Project-Specific Guardrails

- TradingAgents is the first integrated ecosystem, not the foundation of all generic platform code.
- Keep generic packages free of finance assumptions.
- Keep upstream-derived patches narrow and documented.
- Do not store secrets, gateway tokens, API keys, generated caches, or local model credentials in docs.

## Final Response Pattern

When done, respond briefly with:

- Files updated.
- State preserved.
- Validation performed.
- Next recommended action.
