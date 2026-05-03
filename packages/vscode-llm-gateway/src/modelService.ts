import type { NativeErrorCode } from "./errors";

export interface GatewayModelCapabilities {
  readonly streaming: boolean;
  readonly toolCalling: boolean;
  readonly structuredOutput: boolean;
}

export interface GatewayModel {
  readonly id: string;
  readonly name: string;
  readonly vendor: string | null;
  readonly family: string | null;
  readonly version: string | null;
  readonly capabilities: GatewayModelCapabilities;
}

export type GatewayChatRole = "system" | "user" | "assistant" | "tool";

export interface GatewayTool {
  readonly name: string;
  readonly description: string;
  readonly inputSchema?: Record<string, unknown>;
}

export interface GatewayToolCall {
  readonly id: string;
  readonly name: string;
  readonly input: Record<string, unknown>;
}

export interface GatewayChatMessage {
  readonly role: GatewayChatRole;
  readonly content: string;
  readonly toolCalls?: readonly GatewayToolCall[];
  readonly toolCallId?: string;
}

export interface GatewayChatRequest {
  readonly model: string;
  readonly messages: readonly GatewayChatMessage[];
  readonly tools?: readonly GatewayTool[];
}

export interface GatewayAssistantMessage {
  readonly role: "assistant";
  readonly content: string;
  readonly toolCalls?: readonly GatewayToolCall[];
}

export interface GatewayChatCompletionBody {
  readonly message: GatewayAssistantMessage;
}

export type GatewayChatCompletion = string | GatewayChatCompletionBody;

export interface GatewayStartedChat {
  readonly text: AsyncIterable<string>;
  readonly dispose: () => void;
}

export interface GatewayModelService {
  readonly listModels: () => Promise<readonly GatewayModel[]>;
  readonly startChat: (request: GatewayChatRequest, signal: AbortSignal) => Promise<GatewayStartedChat>;
  readonly completeChat: (request: GatewayChatRequest, signal: AbortSignal) => Promise<GatewayChatCompletion>;
}

export interface GatewayLanguageModelChatResponse {
  readonly stream?: AsyncIterable<unknown>;
  readonly text: AsyncIterable<string>;
}

export interface GatewayLanguageModel {
  readonly id: string;
  readonly name: string;
  readonly vendor?: string;
  readonly family?: string;
  readonly version?: string;
}

interface GatewayChatCapableLanguageModel {
  readonly sendRequest?: (
    messages: unknown[],
    options?: unknown,
    token?: unknown
  ) => PromiseLike<GatewayLanguageModelChatResponse>;
}

export interface GatewayLanguageModelSource<
  TSelector = Record<string, never>,
  TLanguageModel extends GatewayLanguageModel = GatewayLanguageModel,
> {
  readonly selectChatModels: (selector?: TSelector) => PromiseLike<readonly TLanguageModel[]>;
}

export interface GatewayCancellationSource<TCancellationToken = unknown> {
  readonly token: TCancellationToken;
  readonly cancel: () => void;
  readonly dispose: () => void;
}

export interface GatewayChatRuntime<TMessage = unknown, TCancellationToken = unknown, TTool = unknown> {
  readonly createUserMessage: (content: string) => TMessage;
  readonly createAssistantMessage: (content: string) => TMessage;
  readonly createAssistantToolCallMessage: (
    content: string,
    toolCalls: readonly GatewayToolCall[]
  ) => TMessage;
  readonly createToolResultMessage: (toolCallId: string, content: string) => TMessage;
  readonly createTool: (tool: GatewayTool) => TTool;
  readonly extractTextResponsePart: (part: unknown) => string | null;
  readonly extractToolCallResponsePart: (part: unknown) => GatewayToolCall | null;
  readonly createCancellationSource: () => GatewayCancellationSource<TCancellationToken>;
}

function hasText(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function toOptionalField(value: unknown): string | null {
  return hasText(value) ? value : null;
}

export function mapLanguageModel(model: GatewayLanguageModel): GatewayModel {
  const id = model.id;

  return {
    id,
    name: hasText(model.name) ? model.name : id,
    vendor: toOptionalField(model.vendor),
    family: toOptionalField(model.family),
    version: toOptionalField(model.version),
    capabilities: {
      streaming: true,
      toolCalling: false,
      structuredOutput: false,
    },
  };
}

function getErrorCode(error: unknown): string | null {
  if (typeof error !== "object" || error === null) {
    return null;
  }

  const maybeCode = (error as { code?: unknown }).code;
  if (!hasText(maybeCode)) {
    return null;
  }

  return maybeCode;
}

function isCancellationLike(error: unknown): boolean {
  const code = getErrorCode(error);
  if (code && code.toLowerCase().includes("cancel")) {
    return true;
  }

  if (typeof error !== "object" || error === null) {
    return false;
  }

  const maybeName = (error as { name?: unknown }).name;
  if (hasText(maybeName) && maybeName.toLowerCase().includes("cancel")) {
    return true;
  }

  const maybeMessage = (error as { message?: unknown }).message;
  if (hasText(maybeMessage) && maybeMessage.toLowerCase().includes("cancel")) {
    return true;
  }

  return false;
}

export function mapLanguageModelErrorCode(error: unknown): NativeErrorCode {
  const errorCode = getErrorCode(error);

  switch (errorCode) {
    case "NoPermissions":
      return "model_access_denied";
    case "NotFound":
      return "model_not_found";
    case "Blocked":
      return "quota_or_rate_limited";
    default:
      if (isCancellationLike(error)) {
        return "cancelled";
      }

      return "unknown_model_error";
  }
}

const SYSTEM_MESSAGE_PREFIX = "System instructions:\n";

function createCancellationLikeError(): Error & { code: string } {
  const cancellationError = new Error("The request was cancelled.") as Error & { code: string };
  cancellationError.name = "CancellationError";
  cancellationError.code = "Cancelled";
  return cancellationError;
}

function throwIfAborted(signal: AbortSignal): void {
  if (signal.aborted) {
    throw createCancellationLikeError();
  }
}

function mapToProviderMessage<TMessage>(
  message: GatewayChatMessage,
  runtime: GatewayChatRuntime<TMessage, unknown, unknown>
): TMessage {
  switch (message.role) {
    case "system":
      return runtime.createUserMessage(`${SYSTEM_MESSAGE_PREFIX}${message.content}`);
    case "user":
      return runtime.createUserMessage(message.content);
    case "assistant":
      if (message.toolCalls && message.toolCalls.length > 0) {
        return runtime.createAssistantToolCallMessage(message.content, message.toolCalls);
      }

      return runtime.createAssistantMessage(message.content);
    case "tool":
      return runtime.createToolResultMessage(message.toolCallId ?? "", message.content);
    default:
      // The HTTP layer should already reject unsupported roles.
      return runtime.createUserMessage(message.content);
  }
}

async function collectTextResponse(text: AsyncIterable<string>, signal: AbortSignal): Promise<string> {
  throwIfAborted(signal);

  let content = "";

  for await (const chunk of text) {
    throwIfAborted(signal);

    content += chunk;
  }

  throwIfAborted(signal);

  return content;
}

async function collectResponseParts<TMessage, TCancellationToken, TTool>(
  response: GatewayLanguageModelChatResponse,
  runtime: GatewayChatRuntime<TMessage, TCancellationToken, TTool>,
  signal: AbortSignal
): Promise<GatewayAssistantMessage> {
  throwIfAborted(signal);

  if (!response.stream) {
    return {
      role: "assistant",
      content: await collectTextResponse(response.text, signal),
    };
  }

  let content = "";
  const toolCalls: GatewayToolCall[] = [];

  for await (const part of response.stream) {
    throwIfAborted(signal);

    const text = runtime.extractTextResponsePart(part);
    if (text !== null) {
      content += text;
      continue;
    }

    const toolCall = runtime.extractToolCallResponsePart(part);
    if (toolCall !== null) {
      toolCalls.push(toolCall);
    }
  }

  throwIfAborted(signal);

  if (toolCalls.length > 0) {
    return {
      role: "assistant",
      content,
      toolCalls,
    };
  }

  return {
    role: "assistant",
    content,
  };
}

export function createEmptyModelService(): GatewayModelService {
  return {
    async listModels(): Promise<readonly GatewayModel[]> {
      return [];
    },
    async startChat(): Promise<GatewayStartedChat> {
      throw { code: "NotFound" };
    },
    async completeChat(): Promise<string> {
      throw { code: "NotFound" };
    },
  };
}

export function createVsCodeModelService<
  TSelector = Record<string, never>,
  TLanguageModel extends GatewayLanguageModel = GatewayLanguageModel,
  TMessage = unknown,
  TCancellationToken = unknown,
  TTool = unknown,
>(
  source: GatewayLanguageModelSource<TSelector, TLanguageModel>,
  runtime?: GatewayChatRuntime<TMessage, TCancellationToken, TTool>
): GatewayModelService {
  const sendChatRequest = async (
    request: GatewayChatRequest,
    signal: AbortSignal
  ): Promise<{ response: GatewayLanguageModelChatResponse; dispose: () => void }> => {
    if (!runtime) {
      throw new Error("Gateway chat runtime dependencies are unavailable.");
    }

    throwIfAborted(signal);

    const models = await Promise.resolve(source.selectChatModels({} as TSelector));
    throwIfAborted(signal);

    const selectedModel = models.find((model) => model.id === request.model);
    if (!selectedModel) {
      throw { code: "NotFound" };
    }

    const chatModel = selectedModel as TLanguageModel & GatewayChatCapableLanguageModel;

    if (typeof chatModel.sendRequest !== "function") {
      throw new Error("Selected model does not support chat requests.");
    }

    const sendRequest = chatModel.sendRequest as (
      messages: TMessage[],
      options?: { tools?: TTool[] },
      token?: TCancellationToken
    ) => PromiseLike<GatewayLanguageModelChatResponse>;

    throwIfAborted(signal);

    const cancellationSource = runtime.createCancellationSource();
    const handleAbort = (): void => {
      cancellationSource.cancel();
    };

    signal.addEventListener("abort", handleAbort, { once: true });

    let released = false;
    const release = (): void => {
      if (released) {
        return;
      }

      released = true;
      signal.removeEventListener("abort", handleAbort);
      cancellationSource.dispose();
    };

    try {
      if (signal.aborted) {
        cancellationSource.cancel();
      }
      throwIfAborted(signal);

      const messages = request.messages.map((message) => mapToProviderMessage(message, runtime));
      const options = request.tools && request.tools.length > 0
        ? { tools: request.tools.map((tool) => runtime.createTool(tool)) }
        : {};

      throwIfAborted(signal);

      const modelResponse = await Promise.resolve(sendRequest.call(chatModel, messages, options, cancellationSource.token));

      if (signal.aborted) {
        cancellationSource.cancel();
      }
      throwIfAborted(signal);

      return {
        response: modelResponse,
        dispose: release,
      };
    } catch (error) {
      release();
      throw error;
    }
  };

  const startChat = async (request: GatewayChatRequest, signal: AbortSignal): Promise<GatewayStartedChat> => {
    const startedChat = await sendChatRequest(request, signal);
    return {
      text: startedChat.response.text,
      dispose: startedChat.dispose,
    };
  };

  return {
    async listModels(): Promise<readonly GatewayModel[]> {
      const models = await Promise.resolve(source.selectChatModels({} as TSelector));
      return models.map((model) => mapLanguageModel(model));
    },
    startChat,
    async completeChat(request: GatewayChatRequest, signal: AbortSignal): Promise<GatewayChatCompletion> {
      if (!runtime) {
        throw new Error("Gateway chat runtime dependencies are unavailable.");
      }

      const startedChat = await sendChatRequest(request, signal);
      try {
        const message = await collectResponseParts(startedChat.response, runtime, signal);
        if (!message.toolCalls || message.toolCalls.length === 0) {
          return message.content;
        }

        return { message };
      } finally {
        startedChat.dispose();
      }
    },
  };
}