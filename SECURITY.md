# Security

## Scope

This file covers security rules for our local platform work: VS Code model gateway, SDKs, generic agent runtime, prompts, and TradingAgents integration patches.

The upstream TradingAgents project is research software and is not financial advice. Our work does not add real brokerage execution.

## Secrets

Never commit:

- `.env` or `.env.*` values
- provider API keys
- VS Code gateway tokens
- local credentials
- generated local caches
- private model credentials
- customer data or proprietary data

If examples are needed, use placeholders only.

## VS Code Model Gateway

The gateway must default to a local-only security posture:

- Bind to `127.0.0.1`, not all interfaces.
- Generate a random token per session or per configured trusted client.
- Do not enable permissive CORS by default.
- Start only through explicit user action in VS Code.
- Make status visible to the user while running.
- Provide a clear stop command.
- Do not log full prompts or responses by default if they may contain sensitive data.

## Model Access

VS Code model access may require user consent and may be subject to quota or policy limits. The extension should surface these states clearly instead of hiding them behind generic failures.

## Tool Calling

Tool calling is a trust boundary.

- Tools should be explicitly registered and permissioned.
- App-specific tools should execute in the owning app process unless there is a clear reason to run them in the extension.
- Tool arguments and outputs should be logged carefully and redacted when sensitive.
- Dangerous tools such as shell execution, file writes, network calls, and credential access should require explicit design review.

## Trading And Financial Output

TradingAgents outputs are research artifacts, not investment advice or automated trading instructions. Do not present generated decisions as guaranteed profitable or suitable for real trading without human review.

## Reporting Issues

Until this project has its own repository policy, report security issues directly to the project owner instead of opening public issues containing sensitive details.
