# TradingAgents VS Code Provider Smoke

Purpose: verify the TradingAgents `vscode` provider boundary can construct a gateway-backed LangChain model, optionally make one direct chat call through a running VS Code gateway, and provide the P3.3c full-graph harness command. P3.3b adds mocked non-streaming native tool-call roundtrip support through the gateway, SDK, and LangChain adapter; P3.3c live proof passed once the full-graph command exited successfully against a real gateway/model.

## Prerequisites

- Open this repository at `C:\VSCode\Tauric\TradingAgents`.
- Start from an activated repo `.venv`, or use the explicit `$Python` path below.
- Start the VS Code gateway and copy the gateway token by following [Gateway G1 Smoke](gateway-g1-smoke.md). The token should come from the VS Code `Copy Token` action or command.
- Confirm VS Code can access at least one Language Model API model.

Package-local SDK and LangChain adapter preflight:

```powershell
Set-Location "C:\VSCode\Tauric\TradingAgents"
$Python = "C:\VSCode\Tauric\TradingAgents\.venv\Scripts\python.exe"
& $Python -m pip install -e "packages/llm-gateway-python[langchain]"
& $Python -c "import llm_gateway, llm_gateway.langchain_adapter; print('llm-gateway LangChain adapter import OK')"
```

## Configure The Gateway Environment

Use the port shown by the gateway start notification. Keep the token in process environment only; do not paste token literals into docs, scripts, commits, or issue comments.

```powershell
$Port = <port-from-notification>
$env:TRADINGAGENTS_VSCODE_GATEWAY_URL = "http://127.0.0.1:$Port"
$env:TRADINGAGENTS_VSCODE_GATEWAY_TOKEN = Get-Clipboard
$Headers = @{ Authorization = "Bearer $env:TRADINGAGENTS_VSCODE_GATEWAY_TOKEN" }
```

## Select A Model

List gateway-owned model IDs and choose one `id` value:

```powershell
$Models = Invoke-RestMethod -Method Get -Uri "$env:TRADINGAGENTS_VSCODE_GATEWAY_URL/v1/models" -Headers $Headers
$Models.models | Format-Table id,name,vendor,family,version
$ModelId = $Models.models[0].id
```

## Run The Provider Smoke

Construction-only mode verifies the TradingAgents factory path, the `vscode` provider, and the package-local LangChain adapter without making a model call:

```powershell
& $Python scripts/smoke_vscode_provider.py --model $ModelId --no-invoke
```

Default mode constructs the model and makes one direct `llm.invoke(...)` call:

```powershell
& $Python scripts/smoke_vscode_provider.py --model $ModelId
```

Use a custom direct prompt when needed:

```powershell
& $Python scripts/smoke_vscode_provider.py --model $ModelId --prompt "Reply with one short sentence."
```

The script reads `TRADINGAGENTS_VSCODE_GATEWAY_URL` and `TRADINGAGENTS_VSCODE_GATEWAY_TOKEN`, requires a nonblank `--model`, trims blank values before provider construction, and redacts the configured token from printed exception and assistant-response text.

## Run The Full-Graph Harness For P3.3c

This is the repeatable command path for P3.3c live proof.

Minimal one-analyst run using the default ticker, date, and one debate/risk round:

```powershell
& $Python scripts/smoke_vscode_tradingagents_graph.py --model $ModelId
```

Explicit run with an isolated output root:

```powershell
$OutputRoot = Join-Path $env:TEMP "tradingagents-vscode-graph-smoke"
& $Python scripts/smoke_vscode_tradingagents_graph.py --model $ModelId --ticker NVDA --trade-date 2024-05-10 --analysts market --output-dir $OutputRoot --max-debate-rounds 1 --max-risk-discuss-rounds 1
```

The full-graph harness reads the same gateway environment variables as the direct provider smoke, validates inputs before graph construction, configures both TradingAgents model slots to the selected opaque gateway model ID, disables checkpointing, and writes results, cache, and memory under the output root. If `--output-dir` is omitted, the script creates a persistent temp directory with the `tradingagents-vscode-graph-smoke-` prefix.

Both `--max-debate-rounds` and `--max-risk-discuss-rounds` must be integers `>= 1`, matching the current graph defaults used by this smoke path. Success requires nonblank selected analyst report fields plus `investment_plan`, `trader_investment_plan`, `final_trade_decision`, and a nonblank processed decision from `propagate()`. The script prints only concise evidence, redacts the configured token, and reports character counts for checked final-state fields rather than full report bodies.

## Current Boundary

P3.3b supports mocked non-streaming `prompt | llm.bind_tools(tools)` roundtrips: the gateway can return native assistant `toolCalls`, the Python SDK/LangChain adapter can expose them as LangChain `AIMessage.tool_calls`, and a local LangGraph `ToolNode` can send tool results back as native `role: "tool"` messages on the next non-stream turn.

P3.3c live proof passed on 2026-05-02 with a running VS Code gateway and model `claude-opus-4.6-1m`. The direct provider smoke validated provider construction and a direct LangChain `invoke()` call, and the full-graph harness validated a market-only `NVDA` run through Research Manager, Trader, and Portfolio Manager. Those downstream nodes used documented free-text fallback because `with_structured_output(...)` remains unsupported by the native gateway adapter.

## Cleanup

Stop the gateway using [Gateway G1 Smoke](gateway-g1-smoke.md), then clear the process environment values:

```powershell
Remove-Item Env:TRADINGAGENTS_VSCODE_GATEWAY_URL -ErrorAction SilentlyContinue
Remove-Item Env:TRADINGAGENTS_VSCODE_GATEWAY_TOKEN -ErrorAction SilentlyContinue
```
