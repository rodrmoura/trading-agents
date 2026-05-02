import test from "node:test";
import assert from "node:assert/strict";
import http from "node:http";

import { createGatewayController, createVsCodeModelService } from "../dist/index.js";

const MAX_CHAT_BODY_BYTES = 1024 * 1024;

function chatUrl(status) {
  return `http://${status.host}:${status.port}/v1/chat/completions`;
}

function buildChatBody(overrides = {}) {
  return {
    model: "model-alpha",
    messages: [{ role: "user", content: "Hello" }],
    ...overrides,
  };
}

function getBearerToken(gateway) {
  const token = gateway.getToken();
  assert.ok(token);
  return token;
}

async function postChat(gateway, body, contentType = "application/json") {
  const status = gateway.getStatus();
  const token = getBearerToken(gateway);

  return fetch(chatUrl(status), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": contentType,
    },
    body: typeof body === "string" ? body : JSON.stringify(body),
  });
}

async function sendRawChatRequest(gateway, options = {}) {
  const {
    method = "POST",
    path = "/v1/chat/completions",
    headers = {},
    chunks = [],
    ignoreRequestErrors = false,
  } = options;

  const status = gateway.getStatus();

  return new Promise((resolve, reject) => {
    const request = http.request(
      {
        host: status.host,
        port: status.port,
        method,
        path,
        headers,
      },
      (response) => {
        const responseChunks = [];

        response.on("data", (chunk) => {
          responseChunks.push(Buffer.from(chunk));
        });

        response.on("end", () => {
          resolve({
            statusCode: response.statusCode ?? 0,
            bodyText: Buffer.concat(responseChunks).toString("utf8"),
          });
        });
      }
    );

    request.on("error", (error) => {
      if (ignoreRequestErrors) {
        resolve({ statusCode: 0, bodyText: "", error });
        return;
      }

      reject(error);
    });

    for (const chunk of chunks) {
      request.write(chunk);
    }

    request.end();
  });
}

function withTimeout(promise, timeoutMs, message) {
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error(message));
      }, timeoutMs);
    }),
  ]);
}

test("chat requires bearer auth before body parsing or model access", async () => {
  let completeChatCalls = 0;

  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async completeChat() {
        completeChatCalls += 1;
        return "should-not-run";
      },
    },
  });

  await gateway.start();

  try {
    const status = gateway.getStatus();
    const unauthorized = await fetch(chatUrl(status), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: "{not-json",
    });

    assert.equal(unauthorized.status, 401);
    const body = await unauthorized.json();
    assert.equal(body.error.code, "unauthorized");
    assert.equal(completeChatCalls, 0);
  } finally {
    await gateway.stop("command");
  }
});

test("chat enforces and accepts JSON content-type variants", async () => {
  let completeChatCalls = 0;

  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async completeChat() {
        completeChatCalls += 1;
        return "ok";
      },
    },
  });

  await gateway.start();

  try {
    const acceptedTypes = ["application/json", "application/json; charset=utf-8", "APPLICATION/JSON"];

    for (const contentType of acceptedTypes) {
      const response = await postChat(gateway, buildChatBody(), contentType);
      assert.equal(response.status, 200);
      const body = await response.json();
      assert.equal(body.message.content, "ok");
    }

    assert.equal(completeChatCalls, acceptedTypes.length);

    const token = getBearerToken(gateway);

    const missingContentType = await sendRawChatRequest(gateway, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      chunks: [JSON.stringify(buildChatBody())],
    });

    assert.equal(missingContentType.statusCode, 415);
    assert.equal(JSON.parse(missingContentType.bodyText).error.code, "unsupported_media_type");

    const wrongContentType = await postChat(gateway, buildChatBody(), "text/plain");
    assert.equal(wrongContentType.status, 415);
    assert.equal((await wrongContentType.json()).error.code, "unsupported_media_type");

    assert.equal(completeChatCalls, acceptedTypes.length);
  } finally {
    await gateway.stop("command");
  }
});

test("chat rejects malformed JSON and empty body", async () => {
  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async completeChat() {
        return "ok";
      },
    },
  });

  await gateway.start();

  try {
    const malformed = await postChat(gateway, "{\"model\":", "application/json");
    assert.equal(malformed.status, 400);
    assert.equal((await malformed.json()).error.code, "invalid_json");

    const token = getBearerToken(gateway);
    const empty = await sendRawChatRequest(gateway, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      chunks: [],
    });

    assert.equal(empty.statusCode, 400);
    assert.equal(JSON.parse(empty.bodyText).error.code, "invalid_json");
  } finally {
    await gateway.stop("command");
  }
});

test("chat rejects oversized body by Content-Length and by streamed chunks", async () => {
  let completeChatCalls = 0;

  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async completeChat() {
        completeChatCalls += 1;
        return "ok";
      },
    },
  });

  await gateway.start();

  try {
    const oversizedByLength = "x".repeat(MAX_CHAT_BODY_BYTES + 1);
    const byLengthResponse = await postChat(gateway, oversizedByLength, "application/json");
    assert.equal(byLengthResponse.status, 400);
    assert.equal((await byLengthResponse.json()).error.code, "validation_error");

    const token = getBearerToken(gateway);
    const byChunkResponse = await sendRawChatRequest(gateway, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      chunks: ["x".repeat(MAX_CHAT_BODY_BYTES + 512)],
    });

    assert.equal(byChunkResponse.statusCode, 400);
    assert.equal(JSON.parse(byChunkResponse.bodyText).error.code, "validation_error");
    assert.equal(completeChatCalls, 0);
  } finally {
    await gateway.stop("command");
  }
});

test("chat rejects unknown top-level and message fields", async () => {
  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async completeChat() {
        return "ok";
      },
    },
  });

  await gateway.start();

  try {
    const invalidTopLevel = [
      { stream: true },
      { temperature: 0.2 },
      { tools: [] },
      { tool_choice: "auto" },
      { response_format: { type: "json_object" } },
      { extra: 1 },
    ];

    for (const addition of invalidTopLevel) {
      const response = await postChat(gateway, { ...buildChatBody(), ...addition });
      assert.equal(response.status, 400);
      assert.equal((await response.json()).error.code, "validation_error");
    }

    const invalidMessageName = await postChat(gateway, {
      model: "model-alpha",
      messages: [{ role: "user", content: "Hello", name: "alice" }],
    });
    assert.equal(invalidMessageName.status, 400);
    assert.equal((await invalidMessageName.json()).error.code, "validation_error");

    const invalidMessageToolCalls = await postChat(gateway, {
      model: "model-alpha",
      messages: [{ role: "assistant", content: "tool", tool_calls: [] }],
    });
    assert.equal(invalidMessageToolCalls.status, 400);
    assert.equal((await invalidMessageToolCalls.json()).error.code, "validation_error");
  } finally {
    await gateway.stop("command");
  }
});

test("chat validates required and optional native fields", async () => {
  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async completeChat() {
        return "ok";
      },
    },
  });

  await gateway.start();

  try {
    const invalidBodies = [
      { messages: [{ role: "user", content: "Hello" }] },
      { model: "  ", messages: [{ role: "user", content: "Hello" }] },
      { model: "model-alpha" },
      { model: "model-alpha", messages: [] },
      { model: "model-alpha", messages: [{ role: "invalid", content: "Hello" }] },
      { model: "model-alpha", messages: [{ role: "user", content: "" }] },
      { model: "model-alpha", messages: [{ role: "user", content: "  " }] },
      { model: "model-alpha", messages: [{ role: "user", content: "Hello" }], metadata: null },
      { model: "model-alpha", messages: [{ role: "user", content: "Hello" }], metadata: [] },
      { model: "model-alpha", messages: [{ role: "user", content: "Hello" }], requestId: "" },
      { model: "model-alpha", messages: [{ role: "user", content: "Hello" }], requestId: "   " },
    ];

    for (const invalidBody of invalidBodies) {
      const response = await postChat(gateway, invalidBody);
      assert.equal(response.status, 400);
      assert.equal((await response.json()).error.code, "validation_error");
    }
  } finally {
    await gateway.stop("command");
  }
});

test("chat resolves model by exact ID, uses raw model sendRequest, and assembles text response", async () => {
  const selectedMessages = [];
  const selectedTokens = [];
  let selectChatModelsCalls = 0;
  let primarySendRequestCalls = 0;
  let secondarySendRequestCalls = 0;

  const exactModelId = "Opaque Id With Spaces / Do-Not-Normalize";

  const fakeModelService = createVsCodeModelService(
    {
      async selectChatModels(selector) {
        selectChatModelsCalls += 1;
        assert.deepEqual(selector, {});

        return [
          {
            id: "model-never-used",
            name: "Unused",
            vendor: "VendorA",
            family: "FamilyA",
            version: "2026.05",
            async sendRequest() {
              secondarySendRequestCalls += 1;
              throw new Error("Incorrect model selected.");
            },
          },
          {
            id: exactModelId,
            name: "Exact Match",
            vendor: "VendorB",
            family: "FamilyB",
            version: "2026.06",
            async sendRequest(messages, _options, token) {
              primarySendRequestCalls += 1;
              selectedMessages.push(messages);
              selectedTokens.push(token);
              return {
                text: (async function* createTextChunks() {
                  yield "First ";
                  yield "second ";
                  yield "third";
                })(),
              };
            },
          },
        ];
      },
    },
    {
      createUserMessage(content) {
        return { role: "user", content };
      },
      createAssistantMessage(content) {
        return { role: "assistant", content };
      },
      createCancellationSource() {
        const controller = new AbortController();
        return {
          token: controller.signal,
          cancel() {
            controller.abort();
          },
          dispose() {},
        };
      },
    }
  );

  const gateway = createGatewayController({ modelService: fakeModelService });

  await gateway.start();

  try {
    const requestBody = {
      model: exactModelId,
      messages: [
        { role: "system", content: "Top-level instructions." },
        { role: "user", content: "User turn 1" },
        { role: "assistant", content: "Assistant turn 1" },
        { role: "system", content: "Interleaved instructions." },
        { role: "user", content: "User turn 2" },
      ],
      requestId: "client-request-id",
      metadata: { ignoredByPhase1: true },
    };

    const firstResponse = await postChat(gateway, requestBody);
    assert.equal(firstResponse.status, 200);
    const firstBody = await firstResponse.json();

    assert.equal(firstBody.id.startsWith("gwchat_"), true);
    assert.equal(firstBody.model, exactModelId);
    assert.equal(typeof firstBody.created, "string");
    assert.equal(Number.isNaN(Date.parse(firstBody.created)), false);
    assert.deepEqual(firstBody.message, {
      role: "assistant",
      content: "First second third",
    });
    assert.equal(firstBody.finishReason, "stop");
    assert.equal(firstBody.usage, null);
    assert.deepEqual(firstBody.metadata, {});
    assert.equal(Object.prototype.hasOwnProperty.call(firstBody, "requestId"), false);

    const secondResponse = await postChat(gateway, requestBody);
    assert.equal(secondResponse.status, 200);
    const secondBody = await secondResponse.json();

    assert.equal(secondBody.id.startsWith("gwchat_"), true);
    assert.notEqual(secondBody.id, firstBody.id);

    assert.equal(selectChatModelsCalls, 2);
    assert.equal(primarySendRequestCalls, 2);
    assert.equal(secondarySendRequestCalls, 0);

    assert.equal(selectedMessages.length >= 1, true);
    assert.deepEqual(selectedMessages[0], [
      { role: "user", content: "System instructions:\nTop-level instructions." },
      { role: "user", content: "User turn 1" },
      { role: "assistant", content: "Assistant turn 1" },
      { role: "user", content: "System instructions:\nInterleaved instructions." },
      { role: "user", content: "User turn 2" },
    ]);

    assert.equal(selectedTokens.length, 2);
    assert.ok(selectedTokens[0]);

    const missingModel = await postChat(gateway, {
      model: "missing-model-id",
      messages: [{ role: "user", content: "Hello" }],
    });
    assert.equal(missingModel.status, 404);
    assert.equal((await missingModel.json()).error.code, "model_not_found");
  } finally {
    await gateway.stop("command");
  }
});

test("chat maps model errors to sanitized native errors", async () => {
  const secretPrompt = "PROMPT_SECRET_123";
  const secretResponse = "RESPONSE_SECRET_456";

  const cases = [
    {
      name: "NoPermissions",
      thrownError: { code: "NoPermissions", message: `provider details ${secretResponse}` },
      expectedStatus: 403,
      expectedCode: "model_access_denied",
      expectedMessage: "Model access is denied.",
    },
    {
      name: "NotFound",
      thrownError: { code: "NotFound", message: `provider details ${secretResponse}` },
      expectedStatus: 404,
      expectedCode: "model_not_found",
      expectedMessage: "The requested model was not found.",
    },
    {
      name: "Blocked",
      thrownError: { code: "Blocked", message: `provider details ${secretResponse}` },
      expectedStatus: 429,
      expectedCode: "quota_or_rate_limited",
      expectedMessage: "Model access is currently rate limited.",
    },
    {
      name: "cancelled",
      thrownError: { code: "CancelledByClient", message: `provider details ${secretResponse}` },
      expectedStatus: 499,
      expectedCode: "cancelled",
      expectedMessage: "The request was cancelled.",
    },
    {
      name: "unknown",
      thrownError: new Error(`provider failure ${secretResponse}`),
      expectedStatus: 502,
      expectedCode: "unknown_model_error",
      expectedMessage: "The model request failed.",
    },
  ];

  for (const scenario of cases) {
    const gateway = createGatewayController({
      modelService: {
        async listModels() {
          return [];
        },
        async completeChat() {
          throw scenario.thrownError;
        },
      },
    });

    await gateway.start();

    try {
      const response = await postChat(gateway, {
        model: "model-alpha",
        messages: [{ role: "user", content: secretPrompt }],
      });

      assert.equal(response.status, scenario.expectedStatus, scenario.name);
      const body = await response.json();
      assert.equal(body.error.code, scenario.expectedCode);
      assert.equal(body.error.message, scenario.expectedMessage);
      const serialized = JSON.stringify(body);
      assert.equal(serialized.includes(secretPrompt), false);
      assert.equal(serialized.includes(secretResponse), false);
    } finally {
      await gateway.stop("command");
    }
  }
});

test("gateway stop cancels in-flight chat requests", async () => {
  let startedResolver;
  const started = new Promise((resolve) => {
    startedResolver = resolve;
  });

  let abortedResolver;
  const aborted = new Promise((resolve) => {
    abortedResolver = resolve;
  });

  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async completeChat(_request, signal) {
        startedResolver();

        return new Promise((resolve, reject) => {
          const onAbort = () => {
            abortedResolver();
            reject({ code: "CancelledByStop" });
          };

          if (signal.aborted) {
            onAbort();
            return;
          }

          signal.addEventListener("abort", onAbort, { once: true });
        });
      },
    },
  });

  await gateway.start();

  const requestPromise = postChat(gateway, buildChatBody())
    .then(async (response) => ({ status: response.status, body: await response.json() }))
    .catch(() => null);

  await withTimeout(started, 2000, "Chat request did not start.");

  const stopResult = await gateway.stop("command");
  assert.equal(stopResult.outcome, "stopped");

  await withTimeout(aborted, 2000, "In-flight chat request was not aborted during stop.");

  const maybeResponse = await requestPromise;
  if (maybeResponse) {
    assert.ok([499, 502].includes(maybeResponse.status));
  }

  assert.equal(gateway.getStatus().state, "stopped");
  assert.equal(gateway.getToken(), null);
});

test("client disconnect aborts in-flight chat requests on best effort", async () => {
  let startedResolver;
  const started = new Promise((resolve) => {
    startedResolver = resolve;
  });

  let abortedResolver;
  const aborted = new Promise((resolve) => {
    abortedResolver = resolve;
  });

  const gateway = createGatewayController({
    modelService: {
      async listModels() {
        return [];
      },
      async completeChat(_request, signal) {
        startedResolver();

        return new Promise((resolve, reject) => {
          const onAbort = () => {
            abortedResolver();
            reject({ code: "CancelledByDisconnect" });
          };

          if (signal.aborted) {
            onAbort();
            return;
          }

          signal.addEventListener("abort", onAbort, { once: true });
        });
      },
    },
  });

  await gateway.start();

  try {
    const status = gateway.getStatus();
    const token = getBearerToken(gateway);

    await new Promise((resolve, reject) => {
      const body = JSON.stringify(buildChatBody());
      const request = http.request(
        {
          host: status.host,
          port: status.port,
          method: "POST",
          path: "/v1/chat/completions",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
            "Content-Length": Buffer.byteLength(body),
          },
        },
        () => {
          resolve();
        }
      );

      request.on("error", () => {
        resolve();
      });

      request.write(body);
      request.end();

      started.then(() => {
        request.destroy();
      }).catch(reject);
    });

    await withTimeout(aborted, 2000, "In-flight chat request was not aborted on client disconnect.");
  } finally {
    await gateway.stop("command");
  }
});

test("gateway stop during model selection cancels before sendRequest", async () => {
  let selectionStartedResolver;
  const selectionStarted = new Promise((resolve) => {
    selectionStartedResolver = resolve;
  });

  let resolveSelection;
  const pendingSelection = new Promise((resolve) => {
    resolveSelection = resolve;
  });

  let selectionResolved = false;
  const completeSelection = (models) => {
    if (selectionResolved) {
      return;
    }

    selectionResolved = true;
    resolveSelection(models);
  };

  let sendRequestCalls = 0;

  const fakeModelService = createVsCodeModelService(
    {
      selectChatModels(selector) {
        assert.deepEqual(selector, {});
        selectionStartedResolver();
        return pendingSelection;
      },
    },
    {
      createUserMessage(content) {
        return { role: "user", content };
      },
      createAssistantMessage(content) {
        return { role: "assistant", content };
      },
      createCancellationSource() {
        const controller = new AbortController();
        return {
          token: controller.signal,
          cancel() {
            controller.abort();
          },
          dispose() {},
        };
      },
    }
  );

  const gateway = createGatewayController({ modelService: fakeModelService });

  await gateway.start();

  try {
    const token = getBearerToken(gateway);
    const body = JSON.stringify(buildChatBody());

    const responsePromise = sendRawChatRequest(gateway, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(body),
        Connection: "close",
      },
      chunks: [body],
    });

    await withTimeout(selectionStarted, 2000, "Model selection did not start.");

    const stopPromise = gateway.stop("command");

    completeSelection([
      {
        id: "model-alpha",
        name: "Model Alpha",
        async sendRequest() {
          sendRequestCalls += 1;
          throw new Error("sendRequest must not be called after cancellation.");
        },
      },
    ]);

    const [chatResponse, stopResult] = await Promise.all([
      withTimeout(responsePromise, 2000, "Chat response did not complete after cancellation."),
      withTimeout(stopPromise, 2000, "Gateway stop did not complete after cancellation."),
    ]);

    assert.equal(stopResult.outcome, "stopped");
    assert.equal(chatResponse.statusCode, 499);

    const chatBody = JSON.parse(chatResponse.bodyText);
    assert.equal(chatBody.error.code, "cancelled");
    assert.equal(chatBody.error.message, "The request was cancelled.");
    assert.equal(sendRequestCalls, 0);
  } finally {
    completeSelection([]);
    await gateway.stop("command");
  }
});
