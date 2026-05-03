import type { IncomingMessage, ServerResponse } from "node:http";
import { randomUUID } from "node:crypto";
import { ensureAuthorized, type TokenProvider } from "./auth";
import { createNativeError, sendJson, sendNativeError } from "./errors";
import {
  mapLanguageModelErrorCode,
  type GatewayChatMessage,
  type GatewayChatCompletion,
  type GatewayModelService,
  type GatewayChatRole,
  type GatewayStartedChat,
  type GatewayTool,
  type GatewayToolCall,
} from "./modelService";
import type { GatewayHealthResponse } from "./types";

export interface RouterRuntime {
  readonly getHealth: () => GatewayHealthResponse | null;
  readonly getState: () => "stopped" | "starting" | "running" | "stopping" | "failed";
  readonly tokenProvider: TokenProvider;
  readonly modelService: GatewayModelService;
  readonly stopGateway: () => Promise<void>;
  readonly registerChatRequest: () => RegisteredChatRequest;
}

export interface RegisteredChatRequest {
  readonly signal: AbortSignal;
  readonly abort: () => void;
  readonly unregister: () => void;
}

type RouteHandler = (request: IncomingMessage, response: ServerResponse) => void | Promise<void>;

const MAX_CHAT_BODY_BYTES = 1024 * 1024;

const CHAT_REQUEST_ALLOWED_KEYS = new Set(["model", "messages", "requestId", "metadata", "tools"]);
const TEXT_CHAT_MESSAGE_ALLOWED_KEYS = new Set(["role", "content"]);
const ASSISTANT_CHAT_MESSAGE_ALLOWED_KEYS = new Set(["role", "content", "toolCalls"]);
const TOOL_CHAT_MESSAGE_ALLOWED_KEYS = new Set(["role", "toolCallId", "content"]);
const TOOL_OBJECT_ALLOWED_KEYS = new Set(["name", "description", "inputSchema"]);
const TOOL_CALL_ALLOWED_KEYS = new Set(["id", "name", "input"]);
const CHAT_ROLES = new Set<GatewayChatRole>(["system", "user", "assistant", "tool"]);

interface ParsedChatRequest {
  readonly model: string;
  readonly messages: readonly GatewayChatMessage[];
  readonly tools?: readonly GatewayTool[];
}

interface ChatResponseBody {
  readonly id: string;
  readonly model: string;
  readonly created: string;
  readonly message: {
    readonly role: "assistant";
    readonly content: string;
    readonly toolCalls?: readonly GatewayToolCall[];
  };
  readonly finishReason: "stop" | "toolCalls";
  readonly usage: null;
  readonly metadata: Record<string, never>;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasText(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function hasOnlyKeys(value: Record<string, unknown>, allowedKeys: ReadonlySet<string>): boolean {
  for (const key of Object.keys(value)) {
    if (!allowedKeys.has(key)) {
      return false;
    }
  }

  return true;
}

function parseToolCall(value: unknown): GatewayToolCall | null {
  if (!isRecord(value) || !hasOnlyKeys(value, TOOL_CALL_ALLOWED_KEYS)) {
    return null;
  }

  if (!hasText(value.id) || !hasText(value.name) || !isRecord(value.input)) {
    return null;
  }

  return {
    id: value.id,
    name: value.name,
    input: value.input,
  };
}

function parseToolCalls(value: unknown): readonly GatewayToolCall[] | null {
  if (!Array.isArray(value) || value.length === 0) {
    return null;
  }

  const toolCalls: GatewayToolCall[] = [];
  for (const item of value) {
    const toolCall = parseToolCall(item);
    if (!toolCall) {
      return null;
    }

    toolCalls.push(toolCall);
  }

  return toolCalls;
}

function parseTool(value: unknown): GatewayTool | null {
  if (!isRecord(value) || !hasOnlyKeys(value, TOOL_OBJECT_ALLOWED_KEYS)) {
    return null;
  }

  if (!hasText(value.name) || typeof value.description !== "string") {
    return null;
  }

  if (value.inputSchema !== undefined && !isRecord(value.inputSchema)) {
    return null;
  }

  return value.inputSchema === undefined
    ? {
        name: value.name,
        description: value.description,
      }
    : {
        name: value.name,
        description: value.description,
        inputSchema: value.inputSchema,
      };
}

function parseTools(value: unknown): readonly GatewayTool[] | null {
  if (!Array.isArray(value) || value.length === 0) {
    return null;
  }

  const tools: GatewayTool[] = [];
  for (const item of value) {
    const tool = parseTool(item);
    if (!tool) {
      return null;
    }

    tools.push(tool);
  }

  return tools;
}

function parseChatMessage(item: unknown): GatewayChatMessage | null {
  if (!isRecord(item)) {
    return null;
  }

  const role = item.role;
  if (typeof role !== "string" || !CHAT_ROLES.has(role as GatewayChatRole)) {
    return null;
  }

  if (role === "tool") {
    if (!hasOnlyKeys(item, TOOL_CHAT_MESSAGE_ALLOWED_KEYS)) {
      return null;
    }

    if (!hasText(item.toolCallId) || typeof item.content !== "string") {
      return null;
    }

    return {
      role: "tool",
      toolCallId: item.toolCallId,
      content: item.content,
    };
  }

  if (role === "assistant") {
    if (!hasOnlyKeys(item, ASSISTANT_CHAT_MESSAGE_ALLOWED_KEYS) || typeof item.content !== "string") {
      return null;
    }

    if (item.toolCalls !== undefined) {
      const toolCalls = parseToolCalls(item.toolCalls);
      if (!toolCalls) {
        return null;
      }

      return {
        role: "assistant",
        content: item.content,
        toolCalls,
      };
    }

    return hasText(item.content)
      ? {
          role: "assistant",
          content: item.content,
        }
      : null;
  }

  if (!hasOnlyKeys(item, TEXT_CHAT_MESSAGE_ALLOWED_KEYS) || !hasText(item.content)) {
    return null;
  }

  return {
    role: role as "system" | "user",
    content: item.content,
  };
}

function parseContentLength(contentLengthHeader: string | undefined): number | null {
  if (!contentLengthHeader) {
    return null;
  }

  const parsed = Number(contentLengthHeader.trim());
  if (!Number.isFinite(parsed) || parsed < 0) {
    return null;
  }

  return parsed;
}

function isJsonContentType(request: IncomingMessage): boolean {
  const header = request.headers["content-type"];
  if (typeof header !== "string") {
    return false;
  }

  const [mediaType] = header.split(";", 1);
  if (!mediaType) {
    return false;
  }

  return mediaType.trim().toLowerCase() === "application/json";
}

async function readJsonBody(request: IncomingMessage): Promise<string | null> {
  let totalBytes = 0;
  const chunks: Buffer[] = [];

  for await (const chunk of request) {
    const chunkBuffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    totalBytes += chunkBuffer.byteLength;

    if (totalBytes > MAX_CHAT_BODY_BYTES) {
      return null;
    }

    chunks.push(chunkBuffer);
  }

  if (chunks.length === 0) {
    return "";
  }

  return Buffer.concat(chunks).toString("utf8");
}

function parseChatRequest(body: unknown): ParsedChatRequest | null {
  if (!isRecord(body)) {
    return null;
  }

  for (const key of Object.keys(body)) {
    if (!CHAT_REQUEST_ALLOWED_KEYS.has(key)) {
      return null;
    }
  }

  if (!hasText(body.model)) {
    return null;
  }

  if (!Array.isArray(body.messages) || body.messages.length === 0) {
    return null;
  }

  if (body.requestId !== undefined && !hasText(body.requestId)) {
    return null;
  }

  if (body.metadata !== undefined && !isRecord(body.metadata)) {
    return null;
  }

  const tools = body.tools === undefined ? undefined : parseTools(body.tools);
  if (body.tools !== undefined && !tools) {
    return null;
  }

  const messages: GatewayChatMessage[] = [];

  for (const item of body.messages) {
    const message = parseChatMessage(item);
    if (!message) {
      return null;
    }

    messages.push(message);
  }

  return {
    model: body.model,
    messages,
    ...(tools ? { tools } : {}),
  };
}

async function parseAndValidateChatRequest(
  request: IncomingMessage,
  response: ServerResponse
): Promise<ParsedChatRequest | null> {
  if (!isJsonContentType(request)) {
    sendNativeError(response, "unsupported_media_type");
    return null;
  }

  const contentLengthHeader = request.headers["content-length"];
  const contentLength = parseContentLength(
    typeof contentLengthHeader === "string" ? contentLengthHeader : undefined
  );
  if (contentLength !== null && contentLength > MAX_CHAT_BODY_BYTES) {
    sendNativeError(response, "validation_error");
    return null;
  }

  const bodyText = await readJsonBody(request);
  if (bodyText === null) {
    sendNativeError(response, "validation_error");
    return null;
  }

  if (bodyText.trim().length === 0) {
    sendNativeError(response, "invalid_json");
    return null;
  }

  let parsedBody: unknown;
  try {
    parsedBody = JSON.parse(bodyText);
  } catch {
    sendNativeError(response, "invalid_json");
    return null;
  }

  const parsedRequest = parseChatRequest(parsedBody);
  if (!parsedRequest) {
    sendNativeError(response, "validation_error");
    return null;
  }

  return parsedRequest;
}

function normalizeCompletion(completion: GatewayChatCompletion): { content: string; toolCalls?: readonly GatewayToolCall[] } {
  if (typeof completion === "string") {
    return { content: completion };
  }

  return {
    content: completion.message.content,
    ...(completion.message.toolCalls && completion.message.toolCalls.length > 0
      ? { toolCalls: completion.message.toolCalls }
      : {}),
  };
}

function buildChatResponse(model: string, completion: GatewayChatCompletion): ChatResponseBody {
  const message = normalizeCompletion(completion);

  return {
    id: `gwchat_${randomUUID()}`,
    model,
    created: new Date().toISOString(),
    message: {
      role: "assistant",
      content: message.content,
      ...(message.toolCalls ? { toolCalls: message.toolCalls } : {}),
    },
    finishReason: message.toolCalls ? "toolCalls" : "stop",
    usage: null,
    metadata: {},
  };
}

function hasToolContext(request: ParsedChatRequest): boolean {
  return Boolean(
    (request.tools && request.tools.length > 0) ||
      request.messages.some(
        (message) => message.role === "tool" || (message.toolCalls && message.toolCalls.length > 0)
      )
  );
}

function canWriteResponse(response: ServerResponse): boolean {
  return !response.destroyed && !response.writableEnded;
}

function safeWriteResponse(response: ServerResponse, chunk: string): boolean {
  if (!canWriteResponse(response)) {
    return false;
  }

  try {
    response.write(chunk);
    return true;
  } catch {
    return false;
  }
}

function safeEndResponse(response: ServerResponse): void {
  if (!canWriteResponse(response)) {
    return;
  }

  try {
    response.end();
  } catch {
    // Ignore disconnect races while ending the response.
  }
}

function writeSseEvent(response: ServerResponse, eventName: "chunk" | "done" | "error", payload: unknown): boolean {
  return safeWriteResponse(response, `event: ${eventName}\ndata: ${JSON.stringify(payload)}\n\n`);
}

function commitSseHeaders(response: ServerResponse): boolean {
  if (!canWriteResponse(response)) {
    return false;
  }

  response.statusCode = 200;
  response.setHeader("Content-Type", "text/event-stream");
  response.setHeader("Cache-Control", "no-cache");
  response.setHeader("Connection", "keep-alive");

  try {
    response.flushHeaders();
  } catch {
    return false;
  }

  response.on("error", () => {
    // Suppress destroyed stream races while writing SSE events.
  });

  return true;
}

function handleChatFailure(response: ServerResponse, error: unknown): void {
  if (!canWriteResponse(response)) {
    return;
  }

  sendNativeError(response, mapLanguageModelErrorCode(error));
}

function rejectJsonBodyOnShutdown(request: IncomingMessage, response: ServerResponse): boolean {
  const contentLength = request.headers["content-length"];
  if (typeof contentLength === "string") {
    const parsed = Number(contentLength);
    if (Number.isFinite(parsed) && parsed > 0) {
      sendNativeError(response, "validation_error");
      return false;
    }
  }

  const transferEncoding = request.headers["transfer-encoding"];
  if (typeof transferEncoding === "string" && transferEncoding.trim().length > 0) {
    sendNativeError(response, "validation_error");
    return false;
  }

  return true;
}

async function handleModelsRequest(
  request: IncomingMessage,
  response: ServerResponse,
  runtime: RouterRuntime
): Promise<void> {
  if (!ensureAuthorized(request, response, runtime.tokenProvider)) {
    return;
  }

  if (request.method !== "GET") {
    sendNativeError(response, "method_not_allowed");
    return;
  }

  try {
    const models = await runtime.modelService.listModels();
    sendJson(response, 200, { models });
  } catch (error) {
    sendNativeError(response, mapLanguageModelErrorCode(error));
  }
}

async function handleChatCompletionsRequest(
  request: IncomingMessage,
  response: ServerResponse,
  runtime: RouterRuntime
): Promise<void> {
  if (!ensureAuthorized(request, response, runtime.tokenProvider)) {
    return;
  }

  if (request.method !== "POST") {
    sendNativeError(response, "method_not_allowed");
    return;
  }

  const parsedRequest = await parseAndValidateChatRequest(request, response);
  if (!parsedRequest) {
    return;
  }

  const registration = runtime.registerChatRequest();
  let completed = false;

  const abortOnClose = (): void => {
    if (!completed) {
      registration.abort();
    }
  };

  request.once("close", abortOnClose);
  response.once("close", abortOnClose);

  try {
    const completion = await runtime.modelService.completeChat(parsedRequest, registration.signal);
    if (!canWriteResponse(response)) {
      completed = true;
      return;
    }

    completed = true;
    sendJson(response, 200, buildChatResponse(parsedRequest.model, completion));
  } catch (error) {
    const mappedCode = mapLanguageModelErrorCode(error);
    if (mappedCode === "cancelled") {
      if (canWriteResponse(response)) {
        sendNativeError(response, "cancelled");
      }

      completed = true;
      return;
    }

    completed = true;
    handleChatFailure(response, error);
  } finally {
    request.removeListener("close", abortOnClose);
    response.removeListener("close", abortOnClose);
    registration.unregister();
  }
}

async function handleChatCompletionsStreamRequest(
  request: IncomingMessage,
  response: ServerResponse,
  runtime: RouterRuntime
): Promise<void> {
  if (!ensureAuthorized(request, response, runtime.tokenProvider)) {
    return;
  }

  if (request.method !== "POST") {
    sendNativeError(response, "method_not_allowed");
    return;
  }

  const parsedRequest = await parseAndValidateChatRequest(request, response);
  if (!parsedRequest) {
    return;
  }

  if (hasToolContext(parsedRequest)) {
    sendNativeError(response, "validation_error");
    return;
  }

  const registration = runtime.registerChatRequest();
  let completed = false;
  let startedChat: GatewayStartedChat | null = null;
  let sseCommitted = false;
  let sentStreamError = false;

  const abortOnClose = (): void => {
    if (!completed) {
      registration.abort();
    }
  };

  request.once("close", abortOnClose);
  response.once("close", abortOnClose);

  try {
    startedChat = await runtime.modelService.startChat(parsedRequest, registration.signal);

    if (registration.signal.aborted) {
      startedChat.dispose();
      startedChat = null;
      completed = true;
      if (canWriteResponse(response)) {
        sendNativeError(response, "cancelled");
      }

      return;
    }

    if (!commitSseHeaders(response)) {
      registration.abort();
      completed = true;
      return;
    }

    sseCommitted = true;

    for await (const chunk of startedChat.text) {
      if (chunk.length === 0) {
        continue;
      }

      if (!writeSseEvent(response, "chunk", { text: chunk })) {
        registration.abort();
        completed = true;
        return;
      }
    }

    completed = true;
    writeSseEvent(response, "done", {
      id: `gwchat_${randomUUID()}`,
      model: parsedRequest.model,
      finishReason: "stop",
      metadata: {},
    });
  } catch (error) {
    const mappedCode = mapLanguageModelErrorCode(error);

    if (sseCommitted) {
      completed = true;

      if (!sentStreamError && canWriteResponse(response)) {
        sentStreamError = true;
        writeSseEvent(response, "error", createNativeError(mappedCode).body);
      }

      return;
    }

    completed = true;
    if (mappedCode === "cancelled") {
      if (canWriteResponse(response)) {
        sendNativeError(response, "cancelled");
      }

      return;
    }

    handleChatFailure(response, error);
  } finally {
    request.removeListener("close", abortOnClose);
    response.removeListener("close", abortOnClose);

    if (startedChat) {
      startedChat.dispose();
    }

    registration.unregister();
    safeEndResponse(response);
  }
}

function buildRoutes(runtime: RouterRuntime): Map<string, RouteHandler> {
  return new Map<string, RouteHandler>([
    [
      "/health",
      (request: IncomingMessage, response: ServerResponse): void => {
        if (request.method !== "GET") {
          sendNativeError(response, "method_not_allowed");
          return;
        }

        const health = runtime.getHealth();
        if (!health) {
          sendNativeError(response, "gateway_not_ready");
          return;
        }

        sendJson(response, 200, health);
      },
    ],
    [
      "/shutdown",
      (request: IncomingMessage, response: ServerResponse): void => {
        if (request.method !== "POST") {
          sendNativeError(response, "method_not_allowed");
          return;
        }

        if (!ensureAuthorized(request, response, runtime.tokenProvider)) {
          return;
        }

        if (!rejectJsonBodyOnShutdown(request, response)) {
          return;
        }

        if (runtime.getState() === "stopped") {
          sendNativeError(response, "gateway_not_ready");
          return;
        }

        sendJson(response, 200, { ok: true, message: "Gateway shutdown initiated." });
        // Wait for the response stream to finish so the caller receives a complete response.
        response.once("finish", () => {
          void runtime.stopGateway();
        });
      },
    ],
    [
      "/v1/models",
      (request: IncomingMessage, response: ServerResponse): Promise<void> => {
        return handleModelsRequest(request, response, runtime);
      },
    ],
    [
      "/v1/chat/completions",
      (request: IncomingMessage, response: ServerResponse): Promise<void> => {
        return handleChatCompletionsRequest(request, response, runtime);
      },
    ],
    [
      "/v1/chat/completions/stream",
      (request: IncomingMessage, response: ServerResponse): Promise<void> => {
        return handleChatCompletionsStreamRequest(request, response, runtime);
      },
    ],
  ]);
}

function normalizePath(request: IncomingMessage): string {
  const requestUrl = request.url ?? "/";
  const withoutQuery = requestUrl.split("?", 1)[0] ?? "/";
  return withoutQuery;
}

export function createRequestHandler(runtime: RouterRuntime): RouteHandler {
  const routes = buildRoutes(runtime);

  return (request: IncomingMessage, response: ServerResponse): void => {
    try {
      const path = normalizePath(request);
      const route = routes.get(path);

      if (!route) {
        sendNativeError(response, "not_found");
        return;
      }

      const maybePromise = route(request, response);
      void Promise.resolve(maybePromise).catch(() => {
        sendNativeError(response, "internal_error");
      });
    } catch {
      sendNativeError(response, "internal_error");
    }
  };
}