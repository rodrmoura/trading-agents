# Roadmap

This file owns medium-term governance priorities and parked work. Product-specific roadmap details can live in project planning docs and should point here only for workflow priorities.

## Now

- Treat G0 governance/environment work as approved for GitHub commit/push.
- Treat Phase 1 gateway package implementation as complete (P1.1-P1.5 implemented and reviewed).
- Treat G1 live VS Code gateway smoke as accepted for Phase 2 entry.
- Treat P2.1 Python gateway SDK package skeleton as complete and review-approved.
- Treat P2.2 Python gateway SDK client and typed errors as complete and review-approved.
- Treat P2.3 Python gateway SDK streaming client as complete and review-approved.
- Treat P2.4 Python gateway SDK LangChain-compatible adapter as complete and review-approved.
- Treat P3.1 TradingAgents provider integration audit as complete.
- Treat P3.2 thin TradingAgents `vscode` provider boundary as complete and review-approved.
- Treat P3.3a direct TradingAgents `vscode` provider smoke/runbook as complete and review-approved.
- Treat P3.3b mocked non-stream native tool-call roundtrip as complete and review-approved.
- Treat P3.3c full-graph smoke harness readiness and live full-graph smoke proof as complete.
- Treat P3.4 structured-output adapter compatibility as complete and review-approved.
- Treat post-P3.4 live structured-output smoke through a real VS Code model as complete.

## Next

- Keep using the phase execution queue in `docs/planning/codex-task-packets.md` for handoffs.
- Choose the next `vscode` provider slice: gateway-native structured-output contract decisions, model capability advertisement, or tool-enabled streaming.

## Later

- Add automated metadata or link checks if this workflow repeats.
- Add CI or pre-commit checks only when the repository adopts them explicitly.

## Parked

- Exact lint/typecheck/build command ownership is parked until commands exist or are confirmed.
