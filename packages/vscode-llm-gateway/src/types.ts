export type GatewayLifecycleState = "stopped" | "starting" | "running" | "stopping" | "failed";

export type GatewayStopReason = "command" | "shutdown" | "deactivate" | "internal";

export interface GatewayStatus {
  readonly state: GatewayLifecycleState;
  readonly version: string;
  readonly host: string | null;
  readonly port: number | null;
  readonly startedAt: string | null;
  readonly auth: "bearer";
}

export interface GatewayHealthResponse {
  readonly status: "ok";
  readonly version: string;
  readonly host: string;
  readonly port: number;
  readonly startedAt: string;
  readonly auth: "bearer";
}

export interface GatewayStartResult {
  readonly outcome: "started" | "already_running" | "starting" | "stopping" | "failed";
  readonly status: GatewayStatus;
}

export interface GatewayStopResult {
  readonly outcome: "stopped" | "already_stopped";
  readonly status: GatewayStatus;
}