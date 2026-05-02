import type { GatewayStartResult, GatewayStatus, GatewayStopResult } from "./types";

export const COPY_TOKEN_ACTION = "Copy Token";

export interface InfoMessageSpec {
  readonly message: string;
  readonly actions: readonly string[];
}

function describeListening(status: GatewayStatus): string {
  if (status.host && status.port !== null) {
    return `${status.host}:${status.port}`;
  }

  return "not listening";
}

export function buildStartMessage(result: GatewayStartResult): InfoMessageSpec {
  switch (result.outcome) {
    case "started":
      return {
        message: `TradingAgents Gateway started on ${describeListening(result.status)}.`,
        actions: [COPY_TOKEN_ACTION],
      };
    case "already_running":
      return {
        message: `TradingAgents Gateway is already running on ${describeListening(result.status)}.`,
        actions: [COPY_TOKEN_ACTION],
      };
    case "starting":
      return {
        message: "TradingAgents Gateway is already starting.",
        actions: [],
      };
    case "stopping":
      return {
        message: "TradingAgents Gateway is currently stopping. Try start again in a moment.",
        actions: [],
      };
    case "failed":
      return {
        message: "TradingAgents Gateway failed to start.",
        actions: [],
      };
    default:
      return {
        message: "TradingAgents Gateway start command completed.",
        actions: [],
      };
  }
}

export function buildStopMessage(result: GatewayStopResult): InfoMessageSpec {
  if (result.outcome === "already_stopped") {
    return {
      message: "TradingAgents Gateway is already stopped.",
      actions: [],
    };
  }

  return {
    message: "TradingAgents Gateway stopped.",
    actions: [],
  };
}

export function buildStatusMessage(status: GatewayStatus): InfoMessageSpec {
  if (status.state === "running") {
    return {
      message: `TradingAgents Gateway status: running on ${describeListening(status)} (auth: bearer).`,
      actions: [COPY_TOKEN_ACTION],
    };
  }

  return {
    message: `TradingAgents Gateway status: ${status.state}.`,
    actions: [],
  };
}

export interface CopyTokenResult {
  readonly copied: boolean;
  readonly token: string | null;
  readonly message: string;
}

export function buildCopyTokenResult(token: string | null): CopyTokenResult {
  if (!token) {
    return {
      copied: false,
      token: null,
      message: "TradingAgents Gateway is not running. No token available to copy.",
    };
  }

  return {
    copied: true,
    token,
    message: "TradingAgents Gateway token copied to clipboard.",
  };
}