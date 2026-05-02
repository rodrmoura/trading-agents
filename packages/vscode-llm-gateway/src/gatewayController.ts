import { createServer, type Server } from "node:http";
import { randomBytes } from "node:crypto";
import { createRequestHandler } from "./httpRouter";
import { createEmptyModelService, type GatewayModelService } from "./modelService";
import type {
  GatewayHealthResponse,
  GatewayLifecycleState,
  GatewayStartResult,
  GatewayStatus,
  GatewayStopReason,
  GatewayStopResult,
} from "./types";

const DEFAULT_HOST = "127.0.0.1";
const DEFAULT_VERSION = "0.0.1";

interface GatewayRuntime {
  server: Server | null;
  host: string | null;
  port: number | null;
  token: string | null;
  startedAt: string | null;
  state: GatewayLifecycleState;
}

export interface GatewayController {
  readonly start: () => Promise<GatewayStartResult>;
  readonly stop: (reason?: GatewayStopReason) => Promise<GatewayStopResult>;
  readonly getStatus: () => GatewayStatus;
  readonly getHealth: () => GatewayHealthResponse | null;
  readonly getToken: () => string | null;
}

export interface GatewayControllerOptions {
  readonly modelService?: GatewayModelService;
}

function createInitialRuntime(): GatewayRuntime {
  return {
    server: null,
    host: null,
    port: null,
    token: null,
    startedAt: null,
    state: "stopped",
  };
}

function toStatus(runtime: GatewayRuntime): GatewayStatus {
  return {
    state: runtime.state,
    version: DEFAULT_VERSION,
    host: runtime.host,
    port: runtime.port,
    startedAt: runtime.startedAt,
    auth: "bearer",
  };
}

function toHealth(runtime: GatewayRuntime): GatewayHealthResponse | null {
  if (runtime.state !== "running" || !runtime.host || runtime.port === null || !runtime.startedAt) {
    return null;
  }

  return {
    status: "ok",
    version: DEFAULT_VERSION,
    host: runtime.host,
    port: runtime.port,
    startedAt: runtime.startedAt,
    auth: "bearer",
  };
}

function clearRunningDetails(runtime: GatewayRuntime): void {
  runtime.server = null;
  runtime.host = null;
  runtime.port = null;
  runtime.token = null;
  runtime.startedAt = null;
}

async function closeServer(server: Server): Promise<void> {
  await new Promise<void>((resolve) => {
    server.close(() => {
      resolve();
    });
  });
}

export function createGatewayController(options: GatewayControllerOptions = {}): GatewayController {
  const runtime = createInitialRuntime();
  const modelService = options.modelService ?? createEmptyModelService();
  const activeChatControllers = new Set<AbortController>();

  let startPromise: Promise<GatewayStartResult> | null = null;
  let stopPromise: Promise<GatewayStopResult> | null = null;

  function registerChatRequest(): { signal: AbortSignal; abort: () => void; unregister: () => void } {
    const controller = new AbortController();
    activeChatControllers.add(controller);

    let unregistered = false;

    return {
      signal: controller.signal,
      abort: (): void => {
        controller.abort();
      },
      unregister: (): void => {
        if (unregistered) {
          return;
        }

        unregistered = true;
        activeChatControllers.delete(controller);
      },
    };
  }

  function abortActiveChatRequests(): void {
    for (const controller of activeChatControllers) {
      controller.abort();
    }

    activeChatControllers.clear();
  }

  async function stop(reason: GatewayStopReason = "command"): Promise<GatewayStopResult> {
    void reason;

    if (runtime.state === "stopped") {
      return {
        outcome: "already_stopped",
        status: toStatus(runtime),
      };
    }

    if (runtime.state === "stopping") {
      if (stopPromise) {
        return stopPromise;
      }

      return {
        outcome: "already_stopped",
        status: toStatus(runtime),
      };
    }

    runtime.state = "stopping";
    runtime.token = null;
    abortActiveChatRequests();

    const server = runtime.server;

    stopPromise = (async (): Promise<GatewayStopResult> => {
      try {
        if (server) {
          await closeServer(server);
        }
      } finally {
        abortActiveChatRequests();
        clearRunningDetails(runtime);
        runtime.state = "stopped";
      }

      return {
        outcome: "stopped",
        status: toStatus(runtime),
      };
    })();

    try {
      return await stopPromise;
    } finally {
      stopPromise = null;
    }
  }

  async function start(): Promise<GatewayStartResult> {
    if (runtime.state === "running") {
      return {
        outcome: "already_running",
        status: toStatus(runtime),
      };
    }

    if (runtime.state === "starting") {
      if (startPromise) {
        return startPromise;
      }

      return {
        outcome: "starting",
        status: toStatus(runtime),
      };
    }

    if (runtime.state === "stopping") {
      return {
        outcome: "stopping",
        status: toStatus(runtime),
      };
    }

    runtime.state = "starting";

    startPromise = (async (): Promise<GatewayStartResult> => {
      const server = createServer(
        createRequestHandler({
          getHealth: () => toHealth(runtime),
          getState: () => runtime.state,
          tokenProvider: () => runtime.token,
          modelService,
          registerChatRequest,
          stopGateway: async () => {
            await stop("shutdown");
          },
        })
      );

      try {
        await new Promise<void>((resolve, reject) => {
          const onError = (error: Error): void => {
            server.removeListener("listening", onListening);
            reject(error);
          };

          const onListening = (): void => {
            server.removeListener("error", onError);
            resolve();
          };

          server.once("error", onError);
          server.once("listening", onListening);
          server.listen(0, DEFAULT_HOST);
        });

        const address = server.address();
        if (!address || typeof address === "string") {
          throw new Error("Gateway bound with unsupported address format.");
        }

        runtime.server = server;
        runtime.host = address.address;
        runtime.port = address.port;
        runtime.startedAt = new Date().toISOString();
        // Token is generated only after successful bind to host+port.
        runtime.token = randomBytes(32).toString("base64url");
        runtime.state = "running";

        return {
          outcome: "started",
          status: toStatus(runtime),
        };
      } catch {
        if (server.listening) {
          await closeServer(server);
        }

        runtime.state = "failed";
        runtime.token = null;
        clearRunningDetails(runtime);
        runtime.state = "stopped";

        return {
          outcome: "failed",
          status: toStatus(runtime),
        };
      }
    })();

    try {
      return await startPromise;
    } finally {
      startPromise = null;
    }
  }

  return {
    start,
    stop,
    getStatus: () => toStatus(runtime),
    getHealth: () => toHealth(runtime),
    getToken: () => runtime.token,
  };
}