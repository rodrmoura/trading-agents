# Codex Task Packets

These task packets are written for Codex coding model implementation. GPT reasoning model should review the plan before a packet starts and review results after each meaningful batch.

Each packet is intentionally narrow. Do not combine packets unless GPT reasoning model explicitly approves the combined scope.

Use the callable `Codex Coding Engineer` agent in `.github/agents/codex-coding-engineer.agent.md` to execute one approved packet at a time.

## Packet Format

Each packet includes:

- **Model:** expected Codex coding model reasoning level.
- **Objective:** concrete outcome.
- **Read first:** files the coding model should inspect before editing.
- **May edit:** intended file scope.
- **Do not edit:** explicit boundaries.
- **Steps:** mechanical implementation sequence.
- **Acceptance criteria:** pass/fail criteria.
- **Validation:** commands or checks to run.
- **Docs:** docs to update if the packet changes behavior.

## Execution Queue

Use this table as the planning index. The detailed packet sections below remain the implementation source; create a final ready `Coding-Agent Task Ledger` from the packet before invoking Codex.

| Phase | Packet | Purpose | Depends On | Handoff Status |
| --- | --- | --- | --- | --- |
| 0 | P0.1 | Commit governance/model-routing customization scope | G0 validation and user commit approval | Approved for G0 commit/push |
| 0 | P0.2 | Confirm repository-root skill discovery | VS Code opened at `TradingAgents/` root | Done this session |
| 0 | P0.3 | Refresh `uv.lock` for current package metadata | Current `pyproject.toml` | Done this session; review approved |
| 0 | P0.4 | Run G0 quality gate and prepare commit scope | P0.1-P0.3 evidence | Done this session; commit/push approved |
| 1 | P1.1 | Create VS Code extension package skeleton | G0 passed | Completed this session; implementation and review approved |
| 1 | P1.2 | Implement gateway lifecycle and health | P1.1 | Completed this session; implementation and review approved |
| 1 | P1.3 | Implement model listing | P1.2 and VS Code model API access | Completed this session; implementation and review approved |
| 1 | P1.4 | Implement basic chat invocation | P1.3 | Completed this session; implementation and review approved |
| 1 | P1.5 | Implement streaming and cancellation | P1.4 | Completed this session; implementation and review approved |
| 2 | P2.1 | Create Python gateway SDK package skeleton | G1 passed and accepted | Completed this session; implementation and review approved |
| 2 | P2.2 | Implement gateway client and typed errors | P2.1 and stable gateway responses | Completed this session; implementation and review approved |
| 2 | P2.3 | Implement streaming client | P1.5 and P2.2 | Completed this session; implementation and review approved |
| 2 | P2.4 | Implement LangChain-compatible adapter | P2.2/P2.3 and TradingAgents integration audit | Completed this session; implementation and review approved |
| 3 | P3.1 | Audit TradingAgents provider integration points | G2 passed or SDK shape stable | Completed this session |
| 3 | P3.2 | Add thin `vscode` provider boundary | P3.1 and SDK adapter | Completed this session; implementation and review approved |
| 3 | P3.3a | Add direct provider smoke script and runbook | P3.2 | Completed this session; implementation and review approved |
| 3 | P3.3b | Implement native non-stream tool-call roundtrip | P3.3a | Completed this session; implementation and review approved |
| 3 | P3.3c | Prove live one-ticker TradingAgents smoke path | P3.3b plus running VS Code gateway/model | Completed this session; live proof passed with free-text structured-output fallback |
| 3 | P3.4 | Add structured-output adapter compatibility | P3.3b native tool-call bridge | Completed this session; implementation and review approved |
| 4 | P4.1 | Formalize agent and workflow schemas | G3 passed | Planned |
| 4 | P4.2 | Define tool, event, artifact, memory, and checkpoint contracts | P4.1 | Planned |
| 4 | P4.3 | Create product strategy review example | P4.1/P4.2 | Planned |
| 5 | P5.1 | Create runtime package skeleton | G4 passed | Planned |
| 5 | P5.2 | Implement manifest loader and simple executor | P5.1 and schema package | Planned |
| 5 | P5.3 | Add tool registry, event log, and checkpoint skeleton | P5.2 and contract gaps closed | Planned |
| 6 | P6.1 | Decide UI surface and create UI skeleton | G5 event logs available | Planned |
| 6 | P6.2 | Render live/generic run timeline from event logs | P6.1 and event contract | Planned |
| 6 | P6.3 | Add artifacts, memory, and approval panes | P6.2 and runtime support | Planned |
| 6 | P6.4 | Add replay/demo workflow fixtures and smoke validation | P6.3 | Planned |

## Phase 0 Packets

### P0.1 Commit Model Routing Customization

Model: Codex coding model high.

Objective: commit the already-added GPT reasoning model/Codex coding model routing policy.

Read first:

- `.github/instructions/model-routing.instructions.md`
- `.github/copilot-instructions.md`
- `docs/guidance/copilot-and-skills.md`
- `TODO.md`
- `docs/CHANGELOG.md` when historical handoff matters

May edit:

- Only docs/customization files if validation finds a small issue.

Do not edit:

- `tradingagents/**`
- `cli/**`
- package implementation files

Steps:

1. Run docs validation.
2. Stage only model-routing customization files.
3. Commit with `docs: add model routing policy`.
4. Push the current branch to `origin` only after the approved commit/push scope is confirmed.

Acceptance criteria:

- Routing policy is committed.
- Working tree is clean after commit, or only unrelated user changes remain.

Validation:

```powershell
git diff --check
rg -n '[^\x00-\x7F]' .github docs TODO.md DOCS-GOVERNANCE.md PROJECT-CHANGELOG.md
```

Docs:

- Already updated unless validation finds drift.

### P0.2 Workspace Skill Discovery Fix

Model: Codex coding model high.

Objective: make `/state-sync`, `/session-wrap`, and `/session-resume` discoverable in VS Code by using `TradingAgents/` as the workspace root.

Read first:

- `.github/skills/README.md`
- `.github/skills/state-sync/SKILL.md`
- `.github/skills/session-wrap/SKILL.md`
- `.github/skills/session-resume/SKILL.md`
- `docs/guidance/copilot-and-skills.md`

May edit:

- Docs only, unless user chooses a parent-workspace customization strategy.

Do not edit:

- Duplicate skill files outside the repo unless the user explicitly chooses parent workspace skills.

Steps:

1. Confirm whether VS Code is opened at `TradingAgents/` or parent `Tauric/`.
2. If opened at parent, reopen VS Code at `TradingAgents/` root for this project.
3. Do not duplicate skill files into the parent folder.
4. Update `docs/guidance/copilot-and-skills.md` only if discovery behavior changes.

Acceptance criteria:

- User knows slash commands require the `TradingAgents/` workspace root.
- Skills remain version-controlled in the integration repo.

Validation:

- Confirm skill frontmatter has matching folder names and `user-invocable: true`.
- `git diff --check` for docs changes.

Docs:

- `docs/guidance/copilot-and-skills.md`
- `TODO.md` if the workspace setup choice becomes a tracked task.

### P0.3 Refresh `uv.lock` For Current Package Metadata

Model: Codex coding model high.

Objective: refresh `uv.lock` so the lockfile matches current `pyproject.toml` package metadata.

Read first:

- `pyproject.toml`
- `uv.lock`
- `requirements.txt`
- `docs/repo_state/PROVEN_KNOWLEDGE.md`

May edit:

- `uv.lock`

Do not edit:

- `pyproject.toml`
- `requirements.txt`
- source files
- docs

Steps:

1. Run `uv lock` from the repository root.
2. Inspect the generated `uv.lock` diff for project version and dependency metadata changes.
3. Confirm `requirements.txt` did not drive lockfile metadata.
4. Run `uv lock --check`.
5. Run the Python test suite through the configured `.venv`.

Acceptance criteria:

- `uv.lock` records the current project version and dependency metadata from `pyproject.toml`.
- `uv lock --check` passes.
- Python tests pass.
- Only `uv.lock` changes.

Validation:

```powershell
uv lock --check
& "c:/VSCode/Tauric/TradingAgents/.venv/Scripts/python.exe" -m pytest -q
git diff --check -- uv.lock
```

Docs:

- Current-truth docs only after GPT review accepts the generated lockfile diff.

### P0.4 Run G0 Quality Gate And Prepare Commit Scope

Model: Codex coding model high.

Objective: verify G0 readiness and prepare an explicit commit scope; after approval, commit and push only that approved scope.

Read first:

- `docs/planning/gates.md`
- `docs/repo_state/ACTIVE_STATE.md`
- `docs/repo_state/PROVEN_KNOWLEDGE.md`
- `docs/EXPERIMENT_LOG.md`
- `docs/CHANGELOG.md`

May edit:

- Current-truth or planning docs only if validation finds small stale facts.

Do not edit:

- `tradingagents/**`
- `cli/**`
- package implementation files
- generated caches or build outputs

Steps:

1. Run the G0 validation commands from `docs/planning/gates.md`.
2. Confirm `uv lock --check` and Python tests pass.
3. Review `git status --short --ignored` and separate intended files from ignored local artifacts.
4. Produce an intended commit-scope list.
5. Do not stage, commit, or push unless the user has approved the exact persistence scope.

Acceptance criteria:

- G0 pass/fail status is explicit.
- Intended files are separated from ignored `.venv`, caches, build output, and egg-info.
- Any remaining blockers are recorded in current-truth docs.

Validation:

```powershell
git status --short --branch
git remote -v
git diff --check
rg -n '[^\x00-\x7F]' .github docs apps packages prompts examples PROJECT-GUIDE.md TODO.md DOCS-GOVERNANCE.md CODING-STANDARDS.md SECURITY.md DEPLOY.md CONTRIBUTING.md PROJECT-CHANGELOG.md requirements.txt
uv lock --check
& "c:/VSCode/Tauric/TradingAgents/.venv/Scripts/python.exe" -m pytest -q
```

Docs:

- `docs/repo_state/ACTIVE_STATE.md`
- `docs/EXPERIMENT_LOG.md`
- `docs/CHANGELOG.md` if this closes the session.

## Phase 1 Packets: VS Code Gateway Spike

Phase 1 proves a VS Code extension can expose a secure local gateway and invoke VS Code language models. It must not add TradingAgents-specific behavior, Python SDK code, structured-output normalization, tool calling, OpenAI compatibility, WebSockets, or a standalone service.

Implementation status note: P1.1 through P1.5 were completed and review-approved in this session. Manual G1 live smoke passed, was recorded in `docs/EXPERIMENT_LOG.md`, and is accepted for Phase 2 entry.

### Phase 1 Decision Locks

- Package path: `packages/vscode-llm-gateway/`.
- Language/runtime: TypeScript VS Code extension running in the extension host.
- Package manager: npm. `package-lock.json` is allowed when generated by `npm install` for this package.
- HTTP server: Node built-in `http`; do not add Express, Fastify, Hono, Koa, or a separate local service in Phase 1.
- Gateway bind address: exactly `127.0.0.1`.
- Port: ephemeral by default with `server.listen(0, "127.0.0.1")`; status reports the selected port.
- Token: memory-only, generated with Node crypto after successful server bind, invalidated on stop/shutdown/deactivation, never persisted, never logged, never returned by HTTP endpoints.
- Auth transport: accept tokens only as `Authorization: Bearer <gateway-token>`. Reject query-string, cookie, body, alternate-header, path, and malformed auth tokens.
- Token visibility: expose token only through `tradingAgentsGateway.copyToken` or an explicit `Copy Token` action from start/status messages.
- Commands: `tradingAgentsGateway.start`, `tradingAgentsGateway.stop`, `tradingAgentsGateway.status`, and `tradingAgentsGateway.copyToken`.
- Extension activation: command activation only. No wildcard or startup activation, server start, token generation, model listing, model calls, or clipboard writes during activation.
- Native API only: use the Phase 1 contract in `docs/reference/gateway-api-draft.md`.
- Streaming: only `POST /v1/chat/completions/stream` with Server-Sent Events. Do not implement `stream: true` on `POST /v1/chat/completions`.
- Request validation: strict. Reject unknown top-level fields and unknown message object fields in Phase 1.
- Output mode: plain text only. Structured output and tool calls are deferred.
- CORS: do not enable permissive CORS by default.

### P1.1 Ledger: Create VS Code Extension Package Skeleton

Task ID: `P1.1-vscode-extension-skeleton`

Status: completed; implementation and review approved in this session.

Route: Codex Coding Engineer / Codex 5.3.

Reasoning effort: high.

Decision locks:

- Implement only package scaffolding.
- Do not create an HTTP listener, token generator, gateway state machine, model listing, chat invocation, or streaming behavior in this packet.
- Register the four command IDs from Phase 1 decision locks with deterministic placeholder behavior.
- Use command activation events only; do not use `*`, `onStartupFinished`, workspace activation, or file activation events.
- Use npm and TypeScript.
- Allow `package-lock.json` only if generated by npm for `packages/vscode-llm-gateway/`.

Task:

Create the minimal TypeScript VS Code extension package skeleton in `packages/vscode-llm-gateway/` so later packets can add gateway behavior without reshaping the package.

Read first:

- `packages/vscode-llm-gateway/README.md`
- `packages/vscode-llm-gateway/src/README.md`
- `packages/vscode-llm-gateway/tests/README.md`
- `docs/reference/gateway-api-draft.md`
- `CODING-STANDARDS.md`
- `SECURITY.md`

May edit:

- `packages/vscode-llm-gateway/package.json`
- `packages/vscode-llm-gateway/package-lock.json`
- `packages/vscode-llm-gateway/tsconfig.json`
- `packages/vscode-llm-gateway/.vscodeignore`
- `packages/vscode-llm-gateway/README.md`
- `packages/vscode-llm-gateway/src/**`
- `packages/vscode-llm-gateway/tests/**`

Do not edit:

- `tradingagents/**`
- `cli/**`
- `packages/llm-gateway-python/**`
- `packages/agent-runtime/**`
- `packages/agent-schemas/**`
- root `pyproject.toml`, `requirements.txt`, or `uv.lock`
- repo-level `.github/**` customization files
- docs outside `packages/vscode-llm-gateway/README.md`

Implementation steps:

1. Create `package.json` with VS Code extension metadata, `main` pointing to compiled extension output, activation events only for the four command IDs, and command contributions for start, stop, status, and copy token.
2. Add scripts: `compile` for TypeScript emit, `check` for TypeScript no-emit checking, and `vscode:prepublish` delegating to `compile`.
3. Add TypeScript dev dependencies for VS Code extension typing, Node typing, and TypeScript. Do not add runtime dependencies in P1.1 unless TypeScript/VS Code packaging requires them.
4. Add `tsconfig.json` targeting a Node runtime compatible with the VS Code extension host and emitting compiled files under an ignored build output folder such as `dist/`.
5. Add `src/extension.ts` exporting `activate(context)` and `deactivate()`.
6. Register the four commands in `activate` and push all disposables into `context.subscriptions`.
7. Implement placeholder command behavior only: `start` reports that networking arrives in P1.2; `stop` and `status` report not running; `copyToken` reports no token exists until gateway start is implemented.
8. Ensure placeholder commands do not generate tokens, open sockets, call `vscode.lm`, write to clipboard, or read environment secrets.
9. Update package README with package-local setup, compile/check commands, command IDs, and the fact that P1.1 does not start a gateway.
10. Replace or remove placeholder `src/README.md` and `tests/README.md` only if real source/test files make them obsolete.

Acceptance criteria:

- `npm install` succeeds from `packages/vscode-llm-gateway/`.
- `npm run check` succeeds.
- `npm run compile` succeeds.
- The package contributes exactly the four Phase 1 command IDs.
- Activation events are command-scoped only and do not activate on startup or wildcard.
- Extension activation does not start networking or call VS Code language model APIs.
- Placeholder commands are deterministic and safe.
- No files outside the allowed path list change.

Verification:

```powershell
Push-Location packages/vscode-llm-gateway
npm install
npm run check
npm run compile
Pop-Location
git diff --check -- packages/vscode-llm-gateway
```

Stop conditions:

- If npm cannot resolve VS Code extension typings without changing the package strategy, stop and report.
- If a scaffold command or generator wants to overwrite repo-level files, stop and report.
- If a test/build setup requires choosing a framework beyond TypeScript compile/check, stop and report instead of adding it in P1.1.

Final report:

1. Files changed.
2. Package scripts added.
3. Commands registered.
4. Verification run and result.
5. Any unresolved package/version concerns.

### P1.2 Ledger: Implement Gateway Lifecycle And Health

Task ID: `P1.2-gateway-lifecycle-health`

Status: completed; implementation and review approved in this session.

Route: Codex Coding Engineer / Codex 5.3.

Reasoning effort: high.

Decision locks:

- Use Node built-in `http` only.
- Bind exactly to `127.0.0.1` and use an ephemeral port.
- Generate a memory-only token with Node crypto only after the HTTP server successfully binds.
- Gateway states are `stopped`, `starting`, `running`, `stopping`, and `failed`.
- `/health` is public and must not expose secrets.
- `/shutdown` requires bearer auth, accepts no request body, sends a complete response, then uses the shared stop path.
- All unimplemented known protected endpoints must require auth before returning `501 not_implemented`.
- No VS Code language model API calls in this packet.
- Stop command, authenticated shutdown, and `deactivate` invalidate the token and close the HTTP server on best-effort basis.
- Copy-token before start fails gracefully and must not start the gateway.

Task:

Implement explicit start/stop/status/copy-token command behavior, gateway lifecycle state, token authentication helpers, public health response, token-protected shutdown, and shared native error helpers.

Read first:

- `docs/reference/gateway-api-draft.md`
- `SECURITY.md`
- `CODING-STANDARDS.md`
- `packages/vscode-llm-gateway/package.json`
- `packages/vscode-llm-gateway/src/**`

May edit:

- `packages/vscode-llm-gateway/package.json`
- `packages/vscode-llm-gateway/package-lock.json`
- `packages/vscode-llm-gateway/README.md`
- `packages/vscode-llm-gateway/src/**`
- `packages/vscode-llm-gateway/tests/**`

Do not edit:

- `tradingagents/**`
- `cli/**`
- `packages/llm-gateway-python/**`
- `docs/reference/gateway-api-draft.md`
- `SECURITY.md`
- root package or Python dependency files

Implementation steps:

1. Add gateway state, token, auth, JSON response, native error envelope, and server modules under `src/`.
2. Generate `crypto.randomBytes(32).toString("base64url")` only after successful bind and clear it on stop, shutdown, deactivation, and failed start.
3. Accept only `Authorization: Bearer <token>` and reject URL/body/cookie/alternate-header token submissions.
4. Listen on `127.0.0.1` with port `0`.
5. Implement public `GET /health` with the locked response and no token value.
6. Implement authenticated `POST /shutdown` with no body, response-before-close behavior, and the same stop path as the VS Code stop command.
7. Return sanitized native errors for bad method, bad path, unsupported media type, invalid JSON, validation failure, unauthorized, not-implemented, and gateway-not-ready cases.
8. Make start and stop idempotent.
9. Implement status without showing token by default.
10. Implement `copyToken` command and a `Copy Token` action from start/status messages as the only token disclosure path.
11. Implement `deactivate()` to stop the server on best-effort basis.
12. For known future protected paths, check bearer auth first; after successful auth, return `501 not_implemented` until the owning packet implements the route.
13. Add focused unit tests for token generation/clearing, auth success/failure, token transport rejection, health shape, future protected path auth gating, shutdown auth, shutdown response-before-close behavior, copy-token before start, idempotent start/stop, and no token in health.
14. Update package README with command, health, shutdown, and token-copy behavior.

Acceptance criteria:

- Start command starts exactly one server bound to `127.0.0.1`.
- Start while running does not rotate token and reports existing status.
- Stop command closes the server and clears the token.
- Deactivation stops the server on best-effort basis.
- Authenticated shutdown sends a response before closing the server and clears the token through the shared stop path.
- `/health` works without auth and contains no token.
- `/shutdown` requires bearer auth.
- Token can be copied only through explicit VS Code user action.
- Tokens are accepted only through `Authorization: Bearer <token>`.
- No prompt text, response text, token, environment value, or stack trace is logged or returned.
- No VS Code language model APIs are called.

Verification:

```powershell
Push-Location packages/vscode-llm-gateway
npm run check
npm run compile
npm test --if-present
Pop-Location
git diff --check -- packages/vscode-llm-gateway
```

Manual smoke, if the extension can be launched in a development host:

```powershell
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:<port>/health
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:<port>/shutdown -Headers @{ Authorization = "Bearer <copied-token>" }
```

Stop conditions:

- If the package cannot unit-test HTTP lifecycle without a test framework decision, stop and report the minimum framework choice needed.
- If VS Code command UX cannot safely expose the token via clipboard, stop and report instead of logging or persisting the token.
- If another dependency is needed for HTTP routing, stop and report instead of adding it.

Final report:

1. Files changed.
2. Lifecycle behavior implemented.
3. Auth/token behavior implemented.
4. Tests and manual checks run.
5. Remaining concerns.

### P1.3 Ledger: Implement Model Listing

Task ID: `P1.3-gateway-model-listing`

Status: completed; implementation and review approved in this session.

Route: Codex Coding Engineer / Codex 5.3.

Reasoning effort: xhigh because this touches VS Code Language Model API behavior and model identity.

Decision locks:

- `GET /v1/models` requires bearer auth.
- Use `vscode.lm.selectChatModels({})` only when an authenticated request reaches `/v1/models`.
- Do not call language model APIs during extension activation or gateway start.
- Preserve VS Code model IDs as opaque identifiers.
- Chat requests in later packets may use only IDs returned by the current model listing.
- Capability flags default conservatively.
- Do not implement chat or streaming in this packet.

Task:

Expose available VS Code chat models through the native `GET /v1/models` endpoint.

Read first:

- `docs/reference/gateway-api-draft.md`
- `SECURITY.md`
- VS Code Language Model API docs for `vscode.lm.selectChatModels`, `LanguageModelChat`, and `LanguageModelError`
- `packages/vscode-llm-gateway/src/**`

May edit:

- `packages/vscode-llm-gateway/README.md`
- `packages/vscode-llm-gateway/src/**`
- `packages/vscode-llm-gateway/tests/**`

Do not edit:

- `docs/reference/gateway-api-draft.md`
- `tradingagents/**`
- `cli/**`
- `packages/llm-gateway-python/**`
- Python dependency files

Implementation steps:

1. Add a VS Code model service wrapper with one method for listing models.
2. Call `vscode.lm.selectChatModels({})` inside the authenticated `/v1/models` request path only.
3. Map each model to the locked model object: opaque `id`, `name` fallback to `id`, nullable `vendor`, nullable `family`, nullable `version`, `streaming: false`, conservative `toolCalling`, and `structuredOutput: false`.
4. Return `200` with `{ "models": [] }` when no models are available, unless VS Code throws a known access error.
5. Map VS Code errors into the native sanitized error envelope.
6. Add tests using an injectable model service so tests do not require real VS Code model access.
7. Add tests for auth required, empty list, normal mapping, conservative capability defaults, and sanitized error mapping.
8. Update package README with the model-list endpoint shape and manual smoke instructions.

Acceptance criteria:

- Authenticated `GET /v1/models` returns the locked response shape.
- Unauthenticated request returns `401 unauthorized`.
- Empty model list is represented explicitly.
- Model IDs are opaque and are not normalized, rewritten, or guessed.
- No chat request is made during model listing.
- Tests cover mapping and error cases through an injectable model service.

Verification:

```powershell
Push-Location packages/vscode-llm-gateway
npm run check
npm run compile
npm test --if-present
Pop-Location
git diff --check -- packages/vscode-llm-gateway
```

Manual smoke, if a development host and model access are available:

```powershell
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:<port>/v1/models -Headers @{ Authorization = "Bearer <copied-token>" }
```

Stop conditions:

- If the stable VS Code API in this workspace does not expose model IDs needed for repeatable chat selection, stop and report.
- If model listing requires user consent behavior that cannot be safely triggered from an authenticated local request, stop and report.
- If capability metadata is unavailable, default conservatively instead of inventing capabilities.

Final report:

1. Files changed.
2. Model mapping behavior.
3. Tests and manual checks run.
4. Any VS Code API limitations encountered.

### P1.4 Ledger: Implement Basic Non-Streaming Chat Invocation

Task ID: `P1.4-gateway-basic-chat`

Status: completed; implementation and review approved in this session.

Route: Codex Coding Engineer / Codex 5.3.

Reasoning effort: xhigh because this calls VS Code language models, handles consent/quota errors, and defines the first model invocation contract.

Decision locks:

- Implement only `POST /v1/chat/completions`.
- This endpoint is non-streaming only.
- Reject `stream`, OpenAI-specific fields, tool fields, response schemas, and unknown top-level or message fields.
- Request and response shapes must match `docs/reference/gateway-api-draft.md`.
- Treat model output as plain text.
- Do not implement structured output, tool calling, adapter normalization, Python SDK changes, or TradingAgents provider changes.
- Do not log prompt text, response text, token values, or raw provider payloads.

Task:

Implement authenticated native non-streaming chat invocation through VS Code `LanguageModelChat.sendRequest`.

Read first:

- `docs/reference/gateway-api-draft.md`
- `SECURITY.md`
- VS Code Language Model API docs for `LanguageModelChatMessage`, `LanguageModelChat.sendRequest`, `LanguageModelError`, and cancellation tokens
- `packages/vscode-llm-gateway/src/**`
- `packages/vscode-llm-gateway/tests/**`

May edit:

- `packages/vscode-llm-gateway/README.md`
- `packages/vscode-llm-gateway/src/**`
- `packages/vscode-llm-gateway/tests/**`

Do not edit:

- `docs/reference/gateway-api-draft.md`
- `tradingagents/**`
- `cli/**`
- `packages/llm-gateway-python/**`
- `packages/agent-runtime/**`
- `packages/agent-schemas/**`

Implementation steps:

1. Add strict JSON request parsing for chat POST endpoints with a 1 MiB body limit.
2. Enforce `Content-Type: application/json` or an `application/json` variant.
3. Validate the native chat request exactly: required non-empty `model`, required non-empty `messages`, message roles in `system`, `user`, `assistant`, non-empty string content, optional non-empty `requestId`, optional object `metadata`, and no unknown top-level or message fields.
4. Resolve the requested model by calling `vscode.lm.selectChatModels({})` and selecting the model with matching opaque ID from the current result.
5. If no current model matches, return `404 model_not_found`.
6. Convert native messages to VS Code chat messages: `user` to user message, `assistant` to assistant message, and `system` to a leading user message prefixed with `System instructions:\n` unless stable installed typings expose a system-message constructor.
7. Create and track a `CancellationTokenSource` per non-stream request. Cancel it when the HTTP client disconnects before completion, when the gateway stops, or when the extension deactivates.
8. Call `model.sendRequest(vsCodeMessages, {}, cancellationToken)`.
9. Consume the response text stream into one string for the non-streaming response.
10. Return the locked native chat response shape with generated `gwchat_` ID, ISO `created`, assistant message content, `finishReason: "stop"`, `usage: null`, and metadata.
11. Map `LanguageModelError` categories into sanitized native errors: no permissions/access denied to `model_access_denied`, not found to `model_not_found`, blocked/quota/rate limit to `quota_or_rate_limited`, cancellation to `cancelled`, and other model failures to `unknown_model_error`.
12. Add tests for request validation, unknown fields, auth, model not found, successful response assembly, non-stream cancellation, sanitized model error mapping, and no raw prompt/response in error bodies.
13. Update package README with the non-streaming chat endpoint and manual smoke instructions.

Acceptance criteria:

- Authenticated valid request can call a selected model when VS Code model access is available.
- Invalid JSON, unsupported content type, unknown fields, empty messages, bad roles, missing model, and missing auth all produce native sanitized errors.
- Requested model must match the current model list by opaque ID.
- Non-stream endpoint rejects streaming fields instead of silently streaming.
- HTTP client disconnect, gateway stop, and extension deactivation cancel non-stream model requests on best-effort basis.
- No prompt text, response text, token, raw stack trace, or provider payload is logged or returned in errors.
- Tests cover validation, success path through an injectable model service, cancellation, and error mapping.

Verification:

```powershell
Push-Location packages/vscode-llm-gateway
npm run check
npm run compile
npm test --if-present
Pop-Location
git diff --check -- packages/vscode-llm-gateway
```

Manual smoke, if a development host and model access are available:

```powershell
$body = @{
  model = "<model-id-from-models>"
  messages = @(@{ role = "user"; content = "Reply with one short sentence." })
} | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:<port>/v1/chat/completions -Headers @{ Authorization = "Bearer <copied-token>" } -ContentType "application/json" -Body $body
```

Stop conditions:

- If the installed VS Code API differs from the assumed `sendRequest` response text iteration contract, stop and report the exact type/API mismatch.
- If non-stream cancellation cannot be wired without broad lifecycle refactoring, stop and report before implementing partial cancellation.
- If consent prompts cannot be triggered safely from an authenticated request path, stop and report.
- If tests require a new framework decision, stop and report rather than adding a broad framework without approval.

Final report:

1. Files changed.
2. Chat request/response behavior implemented.
3. Error mapping implemented.
4. Tests and manual checks run.
5. Any VS Code access or consent limitations.

### P1.5 Ledger: Implement Streaming And Cancellation

Task ID: `P1.5-gateway-streaming-cancellation`

Status: completed; implementation and review approved in this session.

Route: Codex Coding Engineer / Codex 5.3.

Reasoning effort: xhigh because this defines streaming semantics and cancellation behavior used by later SDK code.

Decision locks:

- Implement only `POST /v1/chat/completions/stream` for streaming.
- Use Server-Sent Events exactly as documented in `docs/reference/gateway-api-draft.md`.
- Do not implement WebSockets, NDJSON, OpenAI `[DONE]`, or `stream: true` on the non-stream endpoint.
- Client disconnect cancels the VS Code request with a `CancellationTokenSource` on a best-effort basis.
- No tool calling or structured output.
- After P1.5, model listing may report `capabilities.streaming: true` for models that can use this gateway stream path.

Task:

Add native SSE streaming for chat completions and cancellation on client disconnect.

Read first:

- `docs/reference/gateway-api-draft.md`
- VS Code Language Model API docs for response text streaming and cancellation tokens
- `packages/vscode-llm-gateway/src/**`
- `packages/vscode-llm-gateway/tests/**`

May edit:

- `packages/vscode-llm-gateway/README.md`
- `packages/vscode-llm-gateway/src/**`
- `packages/vscode-llm-gateway/tests/**`

Do not edit:

- `docs/reference/gateway-api-draft.md`
- `tradingagents/**`
- `cli/**`
- `packages/llm-gateway-python/**`
- `packages/agent-runtime/**`
- `packages/agent-schemas/**`

Implementation steps:

1. Reuse the P1.4 native chat request validation for the streaming endpoint.
2. Reject unknown fields and reject any attempt to use OpenAI-style streaming flags.
3. Set SSE headers exactly: `Content-Type: text/event-stream`, `Cache-Control: no-cache`, and `Connection: keep-alive`.
4. Add an SSE writer helper for `chunk`, `done`, and `error` events with JSON payloads.
5. Create a `CancellationTokenSource` per streaming request.
6. Register HTTP request/response close handlers so client disconnect cancels the VS Code model request on best-effort basis.
7. Call the selected VS Code model with the same model resolution and message conversion rules as P1.4.
8. Emit one `chunk` event per response text fragment: `event: chunk` and `data: {"text":"partial text"}`.
9. On normal completion, emit exactly one `done` event with `id`, `model`, `finishReason`, and `metadata`, then close.
10. On model or validation error after the first SSE byte is sent, emit exactly one `error` event with the native error envelope, then close.
11. On errors before SSE headers are sent, return normal JSON error response with the native status code.
12. Update model listing capability mapping so `streaming` is `true` after this endpoint exists.
13. Add tests for SSE framing, chunk order, done event, error event, auth failure, validation failure before headers, and cancellation source cancellation on disconnect.
14. Update README with streaming endpoint and manual cancellation smoke notes.

Acceptance criteria:

- Authenticated stream request emits valid SSE `chunk` events and one terminal `done` event on success.
- Stream errors use one terminal `error` event after headers are sent.
- Client disconnect cancels the in-flight VS Code request on best-effort basis.
- Non-streaming endpoint remains non-streaming and rejects streaming fields.
- No OpenAI `[DONE]` sentinel appears.
- No prompt text, response text, token, raw stack trace, or provider payload is logged or returned in errors.
- Tests cover SSE framing and cancellation with mocked/injectable model service behavior.

Verification:

```powershell
Push-Location packages/vscode-llm-gateway
npm run check
npm run compile
npm test --if-present
Pop-Location
git diff --check -- packages/vscode-llm-gateway
```

Manual smoke, if a development host and model access are available:

```powershell
$body = @{
  model = "<model-id-from-models>"
  messages = @(@{ role = "user"; content = "Count from one to five slowly." })
} | ConvertTo-Json -Depth 5
Invoke-WebRequest -Method Post -Uri http://127.0.0.1:<port>/v1/chat/completions/stream -Headers @{ Authorization = "Bearer <copied-token>" } -ContentType "application/json" -Body $body
```

Stop conditions:

- If VS Code response streaming cannot be consumed incrementally through the stable API, stop and report instead of faking chunks from a complete response.
- If cancellation cannot be wired from client disconnect to VS Code cancellation tokens, stop and report the exact API limitation.
- If SSE tests require a new framework decision, stop and report rather than adding a broad framework without approval.

Final report:

1. Files changed.
2. Streaming contract implemented.
3. Cancellation behavior implemented.
4. Tests and manual checks run.
5. Any runtime limitations.

## Phase 2 Packets: Python SDK And LangChain Adapter

### P2.1 Create Python SDK Package Skeleton

Status: completed; implementation and review approved in this session.

Model: Codex coding model high.

Objective: create a generic Python SDK package under `packages/llm-gateway-python/`.

Read first:

- `packages/llm-gateway-python/README.md`
- `docs/reference/gateway-api-draft.md`
- root `pyproject.toml`
- `CODING-STANDARDS.md`

May edit:

- `packages/llm-gateway-python/**`
- docs/runbooks if setup commands are needed

Do not edit:

- `tradingagents/**`
- `cli/**`

Steps:

1. Add package metadata.
2. Add source package with client, errors, and types modules.
3. Add tests scaffold.
4. Add installation/test commands to package README.

Acceptance criteria:

- Package imports locally.
- Tests can run even if minimal.
- No TradingAgents imports.

Validation:

- package test command
- import smoke
- `git diff --check`

Docs:

- `packages/llm-gateway-python/README.md`

### P2.2 Implement Gateway Client And Errors

Status: completed; implementation and review approved in this session. The executed ledger used xhigh/highest available reasoning because bearer-token transport and SDK exception surfaces are security-sensitive.

Model: Codex coding model high.

Objective: implement health, model listing, chat, and error mapping.

Read first:

- `docs/reference/gateway-api-draft.md`
- `packages/llm-gateway-python/src/**`

May edit:

- `packages/llm-gateway-python/**`

Do not edit:

- LangChain adapter unless explicitly in scope.

Steps:

1. Add client configuration for base URL, token, timeout.
2. Implement health call.
3. Implement model listing call.
4. Implement non-streaming chat call.
5. Map gateway errors to typed exceptions.
6. Add unit tests with mocked HTTP responses.

Acceptance criteria:

- Tests cover success and each documented error category.
- Token is sent but never printed.

Validation:

- package tests
- `git diff --check`

Docs:

- SDK README if API changes.

### P2.3 Implement Streaming Client

Model: Codex coding model high.

Objective: expose streaming responses from the gateway SDK.

Read first:

- streaming endpoint in `docs/reference/gateway-api-draft.md`
- SDK client implementation

May edit:

- `packages/llm-gateway-python/**`

Steps:

1. Add streaming method returning an iterator or async iterator.
2. Parse chunk, done, and error events.
3. Add cancellation/close behavior if supported.
4. Add mocked tests.

Acceptance criteria:

- Streaming parser handles normal chunks, done, and error events.
- Caller can stop consuming safely.

Validation:

- package tests
- `git diff --check`

### P2.4 Implement LangChain-Compatible Adapter

Status: completed; implementation and review approved in this session. The adapter remains package-local, keeps LangChain Core optional, and documents structured-output/tool-calling deferrals.

Model: Codex coding model extra-high.

Objective: expose the gateway SDK through the smallest LangChain-compatible surface TradingAgents needs.

Read first:

- `tradingagents/llm_clients/base_client.py`
- `tradingagents/llm_clients/openai_client.py`
- `tradingagents/agents/utils/structured.py`
- `tests/test_structured_agents.py`
- SDK client implementation

May edit:

- `packages/llm-gateway-python/**`
- tests under package

Do not edit:

- TradingAgents provider files until P3.

Steps:

1. Identify minimal LangChain methods/protocols used by TradingAgents.
2. Implement adapter around SDK client.
3. Add structured-output support or a clearly documented fallback.
4. Add tests using mocked gateway responses.

Acceptance criteria:

- Adapter can be invoked in the same style TradingAgents expects.
- Structured-output test proves expected behavior or documents fallback.

Validation:

- package tests
- `git diff --check`

Docs:

- `docs/reference/gateway-api-draft.md` if structured output contract changes.

## Phase 3 Packets: TradingAgents Provider

### P3.1 Audit TradingAgents Provider Integration Points

Model: Codex coding model high.

Objective: produce a short implementation note identifying exact files and minimal changes for `vscode` provider.

Read first:

- `tradingagents/llm_clients/factory.py`
- `tradingagents/llm_clients/model_catalog.py`
- `tradingagents/llm_clients/base_client.py`
- `cli/utils.py`
- `cli/main.py`
- `tradingagents/graph/trading_graph.py`
- `tests/test_model_validation.py`
- `tests/test_structured_agents.py`

May edit:

- `docs/reference/` or `apps/tradingagents-adapter/README.md` only for the implementation note.

Do not edit:

- Source code in this audit packet.

Steps:

1. Identify provider factory extension point.
2. Identify CLI provider selection/config extension point.
3. Identify model catalog changes, if any.
4. Identify tests to add/update.
5. Write concise implementation note.

Acceptance criteria:

- Next packet can implement without rediscovering integration points.

Validation:

- `git diff --check`

### P3.2 Add `vscode` Provider Boundary

Status: completed; implementation and review approved in this session. The provider boundary is construction-focused and does not make full analyst execution pass.

Model: Codex coding model extra-high.

Objective: add a thin `vscode` provider routed through the Python SDK/adapter.

Read first:

- P3.1 implementation note
- SDK adapter files
- provider factory files
- relevant tests

May edit:

- `tradingagents/llm_clients/**`
- `cli/**` only if needed for provider selection
- `tests/**`
- docs for patch rationale

Do not edit:

- agent graph or analyst/trader/manager logic unless unavoidable and documented.

Steps:

1. Add provider identifier `vscode`.
2. Add provider client/factory path that wraps SDK adapter.
3. Read gateway config from environment or explicit config without secrets.
4. Add tests for provider selection and missing config.
5. Update docs with patch rationale.

Acceptance criteria:

- Existing providers still work.
- `vscode` provider can be selected in tests.
- Missing gateway config fails clearly.

Validation:

- targeted provider tests
- existing model validation tests
- `git diff --check`

Docs:

- `docs/architecture/code-governance.md` if patch pattern changes.
- patch log if created.

### P3.3a Add Direct Provider Smoke Script And Runbook

Status: completed this session; implementation and review approved. This slice proves provider construction and optional direct `GatewayChatModel.invoke(...)`, not a full one-ticker analyst graph.

Model: Codex coding model high.

Objective: make a constrained TradingAgents `vscode` provider smoke run straightforward without claiming full analyst support.

Read first:

- `tradingagents/llm_clients/vscode_client.py`
- `scripts/smoke_vscode_provider.py`
- `docs/runbooks/gateway-g1-smoke.md`
- provider implementation

May edit:

- `scripts/**`
- `docs/runbooks/**`
- `tests/**`

Steps:

1. Add a smoke script that reads the `vscode` gateway environment and constructs the provider.
2. Support construction-only mode and one direct `llm.invoke(...)` call.
3. Add runbook steps with required environment variables but no secret values.
4. Add mocked tests for env/model/prompt validation, construction-only mode, invoke mode, and token redaction.

Acceptance criteria:

- User can follow the runbook to start the gateway and validate provider construction/direct invoke.
- Script does not print tokens or secrets, including in failure or assistant-output text.
- Runbook remains explicit that full analyst graph execution is blocked.

Validation:

- targeted tests
- manual direct provider smoke if gateway exists
- `git diff --check`

### P3.3b Implement Native Non-Stream Tool-Call Roundtrip

Status: completed this session; implementation and review approved. This slice proves mocked native tool-call roundtrip across the gateway, SDK, and LangChain adapter, not a live full one-ticker TradingAgents run.

Model: Codex coding model extra-high.

Objective: let TradingAgents analysts receive LangChain `AIMessage.tool_calls` through the `vscode` provider so LangGraph `ToolNode` can execute local Python tools and send tool results back on the next non-stream model turn.

Read first:

- `docs/reference/tradingagents-vscode-provider-audit.md`
- `packages/llm-gateway-python/src/llm_gateway/langchain_adapter.py`
- `tradingagents/agents/**`
- `tradingagents/graph/**`
- `docs/runbooks/tradingagents-vscode-provider.md`

May edit:

- `packages/vscode-llm-gateway/**`
- `packages/llm-gateway-python/**`
- gateway API/runbook docs

Do not edit:

- Do not weaken analyst behavior, silently skip required tools, add OpenAI-compatible endpoint/field names, or claim live full-smoke success from mocked roundtrip tests.

Acceptance criteria:

- Non-stream `/v1/chat/completions` supports native `tools`, assistant `toolCalls`, and `role: "tool"` messages.
- `/v1/chat/completions/stream` remains text-only and rejects tool-enabled requests before model invocation.
- `GatewayChatModel.bind_tools()` returns a bound clone and round-trips LangChain tool calls/results through native SDK types without OpenAI contract leakage.

Validation:

- gateway package check/compile/tests
- SDK package tests
- full root pytest
- `git diff --check`

### P3.3c Prove Live One-Ticker TradingAgents Smoke Path

Status: completed this session; harness readiness and live proof passed. Downstream structured-output support was future work at P3.3c completion because the live proof used the documented free-text fallback.

Model: Codex coding model extra-high.

Objective: prepare a repeatable full-graph smoke harness, then run and record a live full one-ticker TradingAgents path through VS Code models without bypassing analyst requirements silently.

Read first:

- `docs/runbooks/tradingagents-vscode-provider.md`
- `docs/reference/gateway-api-draft.md`
- `scripts/smoke_vscode_provider.py`
- `tests/test_vscode_provider_smoke_script.py`
- `tradingagents/graph/trading_graph.py`
- `tradingagents/agents/**`

May edit:

- smoke/runbook docs and narrow test/script helpers if live execution exposes operator gaps.

Do not edit:

- Do not claim full smoke success unless the live path runs through the relevant graph roles.

Acceptance criteria:

- Harness readiness: `scripts/smoke_vscode_tradingagents_graph.py` can validate gateway environment, model, ticker, ISO trade date, analyst list, output paths, and round counts before graph construction; builds an isolated `vscode` graph config; calls `TradingAgentsGraph(...).propagate(ticker, trade_date)`; checks nonblank selected analyst reports plus `investment_plan`, `trader_investment_plan`, `final_trade_decision`, and processed decision; prints concise token-redacted evidence with field character counts instead of report bodies.
- Harness readiness: deterministic mocked tests cover input validation before construction, config construction, propagation arguments, success redaction, final-state enforcement, and graph construction/propagation exception redaction.
- Live proof: the harness command in `docs/runbooks/tradingagents-vscode-provider.md` exits successfully against a running VS Code gateway/model.
- Live proof: Research Manager, Trader, and Portfolio Manager coverage is proven or any accepted fallback/degraded structured-output behavior is explicitly recorded.
- Live proof: token handling and gateway model IDs remain opaque and secret-safe.
- P3.3c must not be marked completed from mocked harness tests alone.

Completion evidence:

- Live gateway: `127.0.0.1:54593`, gateway `0.0.1`, `56` listed models.
- Selected model: `claude-opus-4.6-1m`.
- Direct provider construction and direct invoke smoke both passed.
- Full graph: `NVDA`, `2024-05-10`, analyst `market`, processed decision `Hold`.
- Checked field counts: `market_report=4401`, `investment_plan=1497`, `trader_investment_plan=480`, `final_trade_decision=1117`.
- Research Manager, Trader, and Portfolio Manager used the documented free-text fallback because `with_structured_output(...)` was unsupported by `llm_gateway` at P3.3c time.

Validation:

- harness readiness targeted tests for the graph smoke script and existing VS Code provider smoke/boundary tests
- documented live smoke evidence for completion of P3.3c live proof
- full root pytest if resources allow after code changes
- `git diff --check`

### P3.4 Structured-Output Adapter Compatibility

Status: completed this session; local validation passed; implementation review approved.

Model: Codex coding model extra-high.

Objective: enable `GatewayChatModel.with_structured_output(...)` for non-streaming adapter calls by delegating to LangChain Core's tool-call parser path over the existing native gateway `tools`/`toolCalls` bridge.

Acceptance evidence:

- Pydantic schemas parse native `GatewayToolCall` input into Pydantic instances.
- Dict/JSON schemas parse matching native tool-call input into dicts.
- `include_raw=True` returns LangChain Core's `raw`/`parsed`/`parsing_error` shape for success and parser-error cases.
- Captured adapter requests contain native `tools` only; no tool-choice enforcement field, OpenAI facade fields, HTTP `response_format`, or LangChain internal structured-output metadata is forwarded.
- Explicit unsupported generation kwargs, stop sequences, tool-enabled streaming, named/required/explicit-any `bind_tools()` tool choice, and arbitrary unsupported `bind_tools()` kwargs remain rejected.

Validation:

- `c:/VSCode/Tauric/TradingAgents/.venv/Scripts/python.exe -m pytest -q packages/llm-gateway-python/tests/test_langchain_adapter.py packages/llm-gateway-python/tests/test_sdk_skeleton.py` (`94 passed`)
- `c:/VSCode/Tauric/TradingAgents/.venv/Scripts/python.exe -m pytest -q tests/test_structured_agents.py tests/test_vscode_tradingagents_graph_smoke_script.py tests/test_vscode_provider_boundary.py` (`47 passed`)
- PhD Critic implementation review approved the P3.4 diff with no blocking findings; optional follow-ups are an explicit `with_structured_output(...).stream(...)` adapter test and a note/test guarding LangChain Core's internal `ls_structured_output_format` metadata behavior.
- Post-P3.4 live smoke passed against `claude-sonnet-4.6`: direct `with_structured_output(..., include_raw=True)` returned one raw tool call and a parsed Pydantic instance, then `scripts/smoke_vscode_tradingagents_graph.py` passed for `NVDA`/`2024-05-10` with market analyst selected and field counts `market_report=7501`, `investment_plan=2551`, `trader_investment_plan=1009`, `final_trade_decision=2523`. The successful graph command required `PYTHONPATH` set to the repository root.

## Phase 4 Packets: Generalized Contracts

### P4.1 Formalize Agent And Workflow Schemas

Model: Codex coding model extra-high.

Objective: turn draft manifest concepts into executable schema definitions.

Read first:

- `docs/reference/agent-manifest-draft.md`
- `packages/agent-schemas/README.md`
- `docs/architecture/project-vision.md`

May edit:

- `packages/agent-schemas/**`
- `docs/reference/**`
- `docs/decisions/**`

Steps:

1. Confirm schema technology after GPT reasoning model decision review.
2. Implement agent manifest schema.
3. Implement workflow graph schema.
4. Add validation tests and example fixtures.
5. Update reference docs.

Acceptance criteria:

- Valid product strategy review manifests pass validation.
- Invalid manifests fail with useful errors.
- No TradingAgents imports.

Validation:

- schema package tests
- `git diff --check`

### P4.2 Define Tool, Event, Artifact, Memory, And Checkpoint Contracts

Model: Codex coding model extra-high.

Objective: define the contracts that the runtime and future control room need.

Read first:

- `docs/reference/agent-manifest-draft.md`
- `packages/agent-schemas/**`
- `docs/architecture/roadmap.md`

May edit:

- `packages/agent-schemas/**`
- `docs/reference/**`

Steps:

1. Define tool registry schema and permission fields.
2. Define event log schema.
3. Define artifact schema.
4. Define memory scope schema.
5. Define checkpoint schema.
6. Add tests and example fixtures.

Acceptance criteria:

- Product strategy review can express tools, events, artifacts, memory, and checkpoints.
- Future UI has enough event data to observe a run.

Validation:

- schema tests
- `git diff --check`

### P4.3 Create Product Strategy Review Example

Model: Codex coding model high.

Objective: create the first non-finance workflow example.

Read first:

- product strategy requirements in `PROJECT-GUIDE.md`
- schema docs and tests
- `examples/README.md`

May edit:

- `examples/**`
- `prompts/shared/**`
- `docs/reference/**`

Steps:

1. Add example workflow manifest.
2. Add agent manifests for market researcher, competitor researcher, risk reviewer, and strategy manager.
3. Add placeholder prompts with clear contracts.
4. Add schema validation test if schemas exist.

Acceptance criteria:

- Example validates against schemas.
- Example avoids TradingAgents imports and finance assumptions.

Validation:

- schema validation tests
- `git diff --check`

## Phase 5 Packets: Runtime Prototype

### P5.1 Create Runtime Package Skeleton

Model: Codex coding model high.

Objective: create the generalized runtime package structure.

Read first:

- `packages/agent-runtime/README.md`
- `packages/agent-schemas/README.md`
- `docs/architecture/roadmap.md`

May edit:

- `packages/agent-runtime/**`
- `docs/runbooks/**`

Do not edit:

- TradingAgents source files.

Steps:

1. Add package manifest/config.
2. Add runtime source structure.
3. Add test command.
4. Add README setup instructions.

Acceptance criteria:

- Runtime package imports/builds.
- No TradingAgents imports.

Validation:

- package tests/import smoke
- `git diff --check`

### P5.2 Implement Manifest Loader And Simple Executor

Model: Codex coding model extra-high.

Objective: load manifests and execute a simple workflow graph.

Read first:

- `packages/agent-runtime/**`
- `packages/agent-schemas/**`
- product strategy example manifests

May edit:

- `packages/agent-runtime/**`
- tests

Steps:

1. Load and validate workflow manifests.
2. Resolve agent manifests.
3. Execute a simple sequential/parallel graph as contracts allow.
4. Return final state and artifacts.
5. Add tests with product strategy review fixture.

Acceptance criteria:

- Runtime can execute product strategy review skeleton without model calls if needed.
- Execution emits basic events.

Validation:

- runtime tests
- `git diff --check`

### P5.3 Add Tool Registry, Event Log, And Checkpoint Skeleton

Model: Codex coding model extra-high.

Objective: add the core runtime services needed before UI.

Read first:

- schemas for tools/events/checkpoints
- runtime executor implementation

May edit:

- `packages/agent-runtime/**`
- `packages/agent-schemas/**` only if schema gaps are discovered

Steps:

1. Implement tool registry with allow-list checks.
2. Emit typed event logs.
3. Store artifacts in a simple in-memory or file-backed store.
4. Add checkpoint save/load skeleton.
5. Add tests.

Acceptance criteria:

- Unauthorized tool call is blocked.
- Event log can replay high-level run timeline.
- Checkpoint skeleton is enough for future resume work.

Validation:

- runtime tests
- `git diff --check`

## Phase 6 Packets: Control Room Prototype

### P6.1 Decide UI Surface And Create UI Skeleton

Model: Codex coding model high after GPT reasoning model decision.

Objective: create the first control-room UI skeleton after event contracts exist.

Read first:

- `apps/control-room/README.md`
- event log reference docs
- `docs/architecture/roadmap.md`

May edit:

- `apps/control-room/**`
- `docs/decisions/**`
- `docs/runbooks/**`

Steps:

1. GPT reasoning model decides VS Code webview vs standalone browser app.
2. Add minimal app skeleton.
3. Add static event-log fixture viewer.
4. Add setup and validation commands.

Acceptance criteria:

- UI can render a sample event log.
- UI has no TradingAgents imports.

Validation:

- UI build/test once package exists
- screenshot/manual smoke if applicable
- `git diff --check`

### P6.2 Render Live/Generic Run Timeline From Event Logs

Model: Codex coding model high.

Objective: render generic runtime event logs as a run timeline without hardcoding TradingAgents concepts.

Read first:

- `apps/control-room/**`
- event log reference docs
- runtime event fixtures from `examples/**` or `packages/agent-runtime/**`

May edit:

- `apps/control-room/**`
- `examples/**` only for UI-safe fixtures
- docs/runbooks if manual smoke steps change

Steps:

1. Add a typed event-log input boundary.
2. Render run, agent, model request, tool call, artifact, approval, checkpoint, and completion events.
3. Add loading, empty, error, and malformed-event states.
4. Add tests or fixture-based smoke validation.

Acceptance criteria:

- A product strategy review fixture can replay as a timeline.
- UI remains domain-neutral.
- Invalid event data fails visibly without crashing the app.

Validation:

- UI test/build command
- fixture replay smoke
- `git diff --check`

### P6.3 Add Artifacts, Memory, And Approval Panes

Model: Codex coding model high.

Objective: expose generic artifacts, memory references, and human approval pauses from runtime events.

Read first:

- `apps/control-room/**`
- artifact, memory, and approval contract docs
- runtime event fixtures

May edit:

- `apps/control-room/**`
- docs/reference only if UI work exposes contract gaps

Steps:

1. Add artifact list/detail views.
2. Add memory/checkpoint reference views.
3. Add approval request state with accept/reject placeholders if runtime actions are not wired yet.
4. Add tests or fixture smoke coverage.

Acceptance criteria:

- UI can inspect artifacts and memory/checkpoint references from a generic run.
- Approval UI does not imply unsupported runtime actions are live.
- No TradingAgents-specific labels or assumptions are required.

Validation:

- UI test/build command
- fixture replay smoke
- `git diff --check`

### P6.4 Add Replay Fixtures And Control-Room Smoke Validation

Model: Codex coding model high.

Objective: make the control room demonstrable and testable from checked-in generic fixtures.

Read first:

- `apps/control-room/**`
- `examples/**`
- `docs/runbooks/**`

May edit:

- `apps/control-room/**`
- `examples/**`
- `docs/runbooks/**`

Steps:

1. Add product strategy review event-log fixtures.
2. Add a smoke route or script that loads fixture replay data.
3. Document manual smoke steps.
4. Add screenshot or browser smoke validation if the UI stack supports it.

Acceptance criteria:

- A user can run the control room and replay a generic workflow fixture.
- The fixture is independent of TradingAgents source code.
- Smoke steps are documented and repeatable.

Validation:

- UI test/build command
- documented smoke command
- `git diff --check`
