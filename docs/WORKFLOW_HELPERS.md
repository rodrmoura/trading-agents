# Workflow Helpers

This file is the canonical home for repository-local AI-agent governance. Agents, prompts, skills, and instructions should point here instead of duplicating these rules.

## Minimal Session Lifecycle

- Use `/session-resume` to restore current truth at the start of a chat.
- Use `/state-sync` for a minimal current-truth refresh before compaction or handoff.
- Use `/session-wrap` for durable closure after meaningful code, docs, decisions, validation, or experiments, including GitHub commit/push once the user approves the persistence scope.
- Use `/phd-critic` for read-only devil's-advocate review.
- Use `/phd-quality-gate` for readiness review that may combine critique, checks, fixes, and persistence.

## Model Ownership Policy

- GPT owns reasoning, planning, architecture, debugging strategy, research, documentation governance, task shaping, and review.
- Codex owns code-writing implementation only after GPT has produced a ready `Coding-Agent Task Ledger`.
- PhD Critic owns read-only devil's-advocate review.
- Code includes source files, tests, executable scripts, runtime-consumed config, schema or migration files, CI files, package/build config, and agent/prompt/skill metadata that changes routing behavior.
- Standalone documentation prose, workflow prose, planning docs, and governance text stay with GPT unless explicitly supporting a code implementation ledger.
- Codex must not receive vague implementation requests.
- Codex receives one bounded task packet at a time.
- If the desired GPT, Codex, or critic model route is unavailable, stop and ask instead of silently falling back.
- Reasoning route: GPT 5.5. Use high reasoning by default and xhigh reasoning for ambiguous, architecture-heavy, high-risk, cross-repository, security-sensitive, or broad work.
- Coding route: Codex 5.3. Use high reasoning for routine implementation and xhigh reasoning for complex, high-risk, cross-module, security-sensitive, framework-level, or routing-sensitive implementation.
- Critic route: Opus 4.7. Fallback routes, in order, are Opus 4.6 and Sonnet 4.6. Always use maximum reasoning for critic work, inspections, audits, quality gates, and implementation reviews.

Model routing applies to custom agents, prompts, skills, or future invocations where supported. It does not hot-swap the model of an already-running top-level chat.

## Agent Routing

Use these owners by default:

- `Reasoning Engineer`: GPT-owned planning, architecture, documentation governance, implementation ledgers, and review coordination.
- `Codex Coding Engineer`: Codex-owned implementation of exactly one ready ledger item at a time.
- `PhD Critic`: read-only devil's-advocate review of plans, implementation results, docs, workflow changes, or current-session changes.

If a request crosses roles, GPT must split it into bounded work before Codex edits anything.

## Plan Critic Gate

Before any substantive non-fast-path code implementation handoff:

1. GPT produces a plan and a ready `Coding-Agent Task Ledger`.
2. PhD Critic reviews the plan read-only.
3. GPT decides whether to accept, reject, or remediate the critic findings.
4. Only then may Codex implement the ledger.

Skip this gate only for:

- plain status or resume requests
- direct answers with no implementation
- fast-path mechanical edits
- explicit user request to skip review

Fast-path mechanical edits are limited to all of the following:

- one file
- mechanically obvious typo, wording, formatting, or comment cleanup
- no runtime/config/schema/test/workflow/current-truth surface
- no behavior change
- no ambiguity

## Codex Implementation Review

After Codex implements a ledger item:

1. Codex reports `needs_review`.
2. GPT or the user invokes PhD Critic with the phrase `Codex implementation review`.
3. The review includes the original canonical `Coding-Agent Task Ledger`, Codex final report, and diff or changed-file summary.
4. PhD Critic leads with:
   - `Approval status`: Approved / Approved with non-blocking follow-ups / Needs changes / Blocked
   - `Critical issues`: None or stable finding IDs
   - `Suggested next patch (route via GPT)`: None or one focused patch recommendation
   - `Verification steps`: commands, checks, or missing evidence
5. If changes are needed, GPT converts accepted findings into one new focused ledger for Codex.
6. Mark the task completed only after review approval and verification.

PhD Critic findings are recommendations to GPT, not direct Codex instructions.

## Coding-Agent Task Ledger

```text
Task ID:

Status: proposed / ready_for_coding / blocked / needs_review / completed

Route:

Reasoning effort: high by default; maximum/highest available for risky work

Task:

Context:
- Project:
- Current behavior:
- Desired behavior:
- Relevant files:
- Related dependencies or assumptions:

Instructions:
- Implement only this task.
- Keep changes minimal.
- Follow existing project style.
- Do not refactor unrelated code.
- Do not rename files, public APIs, schemas, dependencies, commands, or config keys unless explicitly required.
- Add or update tests only when existing patterns or the task justify them.

Acceptance criteria:
- Specific measurable outcome.
- Specific measurable outcome.
- Existing tests pass where applicable.
- No unrelated files changed.

Verification:
- Run:
  - exact test, lint, build, typecheck, smoke command, or reason no command applies

Do not change:
- protected files, APIs, schemas, commands, configs, docs, generated artifacts, or behaviors outside scope

Final report:
1. Files changed
2. Summary of changes
3. Tests run
4. Remaining concerns
```

Ledger discipline:

- One ledger item equals one focused coding task.
- Split broad work before handoff.
- Mark blocked items with the missing decision, data, artifact, command, or approval.
- If a ledger must survive handoff or compaction, mirror only active ready/blocked items into `docs/repo_state/ACTIVE_STATE.md` or a session capsule. Do not create a parallel task system unless explicitly requested.

## Documentation Governance

- One fact gets one home.
- Do not duplicate the same fact across multiple docs unless another doc is only a pointer.
- `docs/repo_state/ACTIVE_STATE.md` owns current focus, blockers, evidence snapshot, next actions, and resume pointers.
- `docs/repo_state/PROVEN_KNOWLEDGE.md` owns durable current priors, known constraints, and reopen rules.
- `docs/DECISIONS.md` owns final governance and workflow decisions with rollback criteria.
- `docs/decisions/` may continue to hold architecture decision records; do not duplicate long ADR content in `docs/DECISIONS.md`.
- `docs/EXPERIMENT_LOG.md` owns measured experiment, validation, or benchmark outcomes.
- `docs/CHANGELOG.md` owns historical timeline between wraps. It is not default resume input.
- `docs/session_capsules/*.md` owns dense long-form handoff for complex sessions.
- `docs/ROADMAP.md` owns medium-term priorities and parked work.
- `docs/WORKFLOW_HELPERS.md` owns helper routing, model ownership, ledger template, session lifecycle, and review workflow.
- `README.md` should stay shallow and operator-facing.
- Prefer pointers to commits, files, artifacts, and commands over pasted raw output.
- Do not create competing current-truth stores.
- If docs disagree, resolve current truth first in `ACTIVE_STATE` and `PROVEN_KNOWLEDGE`.

## Session Resume

Purpose: start every new chat by restoring current project truth quickly.

Procedure:

1. Read `docs/repo_state/ACTIVE_STATE.md`.
2. Read `docs/repo_state/PROVEN_KNOWLEDGE.md`.
3. Read `git log --oneline -5` if available.
4. Follow ACTIVE_STATE resume pointers only if relevant.
5. Read `docs/ROADMAP.md` only if priority is unclear or the user asks what is next.
6. Do not read the whole changelog by default.
7. Do not read session capsules by default unless ACTIVE_STATE points to one.
8. Summarize under 20 lines:
   - current focus
   - blockers
   - relevant recent evidence
   - next actions
   - deeper context intentionally skipped

Rules:

- If ACTIVE_STATE is missing or stale, say so explicitly.
- If PROVEN_KNOWLEDGE is contradicted by fresh repo evidence, mark the prior as contested rather than pretending it is settled.
- Do not turn resume into a full historical audit unless the user asks.

## State Sync

Purpose: minimal current-truth refresh before compaction or handoff when no full historical wrap is needed.

Use when only current focus, blockers, next actions, or proven priors changed.

Do not use when:

- code changes still need validation
- decisions changed materially
- experiment, benchmark, or validation results changed
- a historical session record is needed
- README or operator docs changed
- the session needs to be recoverable historically

Procedure:

1. Scope current changes.
2. Update `docs/repo_state/ACTIVE_STATE.md` if focus, blockers, evidence, or next actions changed.
3. Update `docs/repo_state/PROVEN_KNOWLEDGE.md` only if durable priors changed.
4. Do not update CHANGELOG, DECISIONS, EXPERIMENT_LOG, or README unless their role truly changed.
5. If broader docs are needed, switch to `/session-wrap`.

Output:

1. Current truth updated
2. Files synced
3. What was intentionally not updated
4. Residual risk

## Session Wrap

Purpose: durable handoff at the end of a meaningful session or before compaction, followed by GitHub persistence for approved work.

Use when:

- code, docs, or decisions changed
- experiments, benchmarks, validations, or important checks produced results
- current truth changed and historical recovery matters
- the session was complex enough that future reconstruction would be expensive

Procedure:

1. Scope worktree and separate intended changes from unrelated or generated drift.
2. Validate intended changes.
3. Update current truth first:
   - `docs/repo_state/ACTIVE_STATE.md`
   - `docs/repo_state/PROVEN_KNOWLEDGE.md`
4. Update role-specific docs only as needed:
   - `docs/DECISIONS.md`
   - `docs/EXPERIMENT_LOG.md`
   - `docs/ROADMAP.md`
   - `README.md`
5. Update historical handoff docs only as needed:
   - `docs/CHANGELOG.md`
   - `docs/session_capsules/S<N>_capsule.md`
6. Confirm remaining changes are intentional.
7. Prepare an explicit GitHub persistence plan:
   - current branch
   - push remote, normally `origin`
   - exact files to stage
   - files intentionally excluded
   - commit message
8. If commit and push approval is missing, stop with the ready persistence plan and ask for approval.
9. After approval, stage only the approved files, commit them, push the current branch to `origin`, then report the commit hash and push target.
10. Report what was updated, committed, pushed, and intentionally skipped.

Core rule: ACTIVE_STATE matters more than polished narrative if interrupted.

Git rules:

- Never include secrets, local tokens, credentials, generated caches, local environments, build output, or ignored artifacts.
- Never include unrelated changes.
- Never push to `upstream`.
- Do not branch, reset, revert, merge, rebase, or stash unless explicitly asked.

## PhD Critic

Purpose: run a read-only, falsifiable devil's-advocate review of a concrete plan, code surface, implementation result, documentation artifact, workflow change, or current-session change.

Rules:

- Stay read-only.
- Do not edit files.
- Do not run terminal commands.
- Do not persist state.
- Do not perform state-sync or session-wrap.
- Do not directly instruct Codex to patch.
- Treat latest user request as authoritative.
- Identify the work track before reviewing.
- Use an assumption ledger before findings.
- Classify evidence as `OBSERVED`, `INFERRED`, `HYPOTHESIS`, or `UNKNOWN`.
- Return findings with stable IDs.

Work tracks:

- `workflow-customization`: agents, prompts, skills, hooks, slash routing, metadata tests, workflow helper docs
- `knowledge-docs`: repo-state docs, decisions, experiment logs, changelog, roadmap, session capsules
- `code`: application source, tests, scripts, config, schema, CI, package/build behavior
- `release-ops`: deploy, release, packaging, environment, scheduled tasks, operational commands
- `tests-tooling`: test harnesses, lint/typecheck/build commands, CI helpers, metadata validators

Finding contract:

- Stable ID: `F1`, `F2`, etc.
- Work track
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- Confidence when uncertainty matters
- Evidence with evidence ladder label
- Risk in operator or system terms
- Falsification condition
- Closure criteria
- Reopen condition

If no real issues are found, say so explicitly and still report residual risk.

## PhD Quality Gate

Purpose: full readiness review workflow that may combine read-only critique, checks, fixes, re-runs, and persistence.

Use when:

- before commit, deploy, release, major refactor, or compaction
- the user asks to sanity-check everything
- the user asks to make the current work better
- the user asks for a full review rather than a read-only critic pass

Rules:

1. Start with PhD Critic read-only review.
2. Convert accepted findings into GPT-owned plans or Codex ledgers.
3. Run relevant tests/checks where tools allow.
4. Close or explicitly defer findings.
5. Finish with `/state-sync` or `/session-wrap` when current truth changed.

Validation strength labels:

- `V0 read`: read-only review
- `V1 static`: static checks, grep, metadata validation, syntax checks
- `V2 targeted`: focused tests or smoke checks
- `V3 integration`: broader integration tests
- `V4 runtime`: real runtime validation
- `V5 production`: production or release-environment validation

## Task Triage

A request is gated if it:

- may edit more than one file
- creates, deletes, renames, or moves files
- touches runtime behavior, tests, CI, build, config, schema, docs-current-truth, workflows, commands, deployment, review, audit, or failed-test behavior
- asks for planning, architecture, strategy, review, audit, optimization, bug check, or "make this better"
- follows a failed attempt or user correction
- is ambiguous

Fast path is allowed only when all are true:

- one file
- mechanically obvious change
- no runtime/config/schema/test/workflow/current-truth surface
- no behavior change
- no ambiguity

For gated work:

1. GPT reasons and creates plan/ledger.
2. PhD Critic reviews substantive plans before implementation.
3. Codex implements exactly one ready ledger.
4. PhD Critic reviews Codex implementation.
5. GPT accepts the result or creates the next patch ledger.
6. Persist with state-sync or session-wrap if needed.

## Discovered Project Commands

Discovered on 2026-05-01:

- Package/build backend: Python `setuptools` from `pyproject.toml`.
- Package manager artifacts: `uv.lock` and `requirements.txt` are present.
- Test command: `pytest` is configured through `[tool.pytest.ini_options]` in `pyproject.toml`.
- Lint/typecheck/build commands: TODO: confirm; no repo-local lint/typecheck command was found during bootstrap.
- CI files: TODO: confirm; no `.github/workflows` files were found during bootstrap.
