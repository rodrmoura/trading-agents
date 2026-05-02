# Source

Source files for the VS Code extension and local gateway belong here.

Current source map (P1.5 implementation):

- `extension.ts`: command activation and UX wiring for start, stop, status, and copy-token.
- `gatewayController.ts`: gateway lifecycle state machine, localhost bind/start/stop orchestration, token lifecycle, and request cancellation fanout.
- `httpRouter.ts`: native endpoint routing for `/health`, `/shutdown`, `/v1/models`, `/v1/chat/completions`, and `/v1/chat/completions/stream`, including strict request validation and SSE event framing.
- `modelService.ts`: VS Code LM model listing and chat adapters, model capability mapping, and sanitized LM error mapping.
- `auth.ts`: bearer authorization checks and rejected token transport handling.
- `errors.ts`: native JSON error envelope and HTTP error/status helpers.
- `commandMessages.ts`: deterministic command message construction and copy-token message behavior.
- `types.ts`: shared lifecycle, status, health, and command result contracts.
- `index.ts`: package exports, including `GatewayStartedChat`.

Boundary rules:

- Do not import from `tradingagents/**` in this package.
- Keep model execution plumbing generic and gateway-scoped; app-specific workflow/tooling behavior belongs outside this package.
