# Gateway G1 Smoke

Purpose: produce the live VS Code runtime evidence required by the G1 gate before Phase 2 starts.

This runbook is intentionally manual because the gateway token may be disclosed only through the explicit VS Code `Copy Token` command or notification action.

## Prerequisites

- `packages/vscode-llm-gateway` compiles and tests pass.
- VS Code can access at least one Language Model API model.
- Open this repository at the `TradingAgents/` root.

## Launch The Extension Host

From the repository root:

```powershell
code --new-window --extensionDevelopmentPath "C:\VSCode\Tauric\TradingAgents\packages\vscode-llm-gateway" "C:\VSCode\Tauric\TradingAgents"
```

In the newest Extension Development Host window, use the VS Code Command Palette, not a terminal prompt:

1. Press `Ctrl+Shift+P` or `F1`.
2. Type `TradingAgents Gateway: Start` and select it. Do not paste this text into PowerShell.
3. If using Quick Open with `Ctrl+P`, type `>TradingAgents Gateway: Start`.
4. Record the displayed `127.0.0.1:<port>` value.
5. Click `Copy Token`, or run `TradingAgents Gateway: Copy Token` from the Command Palette.

## Smoke Commands

In a PowerShell terminal, set the port and token:

```powershell
$Port = <port-from-notification>
$Token = Get-Clipboard
$Headers = @{ Authorization = "Bearer $Token" }
```

Public health:

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:$Port/health"
```

Authenticated model list:

```powershell
$Models = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:$Port/v1/models" -Headers $Headers
$Models.models | Format-Table id,name,vendor,family,version
$ModelId = $Models.models[0].id
```

Non-stream chat:

```powershell
$Body = @{
  model = $ModelId
  messages = @(@{ role = "user"; content = "Reply with one short sentence." })
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:$Port/v1/chat/completions" -Headers $Headers -ContentType "application/json" -Body $Body
```

SSE streaming chat:

```powershell
$StreamBody = @{
  model = $ModelId
  messages = @(@{ role = "user"; content = "Count from one to three." })
} | ConvertTo-Json -Depth 5

Invoke-WebRequest -Method Post -Uri "http://127.0.0.1:$Port/v1/chat/completions/stream" -Headers $Headers -ContentType "application/json" -Body $StreamBody
```

Stop through authenticated shutdown:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:$Port/shutdown" -Headers $Headers
```

## Pass Criteria

- Extension starts the gateway through the explicit command.
- `/health` returns public status without a token.
- `/v1/models` returns at least one model, or a clear documented model-access blocker.
- Non-stream chat succeeds, or fails with a documented model-access blocker.
- Streaming response uses SSE `chunk` and `done` events and does not emit `[DONE]`.
- Gateway stops cleanly through shutdown or the VS Code stop command.

Record the command outcomes in `docs/EXPERIMENT_LOG.md` before accepting G1.
