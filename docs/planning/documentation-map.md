# Documentation Map

This map defines what each document owns so planning and implementation changes do not drift.

## Root Documents

| File | Owns | Update When |
| --- | --- | --- |
| `PROJECT-GUIDE.md` | Product direction, project boundaries, success criteria, first vertical slice, repository strategy, decision backlog | Scope, strategy, success criteria, non-goals, or architecture direction changes |
| `TODO.md` | Active task state and near-term backlog | A task starts, completes, blocks, or changes priority |
| `DOCS-GOVERNANCE.md` | Documentation routing and maintenance rules | A document class, update trigger, lifecycle command, or governance rule changes |
| `CODING-STANDARDS.md` | Implementation conventions and validation expectations | Code style, package boundary, testing, or validation rules change |
| `SECURITY.md` | Gateway security, secrets, model access, tool-calling trust boundaries | Gateway auth, token handling, secrets, model access, logging, or tool permissions change |
| `DEPLOY.md` | Operations and local setup overview | Setup, packaging, gateway operation, release, or run commands change |
| `CONTRIBUTING.md` | Contributor workflow and upstream/fork expectations | Git workflow, PR expectations, or upstream sync rules change |
| `docs/CHANGELOG.md` | Governance/session history | Session-wrap or historical recovery needs a durable handoff |
| `PROJECT-CHANGELOG.md` | Earlier local platform history | Preserve existing history; do not use as default governance handoff |

## Docs Folder

| File Or Folder | Owns | Update When |
| --- | --- | --- |
| `docs/README.md` | Documentation index | Any new doc class or important doc is added |
| `docs/architecture/project-vision.md` | Supporting product and architecture narrative | Vision details change below project-guide level |
| `docs/architecture/roadmap.md` | Milestone overview and exit criteria | Phase order, milestone goal, or milestone exit criteria change |
| `docs/architecture/repository-layout.md` | File/folder layout and ownership | New top-level folders, packages, apps, prompt areas, or doc classes are added |
| `docs/architecture/repository-strategy.md` | Fork/upstream/platform repo strategy | Repo strategy, remotes, fork/mirror decisions, or extraction strategy changes |
| `docs/architecture/code-governance.md` | Ownership boundaries and dependency direction | Any folder ownership, dependency rule, or upstream patch policy changes |
| `docs/decisions/*.md` | Durable decisions and rationale | A meaningful decision has alternatives and consequences |
| `docs/guidance/copilot-and-skills.md` | Copilot instructions, skills, prompts, and model workflow | Agent behavior, model routing, slash commands, or customization patterns change |
| `docs/planning/*.md` | Execution plans, gates, task packets, and doc map | Tasks, gates, dependencies, or model-ready work packets change |
| `docs/reference/*.md` | Stable or draft contracts | Gateway API, schemas, manifests, event logs, or inventories change |
| `docs/runbooks/*.md` | Repeatable procedures | Commands or operational workflows become repeatable |

## Customization Files

| File Or Folder | Owns | Update When |
| --- | --- | --- |
| `.github/copilot-instructions.md` | Always-on repo instructions | Future agent behavior should change across the repo |
| `.github/instructions/*.instructions.md` | Scoped instruction files | A reusable rule should apply to file patterns or the full workspace |
| `.github/skills/*/SKILL.md` | Slash-command workflow behavior | A lifecycle workflow changes |
| `.github/skills/README.md` | Slash-command lifecycle matrix | Skill responsibilities or command behavior changes |

## Code And Prompt Areas

| Path | Owns | Update When |
| --- | --- | --- |
| `apps/tradingagents-adapter/` | TradingAgents-specific integration shell | Integration code should not live in upstream-derived folders or generic packages |
| `apps/control-room/` | Future UI prototype | Event contracts are stable enough to visualize |
| `packages/vscode-llm-gateway/` | VS Code extension and local gateway | Gateway implementation starts or changes |
| `packages/llm-gateway-python/` | Python SDK and LangChain adapter | Python integration starts or changes |
| `packages/agent-schemas/` | Generic contracts | Manifest, workflow, tool, event, artifact, memory, or checkpoint schemas change |
| `packages/agent-runtime/` | Generic runtime | Manifest-driven runtime implementation starts or changes |
| `prompts/upstream-tradingagents/` | Extracted TradingAgents prompts with provenance | TradingAgents prompts are extracted or adapted |
| `prompts/shared/` | Domain-neutral reusable prompts | Generic prompts are created |
| `examples/` | Safe demos and fixtures | A local demo or workflow fixture is added |

## Drift Checks

Before ending a planning or implementation session, ask:

- Did this change alter product direction? If yes, update `PROJECT-GUIDE.md`.
- Did this change alter active task state? If yes, update `TODO.md`.
- Did this change alter a durable architecture choice? If yes, add/update an ADR.
- Did this change alter a contract? If yes, update `docs/reference/`.
- Did this change alter commands or operations? If yes, update `docs/runbooks/` and `DEPLOY.md`.
- Did this change touch upstream-derived code? If yes, document the patch rationale.
